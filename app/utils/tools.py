from datetime import timedelta

from aiogram import html


def splitting_lists(list_: list, count: int) -> list:
    """
        Example:
            splitting_lists([1, 2, 3], 2) -> [[1, 2], [3]]
    """

    return [list_[i:i + count] for i in range(0, len(list_), count)]


def text_(*args) -> str:
    """
        Example:
            text_("Test", "string") -> "Test\\\\nstring"
    """

    return "\n".join(args)


def get_mention(user_id: int, full_name: str):
    return f"<a href='tg://user?id={user_id}'>{html.quote(full_name)}</a>"


def string_timedelta(td: timedelta):
    return ' '.join([
        pattern.format(value) for value, pattern in zip(
            (td.days, td.seconds // 3600, (td.seconds // 60) % 60, td.seconds % 60),
            ('{} д.', '{} час.', '{} мин.', '{} сек.'),
        )
        if value
    ])
