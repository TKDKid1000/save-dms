from datetime import datetime, timedelta
from typing import TypeVar

T = TypeVar("T")


def group(array: list[T], size: int) -> list[list[T]]:
    """
    Groups the elements of an array into sublists of a specified size.

    Args:
    1. array: A list of elements to be grouped.
    2. size: The desired size of each sublist.

    Returns:
    A list of sublists, where each sublist contains at most `size` elements.
    """
    return [array[i : i + size] for i in range(0, len(array), size)]


def split_conversations(
    messages: list[dict], conversation_duration: timedelta
) -> list[list[dict]]:
    """
    Splits a message download into individual conversations of certain time durations.

    Args:
    1. messages: A list of messages obtained from Save DMs.
    2. conversation_duration: The maximum time between messages before a new conversation begins.

    Returns:
    A list of sublists, where each sublist is a single conversation.
    """
    conversations: list[list[dict]] = []

    last_timestamp: datetime = datetime(
        2000, 1, 1
    )  # No Discord messages can exist before this, so it's a good starting date.
    for message in messages:
        timestamp = datetime.fromisoformat(message["timestamp"])
        if timestamp.timestamp() < (last_timestamp + conversation_duration).timestamp():
            conversations[-1].append(message)
        else:
            conversations.append([message])
        last_timestamp = timestamp

    return conversations
