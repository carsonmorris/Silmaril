from datetime import datetime, timedelta, timezone
from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from urllib.parse import parse_qs, urlparse
import webbrowser

# World map library for visualizing satellite positions
import folium
import requests
from branca.element import Element

from backend.coordinates import ecef_to_geodetic, teme_to_ecef
from backend.propagator import create_satrec, propagate_satellite
from data.satellite_data import get_satellite_data


# Interval settings for satellite tracking and path visualization
REFRESH_INTERVAL_SECONDS = 3
PATH_HISTORY_HOURS = 24
PATH_SAMPLE_INTERVAL_SECONDS = 10
TRAIL_REDRAW_INTERVAL_SECONDS = 10
MAX_TRAIL_AGE_SECONDS = PATH_HISTORY_HOURS * 60 * 60
INITIAL_VIEW_WINDOW_MINUTES = 10


def get_current_position(satellite, current_time=None):
    # Use the current UTC time for live updates, or a supplied time for path history.
    if current_time is None:
        current_time = datetime.now(timezone.utc)

    # SGP4 returns a TEME position. Convert it through ECEF to map-ready coordinates.
    position_teme, _ = propagate_satellite(satellite, current_time)
    position_ecef = teme_to_ecef(position_teme, current_time)
    latitude, longitude, altitude = ecef_to_geodetic(position_ecef)

    # Keep the result in simple values so it can be used by Folium and sent as JSON.
    return {
        "latitude": latitude,
        "longitude": longitude,
        "altitude": altitude,
        "timestamp": current_time.strftime("%Y-%m-%d %H:%M:%S UTC"),
        "timestamp_unix": current_time.timestamp(),
    }

# Sample the past day at a fixed interval so the user can choose a trail duration.
def get_path_history(satellite, end_time):
    start_time = end_time - timedelta(hours=PATH_HISTORY_HOURS)
    number_of_steps = PATH_HISTORY_HOURS * 60 * 60 // PATH_SAMPLE_INTERVAL_SECONDS
    path = []

    for step in range(number_of_steps + 1):
        sample_time = start_time + timedelta(
            seconds=step * PATH_SAMPLE_INTERVAL_SECONDS
        )
        position = get_current_position(satellite, sample_time)
        path.append([
            position["latitude"],
            position["longitude"],
            position["timestamp_unix"],
        ])

    return path


def create_selection_page(error_message=""):
    # Escape server errors before showing them in the HTML selection page.
    error_html = ""
    if error_message:
        error_html = f'<p class="selection-error" role="alert">{escape(error_message)}</p>'

    return f"""<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Silmaril: Satellite Tracker</title>
    <style>
        :root {{ color-scheme: light; font-family: "Segoe UI", sans-serif; }}
        * {{ box-sizing: border-box; }}
        body {{ display: flex; flex-direction: column; margin: 0; min-height: 100vh; color: #182b32; background: #edf1ef; }}
        header {{ padding: 22px clamp(20px, 6vw, 72px); background: #182b32; color: #fff; }}
        .brand {{ max-width: 100%; margin: 0 auto; text-align: center; }}
        .brand-title {{ color: #fff; font-size: 48px; font-weight: 700; text-decoration: none; }}
        .brand-links {{ display: flex; justify-content: center; gap: 16px; margin-top: 8px; font-size: 13px; }}
        .brand-links a {{ color: #c8ded8; }}
        main {{ display: flex; flex: 1; flex-direction: column; align-items: center; width: 100%; max-width: 780px; margin: 0 auto; padding: clamp(36px, 7vh, 72px) 20px 40px; text-align: center; }}
        .intro {{ max-width: 620px; }}
        .intro h1 {{ margin: 0 0 14px; font-size: 30px; line-height: 1.15; }}
        .intro p {{ margin: 0; font-size: 17px; line-height: 1.6; }}
        .selector {{ display: flex; flex-direction: column; align-items: center; width: 100%; }}
        .selector h2 {{ margin: 0 0 6px; font-size: 24px; }}
        .form-hint {{ margin: 0; color: #66756f; font-size: 12px; line-height: 1.4; }}
        form {{ width: 100%; max-width: 440px; margin: 20px; padding: 24px; background: #fff; border: 1px solid #cbd5d1; border-radius: 6px; text-align: left; }}
        label {{ display: block; margin-bottom: 8px; font-size: 14px; font-weight: 600; }}
        input {{ width: 100%; min-height: 46px; padding: 10px 12px; border: 1px solid #83938e; border-radius: 4px; font: inherit; }}
        button {{ width: 100%; min-height: 46px; margin-top: 14px; border: 0; border-radius: 4px; background: #b83b35; color: #fff; font: 600 15px "Segoe UI", sans-serif; cursor: pointer; }}
        button:hover {{ background: #982f2a; }}
        button:disabled {{ opacity: .7; cursor: wait; }}
        .selection-error {{ width: 100%; max-width: 440px; margin: 0 0 12px; color: #8f221d; }}
        @media (max-width: 480px) {{ .brand-links {{ flex-wrap: wrap; }} form {{ padding: 18px; }} }}
    </style>
</head>
<body>
    <header>
        <div class="brand">
            <a class="brand-title" href="https://github.com/carsonmorris/Silmaril" target="_blank" rel="noopener noreferrer"><i>Silmaril</i>: Satellite Tracker</a>
            <div class="brand-links">
                <a href="https://github.com/carsonmorris/Silmaril" target="_blank" rel="noopener noreferrer">GitHub repository</a>
                <span>Made by Carson Morris - 2026</span>
                <a href="https://creativecommons.org/publicdomain/zero/1.0/" target="_blank" rel="noopener noreferrer">CC0 1.0 Universal</a>
                <span>Orbital data sourced from <a href="https://celestrak.org" target="_blank" rel="noopener noreferrer">CelesTrak</a></span>
            </div>
        </div>
    </header>
    <main>
        <section class="intro" aria-labelledby="about-title">
            <h1 id="about-title">Objects in Orbit</h1>
            <p><i>Silmaril</i> calculates satellite positions from orbital data and brings them to life on a live map. Built to explore orbital mechanics and live visual tracking.</p>
            <p><br>“And thus it came to pass that the Silmarils found their long homes: one in the airs of heaven, and one in the fires of the heart of the world, and one in the deep waters.” ― J.R.R. Tolkien, The Silmarillion</p>
            <p><br>Enter a NORAD catalog number to track a satellite in real-time.<br></p>
        </section>
        <section class="selector" aria-labelledby="selector-title">
            
            <form id="satellite-form" action="/map" method="get">
				<h2 id="selector-title">Choose a satellite to track</h2>
				{error_html}
                <p class="form-hint"><i>Hint: The International Space Station's NORAD catalog number is 25544.</i></p>
                <label for="catalog-number">NORAD catalog number</label>
                <input id="catalog-number" name="catalog_number" type="number" min="1" step="1" value="" required autofocus>
                <button id="submit-button" type="submit">Open live map</button>
            </form>
        </section>
    </main>
    <script>
        document.getElementById("satellite-form").addEventListener("submit", () => {{
            const button = document.getElementById("submit-button");
            button.disabled = true;
            button.textContent = "Loading satellite...";
        }});
    </script>
</body>
</html>"""


def create_map_page(catalog_number, satellite, satellite_name, position, path_history):
    # Start centered on the satellite; the browser fits the recent path after loading.
    location_map = folium.Map(
        location=[position["latitude"], position["longitude"]],
        zoom_start=4,
        tiles=None,
        max_bounds=True,
    )
    # Keep the map to one world and prevent Esri tiles from wrapping horizontally.
    folium.TileLayer(
        tiles="Esri.WorldStreetMap",
        no_wrap=True,
    ).add_to(location_map)

    # Place the marker at the first calculated position; the browser moves it on later updates.
    marker = folium.Marker(
        location=[position["latitude"], position["longitude"]],
        tooltip=satellite_name,
        popup=(
            f"{satellite_name}<br>"
            f"Time: {position['timestamp']}<br>"
            f"Latitude: {position['latitude']:.4f}°<br>"
            f"Longitude: {position['longitude']:.4f}°<br>"
            f"Altitude: {position['altitude']:.1f} km"
        ),
    ).add_to(location_map)
    # JavaScript draws the selected time window and splits it at the date line.
    trail_group = folium.FeatureGroup(name="Satellite trail").add_to(location_map)

    # Give the user a small segmented control for choosing how much trail to show.
    location_map.get_root().html.add_child(Element(
        '<div id="trail-duration-control" role="group" aria-label="Trail duration">'
        '<button type="button" data-trail-hours="1" aria-pressed="true">1h</button>'
        '<button type="button" data-trail-hours="6" aria-pressed="false">6h</button>'
        '<button type="button" data-trail-hours="24" aria-pressed="false">24h</button>'
        '</div>'
        '<style>'
        '#trail-duration-control{position:fixed;top:12px;left:50%;transform:translateX(-50%);'
        'z-index:9999;display:flex;padding:3px;background:#fff;border:1px solid #777;'
        'border-radius:6px;box-shadow:0 1px 4px #5558}'
        '#trail-duration-control button{padding:6px 10px;border:0;background:transparent;'
        'color:#222;font:13px sans-serif;cursor:pointer}'
        '#trail-duration-control button[aria-pressed="true"]{background:#d94841;'
        'color:#fff;border-radius:4px}'
        '@media(max-width:700px){ #trail-duration-control{top:100px;left:12px;transform:none}}'
        '</style>'
    ))

    # Put the project identity on the map and provide a way to choose another satellite.
    location_map.get_root().html.add_child(Element(
        '<aside id="silmaril-brand" aria-label="About Silmaril">'
        '<a id="silmaril-brand-title" href="https://github.com/carsonmorris/Silmaril" '
        'target="_blank" rel="noopener noreferrer">Silmaril: Satellite Tracker</a>'
        '<div id="silmaril-brand-links">'
        '<a href="https://github.com/carsonmorris/Silmaril" target="_blank" '
        'rel="noopener noreferrer">GitHub repository</a>'
        '<a href="/">Change satellite</a>'
        '</div>'
        '<div id="silmaril-author">Made by Carson Morris, 2026</div>'
        '</aside>'
        '<style>'
        '#silmaril-brand{position:fixed;top:12px;left:12px;z-index:9999;'
        'box-sizing:border-box;max-width:calc(100vw - 24px);padding:9px 12px;'
        'background:rgba(255,255,255,.96);border:1px solid #777;border-left:3px solid #d94841;'
        'border-radius:5px;box-shadow:0 1px 4px #5558;font:13px sans-serif;color:#222}'
        '#silmaril-brand-title{display:block;color:#222;font-size:15px;font-weight:700;'
        'text-decoration:none;white-space:nowrap}'
        '#silmaril-brand-links{display:flex;gap:12px;margin-top:5px;font-size:12px}'
        '#silmaril-brand-links a:first-child{color:#315c75}'
        '#silmaril-brand-links a:last-child{color:#555}'
        '#silmaril-author{margin-top:4px;color:#555;font-size:11px}'
        '@media(max-width:700px){ #trail-duration-control{top:105px;left:12px;transform:none}}'
        '</style>'
    ))

    # Show the last successful update time or an error from the position request.
    location_map.get_root().html.add_child(Element(
        '<div id="position-status" style="position: fixed; bottom: 16px; '
        'left: 16px; z-index: 9999; padding: 8px 12px; background: white; '
        'border: 1px solid #777; font: 13px sans-serif;">Starting live updates</div>'
    ))

    # Keep timestamped samples in the browser so duration changes do not need a server request.
    update_script = f"""
    const satelliteName = {json.dumps(satellite_name)};
    const maximumTrailAge = {MAX_TRAIL_AGE_SECONDS};
    const trailRedrawInterval = {TRAIL_REDRAW_INTERVAL_SECONDS};
    const initialViewWindow = {INITIAL_VIEW_WINDOW_MINUTES * 60};
    let trailGroup = null;
    let trailSamples = {json.dumps(path_history, separators=(",", ":"))};
    let firstRetainedSample = 0;
    let selectedTrailHours = 1;
    let lastTrailRedraw = 0;
    let refreshInProgress = false;

    function redrawTrail() {{
        trailGroup.clearLayers();
        const newestSample = trailSamples[trailSamples.length - 1];
        const cutoff = newestSample[2] - selectedTrailHours * 60 * 60;
        const segments = [];
        let segment = [];
        let previousLongitude = null;

        for (let index = firstRetainedSample; index < trailSamples.length; index++) {{
            const sample = trailSamples[index];
            if (sample[2] < cutoff) continue;
            if (previousLongitude !== null && Math.abs(sample[1] - previousLongitude) > 180) {{
                if (segment.length > 0) segments.push(segment);
                segment = [];
            }}
            segment.push([sample[0], sample[1]]);
            previousLongitude = sample[1];
        }}
        if (segment.length > 0) segments.push(segment);

        for (const points of segments) {{
            L.polyline(points, {{ color: "#d94841", weight: 3, opacity: 0.8 }}).addTo(trailGroup);
        }}
        lastTrailRedraw = newestSample[2];
    }}

    async function refreshPosition() {{
        if (refreshInProgress) return;
        refreshInProgress = true;
        const positionStatus = document.getElementById("position-status");
        try {{
            const response = await fetch("/position?catalog_number={catalog_number}", {{ cache: "no-store" }});
            if (!response.ok) {{
                const error = await response.json().catch(() => ({{}}));
                throw new Error(error.error || `HTTP ${{response.status}}`);
            }}
            const position = await response.json();
            const liveMarker = {marker.get_name()};
            liveMarker.setLatLng([position.latitude, position.longitude]);
            const previousSample = trailSamples[trailSamples.length - 1];
            const crossedDateLine = Math.abs(position.longitude - previousSample[1]) > 180;
            trailSamples.push([position.latitude, position.longitude, position.timestamp_unix]);

            const oldestAllowedTime = position.timestamp_unix - maximumTrailAge;
            while (
                firstRetainedSample < trailSamples.length &&
                trailSamples[firstRetainedSample][2] < oldestAllowedTime
            ) {{
                firstRetainedSample++;
            }}
            if (firstRetainedSample > 1024 && firstRetainedSample > trailSamples.length / 2) {{
                trailSamples = trailSamples.slice(firstRetainedSample);
                firstRetainedSample = 0;
            }}

            if (
                crossedDateLine ||
                position.timestamp_unix - lastTrailRedraw >= trailRedrawInterval
            ) {{
                redrawTrail();
            }}
            liveMarker.setPopupContent(
                `${{satelliteName}}<br>Time: ${{position.timestamp}}<br>` +
                `Latitude: ${{position.latitude.toFixed(4)}}°<br>` +
                `Longitude: ${{position.longitude.toFixed(4)}}°<br>` +
                `Altitude: ${{position.altitude.toFixed(1)}} km`
            );
            positionStatus.textContent = `Updated ${{position.timestamp}}`;
        }} catch (error) {{
            console.error("Position update failed:", error);
            positionStatus.textContent = `Position update failed: ${{error.message}}`;
        }} finally {{
            refreshInProgress = false;
        }}
    }}

    window.addEventListener("DOMContentLoaded", () => {{
        trailGroup = {trail_group.get_name()};
        redrawTrail();

        // Fit to the latest part of the path instead of the satellite's full-day orbit.
        const initialViewCutoff = trailSamples[trailSamples.length - 1][2] - initialViewWindow;
        let initialViewPoints = [];
        let previousLongitude = null;
        for (let index = firstRetainedSample; index < trailSamples.length; index++) {{
            const sample = trailSamples[index];
            if (sample[2] < initialViewCutoff) continue;
            if (previousLongitude !== null && Math.abs(sample[1] - previousLongitude) > 180) {{
                initialViewPoints = [];
            }}
            initialViewPoints.push([sample[0], sample[1]]);
            previousLongitude = sample[1];
        }}
        const liveMap = {location_map.get_name()};
        if (initialViewPoints.length > 1) {{
            liveMap.fitBounds(initialViewPoints, {{ padding: [48, 48], maxZoom: 5 }});
        }} else {{
            liveMap.setView(
                [{position["latitude"]}, {position["longitude"]}],
                4
            );
        }}

        document.querySelectorAll("[data-trail-hours]").forEach(button => {{
            button.addEventListener("click", () => {{
                selectedTrailHours = Number(button.dataset.trailHours);
                document.querySelectorAll("[data-trail-hours]").forEach(option => {{
                    option.setAttribute("aria-pressed", String(option === button));
                }});
                redrawTrail();
            }});
        }});
        refreshPosition();
        window.setInterval(refreshPosition, {REFRESH_INTERVAL_SECONDS * 1000});
    }});
    """
    location_map.get_root().script.add_child(Element(update_script))
    return location_map.get_root().render()


def main():
    satellites_by_catalog = {}

    class LiveMapRequestHandler(BaseHTTPRequestHandler):
        def send_content(self, status_code, content_type, content):
            response_body = content.encode("utf-8") if isinstance(content, str) else content
            self.send_response(status_code)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(response_body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(response_body)

        def do_GET(self):
            request = urlparse(self.path)
            query = parse_qs(request.query)

            # Open the branded selection screen before asking CelesTrak for any data.
            if request.path == "/":
                self.send_content(200, "text/html; charset=utf-8", create_selection_page())
            elif request.path == "/map":
                catalog_input = query.get("catalog_number", [""])[0]
                try:
                    catalog_number = int(catalog_input)
                    if catalog_number <= 0:
                        raise ValueError("Enter a positive NORAD catalog number.")
                except ValueError:
                    page = create_selection_page("Enter a positive NORAD catalog number.")
                    self.send_content(400, "text/html; charset=utf-8", page)
                    return

                try:
                    satellite = create_satrec(catalog_number)
                    tracking_time = datetime.now(timezone.utc)
                    position = get_current_position(satellite, tracking_time)
                    path_history = get_path_history(satellite, tracking_time)
                    metadata = get_satellite_data(catalog_number)[0]
                    satellite_name = metadata.get(
                        "OBJECT_NAME",
                        f"Satellite {catalog_number}",
                    )
                    satellites_by_catalog[catalog_number] = satellite
                    map_html = create_map_page(
                        catalog_number,
                        satellite,
                        satellite_name,
                        position,
                        path_history,
                    )
                    self.send_content(200, "text/html; charset=utf-8", map_html)
                except (IndexError, requests.RequestException, ValueError) as error:
                    page = create_selection_page(
                        f"Could not load satellite {catalog_number}: {error}"
                    )
                    self.send_content(400, "text/html; charset=utf-8", page)
            elif request.path == "/position":
                try:
                    catalog_number = int(query.get("catalog_number", [""])[0])
                    satellite = satellites_by_catalog[catalog_number]
                    position = get_current_position(satellite)
                    self.send_content(
                        200,
                        "application/json; charset=utf-8",
                        json.dumps(position),
                    )
                except (KeyError, ValueError) as error:
                    self.send_content(
                        404,
                        "application/json; charset=utf-8",
                        json.dumps({"error": f"Satellite is not loaded: {error}"}),
                    )
                except Exception as error:
                    print(f"Position update failed: {error}", flush=True)
                    self.send_content(
                        500,
                        "application/json; charset=utf-8",
                        json.dumps({"error": str(error)}),
                    )
            else:
                self.send_content(404, "text/plain; charset=utf-8", b"Not found")

        def log_message(self, format, *args):
            # Do not print a standard access log for every three-second poll.
            pass

    # Serve the selection screen and map locally until the user stops the application.
    with ThreadingHTTPServer(("127.0.0.1", 0), LiveMapRequestHandler) as server:
        app_url = f"http://127.0.0.1:{server.server_port}/"
        webbrowser.open_new_tab(app_url)
        print(f"Satellite tracker: {app_url}")
        print("Choose a satellite in the browser. Press Ctrl+C to stop tracking.")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nSatellite tracking stopped.")


if __name__ == "__main__":
    main()
