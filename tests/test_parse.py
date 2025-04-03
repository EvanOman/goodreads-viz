import json

import pytest

from goodreads_viz.goodreads import GoodreadsUser
from goodreads_viz.parse import parse_books, parse_goodreads_user_from_url


@pytest.mark.parametrize(
    "url",
    [
        "https://www.goodreads.com/user/show/27464243-evan-oman",  # basic case
        "https://www.goodreads.com/user/show/27464243-evan-oman/",  # trailing slash
        "www.goodreads.com/user/show/27464243-evan-oman",  # no scheme
        "https://goodreads.com/user/show/27464243-evan-oman",  # different domain
        "https://www.goodreads.com/user/show/27464243-evan-oman?ref=nav_profile",  # query params
    ],
)
def test_parse_goodreads_user_from_url_valid(url: str) -> None:
    """Test that valid Goodreads URLs are parsed correctly."""
    user = parse_goodreads_user_from_url(url)
    assert isinstance(user, GoodreadsUser)
    assert user.user_id == "27464243"
    assert user.username == "evan-oman"


@pytest.mark.parametrize(
    "url,expected_error",
    [
        ("https://www.goodreads.com", "no path components found"),
        ("https://www.goodreads.com/", "no path components found"),
        ("https://www.goodreads.com/user/show/invalid", "expected format 'ID-username'"),
    ],
)
def test_parse_goodreads_user_from_url_invalid(url: str, expected_error: str) -> None:
    """Test that invalid Goodreads URLs raise appropriate errors."""
    with pytest.raises(ValueError, match=expected_error):
        parse_goodreads_user_from_url(url)


def test_parse_books():
    with open("tests/test_data/sample_page.txt", encoding="utf-8") as f:
        content = f.read()

    books = parse_books(content)

    with open("tests/test_data/expected_result.json", encoding="utf-8") as f:
        expected_books = json.load(f)

    assert len(books) == len(expected_books)

    for book, expected_book in zip(books, expected_books, strict=True):
        assert book["title"] == expected_book["title"]
        assert book["author"] == expected_book["author"]
        assert book["pages"] == expected_book["pages"]
        assert book["avg_rating"] == expected_book["avg_rating"]
        assert book["num_ratings"] == expected_book["num_ratings"]
        assert book["pub_date"] == expected_book["pub_date"]
        assert book["date_started"] == expected_book["date_started"]
        assert book["date_read"] == expected_book["date_read"]
