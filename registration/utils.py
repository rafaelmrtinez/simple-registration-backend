"""Central utility for ID derivation and reversal."""
import base64


def encode_id(pk: int) -> str:
    """Encode a raw ID into a derived format: U-<YYYY><Base64RawId>."""
    import datetime
    year = datetime.datetime.now().year
    raw = f"{year}:{pk}"
    encoded = base64.urlsafe_b64encode(raw.encode()).decode()
    return f"U-{encoded}"


def decode_id(derived: str) -> int:
    """Decode a derived ID back to the raw integer PK."""
    if not derived.startswith("U-"):
        raise ValueError("Invalid derived ID format")
    encoded = derived[2:]
    raw = base64.urlsafe_b64decode(encoded.encode()).decode()
    _, pk = raw.split(":", 1)
    return int(pk)
