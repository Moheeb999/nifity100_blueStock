import re


def normalize_ticker(value):
    """
    Normalize stock ticker symbols.
    Examples:
    ' tcs ' -> TCS
    'hdfcbank.ns' -> HDFCBANK
    """
    if value is None:
        return None

    ticker = str(value).strip().upper()
    ticker = ticker.replace(".NS", "")
    ticker = ticker.replace(".BO", "")

    return ticker


def normalize_year(value):
    """
    Convert year formats to integer year.
    Examples:
    Mar-24 -> 2024
    2023 -> 2023
    """
    if value is None:
        return None

    value = str(value).strip()

    if value.isdigit() and len(value) == 4:
        return int(value)

    match = re.search(r'(\d{2})$', value)

    if match:
        yr = int(match.group(1))
        return 2000 + yr if yr < 50 else 1900 + yr

    return None