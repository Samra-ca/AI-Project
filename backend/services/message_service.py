import hashlib
import re
from dataclasses import dataclass

_BLOCK_PATTERN = re.compile(
    r"Sender:\s*(?P<sender>.+?)\s*\n"
    r"Date:\s*(?P<date>.+?)\s*\n"
    r"Message:\s*(?P<message>.+?)(?=\n\s*\n|\Z)",
    re.IGNORECASE | re.DOTALL,
)


@dataclass
class RawMessage:
    sender: str
    date: str
    text: str
    raw_block: str
    fingerprint: str


def _fingerprint(sender: str, date: str, text: str) -> str:
    key = f"{sender.strip().lower()}|{date.strip().lower()}|{text.strip().lower()}"
    return hashlib.sha256(key.encode("utf-8")).hexdigest()


def parse_messages(file_text: str) -> list[RawMessage]:
    """Parses a .txt message pack into individual messages, preserving each
    message's original text exactly as provided. Tolerant to blank-line
    separated blocks with "Sender:", "Date:", and "Message:" labels
    (case-insensitive), since the judging pack's exact formatting is
    unseen.
    """
    messages: list[RawMessage] = []
    for match in _BLOCK_PATTERN.finditer(file_text):
        sender = match.group("sender").strip()
        date = match.group("date").strip()
        text = match.group("message").strip()
        messages.append(
            RawMessage(
                sender=sender,
                date=date,
                text=text,
                raw_block=match.group(0).strip(),
                fingerprint=_fingerprint(sender, date, text),
            )
        )
    return messages


def read_message_file(path: str) -> list[RawMessage]:
    with open(path, "r", encoding="utf-8") as f:
        return parse_messages(f.read())


def diff_new_messages(
    messages: list[RawMessage], known_fingerprints: set[str]
) -> list[RawMessage]:
    """Returns only the messages not already present in known_fingerprints,
    so a re-run or additional-message upload only processes what's new."""
    return [m for m in messages if m.fingerprint not in known_fingerprints]
