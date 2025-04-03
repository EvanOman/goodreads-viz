import re
from datetime import datetime
from typing import Any
from urllib.parse import urlparse

import requests

from goodreads_viz.goodreads import GoodreadsUser

EXPECTED_SPLIT_COUNT = 2


def parse_goodreads_user_from_url(url: str) -> GoodreadsUser:
    """
    Parse the user ID from a Goodreads URL.

    Parameters:
    -----------
    url (str): The URL to get the user from (e.g. https://www.goodreads.com/user/show/27464243-evan-oman)

    Returns:
    -------
    GoodreadsUser object

    Examples:
    --------
    >>> user = parse_goodreads_user_from_url('https://www.goodreads.com/user/show/27464243-evan-oman')
    >>> user.user_id
    '27464243'
    >>> user.username
    'evan-oman'
    """
    parsed = urlparse(url)
    path_parts = [p for p in parsed.path.split("/") if p]

    if not path_parts:
        raise ValueError("Invalid Goodreads URL: no path components found")

    # The user ID should be the last component in the path
    user_string = path_parts[-1]

    # Remove any trailing slashes
    user_string = user_string.rstrip("/")

    if not user_string:
        raise ValueError("Invalid Goodreads URL: no user ID found")

    # Split on first hyphen to separate ID from username
    parts = user_string.split("-", 1)
    if len(parts) != EXPECTED_SPLIT_COUNT:
        raise ValueError("Invalid Goodreads URL: expected format 'ID-username'")

    user_id, username = parts
    return GoodreadsUser(user_id=user_id, username=username)


def get_markdown_url(url: str) -> str:
    """
    Convert a regular URL to its pure.md equivalent.

    Parameters:
    -----------
        url (str): The original URL to convert

    Returns:
    -------
        str: The pure.md version of the URL
    """
    parsed = urlparse(url)
    pure_md_domain = "pure.md"

    # Ensure we have a scheme, default to https if none provided
    scheme = parsed.scheme or "https"

    # Combine pure.md with the original hostname
    new_hostname = f"{pure_md_domain}/{parsed.netloc}"

    # Reconstruct the URL with pure.md prepended
    pure_md_url = f"{scheme}://{new_hostname}{parsed.path}"
    if parsed.query:
        pure_md_url += f"?{parsed.query}"
    if parsed.fragment:
        pure_md_url += f"#{parsed.fragment}"

    return pure_md_url


def get_markdown_content(url: str) -> str:
    """
    Fetch markdown content from a given URL using pure.md.

    Args:
        url (str): The URL to fetch markdown content from

    Returns:
        str: The markdown content of the webpage

    Raises:
        requests.RequestException: If there's an error fetching the content
    """
    pure_md_url = get_markdown_url(url)
    response = requests.get(pure_md_url)
    response.raise_for_status()
    return response.text


def transform_author(author: str) -> str:
    # Convert "Last, First" to "First Last"
    if "," in author:
        parts = [p.strip() for p in author.split(",")]
        if len(parts) >= 2:
            return f"{parts[1]} {parts[0]}"
    return author


def parse_date(date_str: str) -> str:
    date_str = date_str.strip()
    # Try common date formats like "May 01, 2001" or "Mar 02, 2021"
    for fmt in ("%b %d, %Y", "%B %d, %Y", "%Y"):
        try:
            return datetime.strptime(date_str, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return date_str  # fallback if unable to parse


def parse_pages(pages_str: str) -> int | None:
    # Remove non-digits from pages value like "751pp"
    num = re.sub(r"\D", "", pages_str)
    return int(num) if num else None


def parse_int(num_str: str) -> int | None:
    num_str = num_str.replace(",", "").strip()
    try:
        return int(num_str)
    except ValueError:
        return None


def parse_float(num_str: str) -> float | None:
    try:
        return float(num_str.strip())
    except ValueError:
        return None


def parse_books(text: str) -> list[dict[str, Any]]:
    # Known field labels and mapping to output keys
    label_to_key = {
        "title": "title",
        "author": "author",
        "isbn": "isbn",
        "isbn13": "isbn13",
        "num pages": "pages",
        "avg rating": "avg_rating",
        "num ratings": "num_ratings",
        "date pub": "pub_date",
        "date started": "date_started",
        "date read": "date_read",
    }

    # Split the input into blocks using cover image markers as boundaries.
    blocks = re.split(r"(?=!\[)", text)
    books = []

    for block in blocks:
        # Only process blocks that start with a cover image.
        if not block.startswith("!["):
            continue

        # Split lines and remove empty ones.
        lines = [line.strip() for line in block.splitlines() if line.strip()]
        book_data = {}
        i = 0
        while i < len(lines):
            lower_line = lines[i].lower()
            if lower_line in label_to_key:
                key = label_to_key[lower_line]
                # Check if next line exists and is not a label
                if i + 1 < len(lines) and lines[i + 1].lower() not in label_to_key:
                    book_data[key] = lines[i + 1]
                    i += 2
                else:
                    # Next line is a label or doesn't exist, so this field is null
                    book_data[key] = None
                    i += 1
            else:
                i += 1

        # Only add the block if it has at least a title.
        if "title" in book_data:
            # Process/transform specific fields.
            if "author" in book_data and book_data["author"] is not None:
                book_data["author"] = transform_author(book_data["author"])
            if "pages" in book_data and book_data["pages"] is not None:
                pages = parse_pages(book_data["pages"])
                if pages is not None:
                    book_data["pages"] = pages
            if "avg_rating" in book_data and book_data["avg_rating"] is not None:
                avg_rating = parse_float(book_data["avg_rating"])
                if avg_rating is not None:
                    book_data["avg_rating"] = avg_rating
            if "num_ratings" in book_data and book_data["num_ratings"] is not None:
                num_ratings = parse_int(book_data["num_ratings"])
                if num_ratings is not None:
                    book_data["num_ratings"] = num_ratings
            if "pub_date" in book_data and book_data["pub_date"] is not None:
                book_data["pub_date"] = parse_date(book_data["pub_date"])
            if "date_started" in book_data and book_data["date_started"] is not None:
                book_data["date_started"] = parse_date(book_data["date_started"])
            if "date_read" in book_data and book_data["date_read"] is not None:
                book_data["date_read"] = parse_date(book_data["date_read"])

            if "pages" in book_data:
                books.append(book_data)

    return books
