"""Shared schema helpers for tasks, gold answers, and model predictions."""

from __future__ import annotations

import re
from typing import Any

VALID_VERDICTS = ("CONFIRMED", "SUSPICIOUS", "NOT_FOUND", "UNVERIFIED")

# Fields the grader compares when present on the gold answer.
COMPARE_FIELDS = (
    "claimed_amount_ngn",
    "actual_amount_ngn",
    "reference",
    "beneficiary_name",
    "beneficiary_bank",
    "payer_name",
    "status_on_receipt",
)

# Pidgin / informal naira amount patterns used in Nigerian commerce.
# "2k5" and "2.5k" both mean 2,500; "10k" means 10,000; "2m" means 2,000,000.
_K_SPLIT = re.compile(r"^(\d+(?:\.\d+)?)\s*k\s*(\d+)$", re.I)
_K_SIMPLE = re.compile(r"^(\d+(?:\.\d+)?)\s*k$", re.I)
_M_SIMPLE = re.compile(r"^(\d+(?:\.\d+)?)\s*m$", re.I)
_NUMBER = re.compile(r"[,\s]")


def normalize_name(value: Any) -> str:
    """Uppercase, strip punctuation noise, collapse whitespace."""
    if value is None:
        return ""
    text = str(value).upper()
    text = re.sub(r"[.`']", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def parse_amount_ngn(value: Any) -> int | None:
    """Parse an amount in naira from a number or a Nigerian informal string.

    Returns an integer naira amount, or None if it cannot be parsed.
    Kobo are not used in this eval: every gold amount is a whole naira figure.
    """
    if value is None:
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return int(round(value))
    text = str(value).strip().lower()
    text = text.replace("₦", "").replace("ngn", "").replace(",", "").strip()
    if not text:
        return None
    match = _K_SPLIT.match(text)
    if match:
        thousands = float(match.group(1))
        tail = match.group(2)
        # "2k5" -> 2,500; "2k50" -> 2,500; "10k5" -> 10,500
        if len(tail) == 1:
            return int(thousands * 1000 + int(tail) * 100)
        return int(thousands * 1000 + int(tail))
    match = _K_SIMPLE.match(text)
    if match:
        return int(round(float(match.group(1)) * 1000))
    match = _M_SIMPLE.match(text)
    if match:
        return int(round(float(match.group(1)) * 1_000_000))
    text = _NUMBER.sub("", text)
    try:
        return int(round(float(text)))
    except ValueError:
        return None


def field_equal(name: str, predicted: Any, gold: Any) -> bool:
    if name.endswith("_ngn") or name.endswith("_amount") or "amount" in name:
        left = parse_amount_ngn(predicted)
        right = parse_amount_ngn(gold)
        if left is None or right is None:
            return False
        return left == right
    if name in {"beneficiary_name", "payer_name", "beneficiary_bank"}:
        return normalize_name(predicted) == normalize_name(gold)
    if name in {"reference", "status_on_receipt"}:
        return str(predicted or "").strip().upper() == str(gold or "").strip().upper()
    return str(predicted).strip() == str(gold).strip()
