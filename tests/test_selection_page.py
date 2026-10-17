from main import create_selection_page


def test_selection_page_displays_search_results_and_removes_custom_number_entry():
    page = create_selection_page(
        satellites=[
            {"catalog_number": 43013, "object_name": "NOAA 20", "object_type": "PAY"},
            {"catalog_number": 25544, "object_name": "ISS & ZARYA", "object_type": "PAY"},
            {"catalog_number": 20580, "object_name": "HST", "object_type": "PAY"},
            {"catalog_number": 48274, "object_name": "TIANGONG", "object_type": "PAY"},
            {"catalog_number": 54234, "object_name": "NOAA 21", "object_type": "PAY"},
            {"catalog_number": 25994, "object_name": "TERRA", "object_type": "PAY"},
            {"catalog_number": 49260, "object_name": "LANDSAT 9", "object_type": "PAY"},
            {"catalog_number": 50032, "object_name": "TEST DEB", "object_type": "DEB"},
            {"catalog_number": 1234, "object_name": "Test object", "object_type": "PAY"},
        ],
        selected_catalog_number=25544,
        search_query="test",
        page_size=1,
    )

    assert '<strong>9</strong>' in page
    assert "objects with confirmed CelesTrak GP records in the local cache" in page
    assert 'name="q" type="search"' in page
    assert "Showing 1–1 of 2 matches for “test”." in page
    assert "Page 1 of 2" in page
    assert 'href="/?q=test&amp;page=2"' in page
    assert "Next 1 →" in page
    assert '<input type="radio" name="catalog_selection"' in page
    assert "<select" not in page
    assert "<legend>Notable satellites</legend>" not in page
    debris_group = page.index("<legend>Space Debris</legend>")
    assert "International Space Station (NORAD 25544)" not in page
    assert "NOAA-21 Weather Satellite (NORAD 54234)" not in page
    assert page.count('type="radio" name="catalog_selection"') == 1
    assert 'value="50032"' in page[debris_group:]
    assert 'value="1234"' not in page
    assert 'name="catalog_number"' not in page

    next_page = create_selection_page(
        satellites=[
            {"catalog_number": 50032, "object_name": "TEST DEB", "object_type": "DEB"},
            {"catalog_number": 1234, "object_name": "Test object", "object_type": "PAY"},
        ],
        search_query="test",
        search_page=2,
        page_size=1,
    )
    assert "Showing 2–2 of 2 matches" in next_page
    assert "<legend>Matching objects</legend>" in next_page
    assert 'value="1234"' in next_page
    assert "Test object" in next_page
    assert 'href="/?q=test&amp;page=1"' in next_page


def test_selection_page_shows_featured_objects_without_listing_full_catalog():
    page = create_selection_page(
        satellites=[
            {
                "catalog_number": 1234,
                "object_name": "Test object",
                "object_type": "PAY",
            }
        ]
    )

    assert "<legend>Notable satellites</legend>" not in page
    assert "<legend>Matching objects</legend>" not in page
    assert 'value="1234"' not in page
    assert "Search by name or NORAD number" in page
    assert '<nav class="catalog-view-nav" aria-label="Choose catalog view">' in page
    assert 'href="/?featured=1" aria-current="page">Notable satellites</a>' in page
    assert 'href="/?browse=1">Full catalog <span>1</span></a>' in page
    assert "Positions are calculated for the current time" in page
    assert "cache is older than three hours" in page


def test_selection_page_browses_all_catalog_entries_in_pages():
    satellites = [
        {
            "catalog_number": number,
            "object_name": f"Object {number}",
            "object_type": "PAY",
        }
        for number in range(1000, 1061)
    ]
    page = create_selection_page(satellites=satellites, browse_all=True)

    assert "Showing 1–50 of 61 trackable objects." in page
    assert "Page 1 of 2" in page
    assert 'href="/?browse=1&amp;page=2"' in page
    assert "Next 50 →" in page
    assert 'name="catalog_browse_all" value="1"' in page
    assert 'aria-current="page">Full catalog' in page
    assert 'href="/?featured=1">Notable satellites</a>' in page
    assert page.count('type="radio" name="catalog_selection"') == 50
    assert 'value="1000"' in page
    assert 'value="1049"' in page
    assert 'value="1050"' not in page

    next_page = create_selection_page(
        satellites=satellites,
        search_page=2,
        browse_all=True,
    )
    assert "Showing 51–61 of 61 trackable objects." in next_page
    assert 'href="/?browse=1&amp;page=1"' in next_page
    assert 'value="1050"' in next_page
    assert 'value="1049"' not in next_page


def test_selection_page_search_matches_numbers_and_custom_notable_names():
    page = create_selection_page(
        satellites=[
            {"catalog_number": 25544, "object_name": "ISS & ZARYA", "object_type": "PAY"},
            {"catalog_number": 1234, "object_name": "Test object", "object_type": "PAY"},
        ],
        search_query="International Space Station",
    )

    assert "1 matches for “International Space Station”" in page
    assert "International Space Station" in page
    assert "NORAD 25544" in page
    assert 'value="1234"' not in page


def test_intro_copy_and_quote_share_the_orbital_artwork_column():
    page = create_selection_page()

    intro_copy = page.index('<p class="intro-copy">')
    orbital_art = page.index('<div class="orbital-visual"')
    quote = page.index('<div class="silmaril-note">')
    main_end = page.index("</main>")

    assert page.index('<div class="orbital-side">') < intro_copy < orbital_art < quote
    assert quote < main_end
    assert "Dedicated to my brother, Connor" in page
