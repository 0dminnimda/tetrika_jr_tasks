import pytest
from unittest.mock import patch, mock_open, call
from collections import Counter
import requests

from solution import (
    fetch_page,
    parse_animals_and_next_page_link,
    scrape_and_count_animals,
    save_counts_to_csv,
    main,
    BASE_URL,
    START_URL,
    OUTPUT_FILE,
)

MOCK_HTML_PAGE_1 = """
<html><body>
    <div id="mw-pages">
        <a href="/w/index.php?title=Категория:Животные_по_алфавиту&pagefrom=БРАжник" title="Категория:Животные по алфавиту">Следующая страница</a>
        <div class="mw-category-group"><h3>А</h3><ul><li>А1</li><li>А2</li></ul></div>
        <div class="mw-category-group"><h3>Б</h3><ul><li>Б1</li></ul></div>
    </div>
</body></html>
"""
NEXT_PAGE_1_URL = BASE_URL + "/w/index.php?title=Категория:Животные_по_алфавиту&pagefrom=БРАжник"

MOCK_HTML_PAGE_2 = """
<html><body>
    <div id="mw-pages">
        <!-- No 'Следующая страница' link -->
        <div class="mw-category-group"><h3>Б</h3><ul><li>Б2</li><li>Б3</li></ul></div>
        <div class="mw-category-group"><h3>Г</h3><ul><li>Г1</li></ul></div>
    </div>
</body></html>
"""

MOCK_HTML_INVALID_GROUP_HEADER = """
<html><body>
    <div id="mw-pages">
        <div class="mw-category-group"><h3>Invalid Header</h3><ul><li>Item 1</li></ul></div>
        <div class="mw-category-group"><h3>Д</h3><ul><li>Д1</li></ul></div>
    </div>
</body></html>
"""

@patch("requests.get")
def test_fetch_page_success(mock_get):
    mock_response = mock_get.return_value
    mock_response.status_code = 200
    mock_response.text = "<html>Success</html>"

    content = fetch_page("http://example.com")
    assert content == "<html>Success</html>"
    mock_get.assert_called_once_with("http://example.com", timeout=10)

@patch("requests.get")
def test_fetch_page_http_error(mock_get):
    mock_response = mock_get.return_value
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Error")

    content = fetch_page("http://example.com/notfound")
    assert content is None


def test_parse_animals_modifies_counter_and_returns_link():
    animal_counts = Counter()
    next_link = parse_animals_and_next_page_link(animal_counts, MOCK_HTML_PAGE_1)

    assert animal_counts == Counter({"А": 2, "Б": 1})
    assert next_link == NEXT_PAGE_1_URL

def test_parse_animals_adds_to_existing_counter():
    animal_counts = Counter({"Б": 10, "Ж": 5}) # Pre-existing counts
    next_link = parse_animals_and_next_page_link(animal_counts, MOCK_HTML_PAGE_2)

    # "Б" should be incremented (10 + 2), "Г" should be added
    assert animal_counts == Counter({"Б": 12, "Г": 1, "Ж": 5})
    assert next_link is None

def test_parse_animals_ignores_invalid_group_headers():
    animal_counts = Counter()
    parse_animals_and_next_page_link(animal_counts, MOCK_HTML_INVALID_GROUP_HEADER)
    # Only "Д" should be counted, "Invalid Header" should be skipped
    assert animal_counts == Counter({"Д": 1})


@patch("solution.fetch_page")
def test_scrape_and_count_animals_multiple_pages(mock_fetch_page):
    def side_effect_fetch(url):
        if url == START_URL:
            return MOCK_HTML_PAGE_1
        elif url == NEXT_PAGE_1_URL:
            return MOCK_HTML_PAGE_2
        return None

    mock_fetch_page.side_effect = side_effect_fetch

    total_counts = scrape_and_count_animals(START_URL)

    # "Б" appears on both pages (1 + 2)
    expected_counts = Counter({"А": 2, "Б": 3, "Г": 1})
    assert total_counts == expected_counts

    assert mock_fetch_page.call_count == 2
    mock_fetch_page.assert_any_call(START_URL)
    mock_fetch_page.assert_any_call(NEXT_PAGE_1_URL)

@patch("solution.fetch_page")
def test_scrape_and_count_animals_fetch_fails(mock_fetch_page):
    mock_fetch_page.return_value = None

    total_counts = scrape_and_count_animals(START_URL)
    assert total_counts == Counter()
    mock_fetch_page.assert_called_once_with(START_URL)


@patch("builtins.open", new_callable=mock_open)
def test_save_counts_to_csv_writes_header_and_data(mock_file_open):
    counts = {"Г": 10, "А": 5, "Б": 12}
    filename = "test_output.csv"

    save_counts_to_csv(counts, filename)

    mock_file_open.assert_called_once_with(filename, "w", encoding="utf-8")

    handle = mock_file_open()

    expected_calls = [
        call("Г,10\n"),
        call("А,5\n"),
        call("Б,12\n"),
    ]
    handle.write.assert_has_calls(expected_calls, any_order=False)


@patch("solution.save_counts_to_csv")
@patch("solution.scrape_and_count_animals")
@patch("solution.SORT_COUNTS", False)
def test_main_unsorted(mock_scrape, mock_save):
    # Setup the mock return value for the scraper
    mock_scrape.return_value = {"Г": 10, "А": 5}

    main()

    mock_scrape.assert_called_once_with(START_URL)

    mock_save.assert_called_once_with({"Г": 10, "А": 5}, OUTPUT_FILE)


@patch("solution.save_counts_to_csv")
@patch("solution.scrape_and_count_animals")
@patch("solution.SORT_COUNTS", True)
def test_main_sorted(mock_scrape, mock_save):
    mock_scrape.return_value = {"Г": 10, "А": 5}

    main()

    mock_scrape.assert_called_once_with(START_URL)

    expected_sorted_counts = {"А": 5, "Г": 10}
    mock_save.assert_called_once_with(expected_sorted_counts, OUTPUT_FILE)


if __name__ == "__main__":
    print("Running tests...")
    exit_code = pytest.main(["-v", "-s", __file__])
    print(f"\nTests finished with exit code: {exit_code}")
