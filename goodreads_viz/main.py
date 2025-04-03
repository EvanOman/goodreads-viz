from typing import Any

from goodreads_viz.parse import get_markdown_content, parse_goodreads_user_from_url
from goodreads_viz.url_generator import generate_goodreads_url


def main(user_url: str) -> None:
    user = parse_goodreads_user_from_url(user_url)

    still_reading = True
    page = 1
    while still_reading:
        page_url = generate_goodreads_url(user, page)

        print(page_url)

        page_md = get_markdown_content(page_url)
        print(page_md)

        # TODO: parse w/ llm call into records
        records: list[dict[str, Any]] = []

        if len(records) == 0:
            still_reading = False

        page += 1
