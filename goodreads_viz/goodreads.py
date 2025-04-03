from dataclasses import dataclass


@dataclass
class GoodreadsUser:
    """
    A class representing a Goodreads user.
    """

    user_id: str
    username: str
