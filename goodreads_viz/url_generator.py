from urllib.parse import urlencode

from goodreads_viz.goodreads import GoodreadsUser


def generate_goodreads_url(user: GoodreadsUser, page: int, per_page: int = 100) -> str:
    """
    Generate a Goodreads URL for a user's read books list.

    Parameters:
    -----------
        user: GoodreadsUser object containing user_id and username
        page: Page number (1-based)
        per_page: Number of items per page (default 100)

    Returns:
    -------
        str: Generated Goodreads URL

    Raises:
        ValueError: If page number is less than 1
    """
    if page < 1:
        raise ValueError("Page number must be at least 1")

    base_url = "https://www.goodreads.com/review/list"

    params = {"utf8": "✓", "shelf": "read", "per_page": per_page}

    if page == 1:
        params["title"] = user.username
    else:
        params["page"] = page

    url = f"{base_url}/{user.user_id}-{user.username}"
    query_string = urlencode(params, safe="✓")

    return f"{url}?{query_string}"
