import pytest

from goodreads_viz.goodreads import GoodreadsUser
from goodreads_viz.url_generator import generate_goodreads_url


@pytest.fixture
def sample_user() -> GoodreadsUser:
    return GoodreadsUser(user_id="12345678", username="test-user")


@pytest.mark.parametrize(
    "page,per_page,expected",
    [
        # First page with default per_page
        (
            1,
            100,
            "https://www.goodreads.com/review/list/12345678-test-user?utf8=%E2%9C%93&shelf=read&per_page=100&title=test-user",
        ),
        # Second page with default per_page
        (
            2,
            100,
            "https://www.goodreads.com/review/list/12345678-test-user?utf8=%E2%9C%93&shelf=read&per_page=100&page=2",
        ),
        # First page with custom per_page
        (
            1,
            50,
            "https://www.goodreads.com/review/list/12345678-test-user?utf8=%E2%9C%93&shelf=read&per_page=50&title=test-user",
        ),
    ],
)
def test_url_generation(sample_user: GoodreadsUser, page: int, per_page: int, expected: str) -> None:
    result = generate_goodreads_url(sample_user, page=page, per_page=per_page)
    assert result == expected


def test_invalid_page_number(sample_user: GoodreadsUser) -> None:
    with pytest.raises(ValueError):
        generate_goodreads_url(sample_user, page=0)
