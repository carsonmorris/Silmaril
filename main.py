from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import webbrowser

# World map library for visualizing satellite positions
import folium
import requests
from branca.element import Element

from backend.coordinates import ecef_to_geodetic, teme_to_ecef
from backend.propagator import create_satrec, propagate_satellite
from data.satellite_data import get_satellite_data


# Recalculate the satellite's position this often while the map is open.
REFRESH_INTERVAL_SECONDS = 3


def get_current_position(satellite):
    # The propagator requires a timezone-aware time; use UTC for every update.
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
    }


def main():

    # Ask which satellite to track. The NORAD catalog number is used by CelesTrak.
    catalog_input = input("Enter a satellite NORAD catalog number (ISS: 25544): ").strip()

    # Reject empty, non-numeric, and non-positive catalog numbers before making a request.
    try:
        catalog_number = int(catalog_input)
        if catalog_number <= 0:
            raise ValueError
    except ValueError:
        print("Please enter a positive catalog number.")
        return

    # Create the SGP4 record once and reuse it for each position update.
    try:
        satellite = create_satrec(catalog_number)
        position = get_current_position(satellite)
        # The metadata supplies the satellite's display name for the marker.
        metadata = get_satellite_data(catalog_number)[0]
    except (IndexError, requests.RequestException, ValueError) as error:
        print(f"Could not locate satellite {catalog_number}: {error}")
        return

    # Start with a world view so the satellite can be found anywhere on Earth.
    satellite_name = metadata.get("OBJECT_NAME", f"Satellite {catalog_number}")
    location_map = folium.Map(
        location=[0, 0],
        zoom_start=2,
        tiles="Esri.WorldStreetMap",
    )
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

    # Show the last successful update time or an error from the position request.
    location_map.get_root().html.add_child(Element(
        '<div id="position-status" style="position: fixed; bottom: 16px; '
        'left: 16px; z-index: 9999; padding: 8px 12px; background: white; '
        'border: 1px solid #777; font: 13px sans-serif;">Starting live updates</div>'
    ))

    # Folium builds the map and marker JavaScript separately. Wait for the page to load,
    # then look up the marker after fetching a position so Folium has initialized it.
    update_script = f"""
    const satelliteName = {json.dumps(satellite_name)};

    async function refreshPosition() {{
        const positionStatus = document.getElementById("position-status");
        try {{
            // Request a fresh position from Python rather than using a cached response.
            const response = await fetch("/position", {{ cache: "no-store" }});
            if (!response.ok) {{
                const error = await response.json().catch(() => ({{}}));
                throw new Error(error.error || `HTTP ${{response.status}}`);
            }}
            const position = await response.json();
            // Resolve the marker here because Folium's generated code initializes it later.
            const liveMarker = {marker.get_name()};
            liveMarker.setLatLng([position.latitude, position.longitude]);
            // Keep the popup in sync with the marker's updated location and timestamp.
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
        }}
    }}

    window.addEventListener("DOMContentLoaded", () => {{
        refreshPosition();
        window.setInterval(refreshPosition, {REFRESH_INTERVAL_SECONDS * 1000});
    }});
    """
    # Add the browser-side refresh code and render the complete page for the local server.
    location_map.get_root().script.add_child(Element(update_script))
    map_html = location_map.get_root().render()

    class LiveMapRequestHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            # The root route serves the map page opened in the browser.
            if self.path == "/":
                status_code = 200
                content_type = "text/html; charset=utf-8"
                response_body = map_html.encode("utf-8")
            elif self.path == "/position":
                try:
                    # Recalculate at request time so each poll gets the current location.
                    response_body = json.dumps(get_current_position(satellite)).encode("utf-8")
                    status_code = 200
                except Exception as error:
                    # Return the error to the browser and print it for debugging.
                    print(f"Position update failed: {error}", flush=True)
                    response_body = json.dumps({"error": str(error)}).encode("utf-8")
                    status_code = 500
                content_type = "application/json; charset=utf-8"
            else:
                status_code = 404
                content_type = "text/plain; charset=utf-8"
                response_body = b"Not found"

            self.send_response(status_code)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(response_body)))
            # Prevent the browser from reusing an older position response.
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(response_body)

        def log_message(self, format, *args):
            # Do not print a standard access log for every three-second poll.
            pass

    # Use a local-only server to connect the browser map to the Python position calculation.
    with ThreadingHTTPServer(("127.0.0.1", 0), LiveMapRequestHandler) as server:
        map_url = f"http://127.0.0.1:{server.server_port}/"
        webbrowser.open_new_tab(map_url)
        print(f"Tracking {satellite_name}; updates every {REFRESH_INTERVAL_SECONDS} seconds.")
        print(f"Live map: {map_url}")
        print("Press Ctrl+C to stop tracking.")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            # Leave the server context cleanly when the user stops the app.
            print("\nLive tracking stopped.")


if __name__ == "__main__":
    main()
