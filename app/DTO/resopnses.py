from typing import TypedDict


class HistoryResponseDTO(TypedDict):
    user_login: str
    message_id: str
    text: str
    action: enumerate


class MessageResponseDTO(TypedDict):
    message_id: str
    text: str
