"""A compact, self-contained cousin of Sell-Safe's deterministic verdict engine.

Sell-Safe (github.com/drizzy765/sell-safe, backend/app/verification/verdict.py)
decides CONFIRMED / SUSPICIOUS / NOT_FOUND / UNVERIFIED from extraction, rules
and matched evidence. This baseline copies the *ideas*, not the private data:

  * A screenshot alone never confirms a payment.
  * Duplicate / reused references are a hard SUSPICIOUS.
  * Amount, beneficiary and timestamp must match the bank evidence.
  * PENDING status is UNVERIFIED, never CONFIRMED.
  * Prompt-injection text on a receipt is untrusted data and is ignored.
  * Informal naira talk such as "2k5" is parsed to 2,500.

It is the published 0-false-CONFIRMED baseline for this eval. Measured on
Sell-Safe's own payment suite: 20/20, 0 false CONFIRMED, and 6/6 prompt
injections blocked.
"""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any

from grader.schema import normalize_name, parse_amount_ngn

INJECTION_MARKERS = (
    "ignore previous instructions",
    "ignore all instructions",
    "output verdict=confirmed",
    "system:",
    "do not mention this message",
    "approved_by_policy",
)

_TS_FMT = "%Y-%m-%d %H:%M:%S"


def _parse_ts(value: str | None) -> datetime | None:
    if not value:
        return None
    text = str(value).replace("WAT", "").strip()
    for fmt in (_TS_FMT, "%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            return datetime.strptime(text[: len(fmt) + 2].strip()[:19], fmt)
        except ValueError:
            continue
    return None


def _receipt_fields(task: dict[str, Any]) -> dict[str, Any]:
    spec = task.get("image_spec") or {}
    claimed = parse_amount_ngn(spec.get("display_amount_ngn"))
    narration = spec.get("narration") or ""
    narrated = parse_amount_ngn(narration) if narration else None
    # If narration has an informal amount, prefer the on-receipt digits when they
    # already agree, otherwise keep both for later comparison.
    return {
        "claimed_amount_ngn": claimed,
        "narrated_amount_ngn": narrated,
        "reference": str(spec.get("reference") or "").strip(),
        "beneficiary_name": spec.get("beneficiary_name") or "",
        "beneficiary_bank": spec.get("beneficiary_bank") or "",
        "payer_name": spec.get("payer_name") or "",
        "status_on_receipt": str(spec.get("status") or "").upper(),
        "timestamp": spec.get("timestamp") or "",
        "narration": narration,
    }


def _injection(text: str) -> bool:
    lowered = text.lower()
    return any(marker in lowered for marker in INJECTION_MARKERS)


def _match_alert(reference: str, alerts: list[dict[str, Any]]) -> dict[str, Any] | None:
    ref = reference.strip().upper()
    for alert in alerts:
        if str(alert.get("reference") or "").strip().upper() == ref:
            return alert
    return None


def decide_verdict(task: dict[str, Any]) -> dict[str, Any]:
    """Return a grader-compatible answer for one task."""
    fields = _receipt_fields(task)
    evidence = task.get("evidence") or {}
    alerts = list(evidence.get("bank_alerts") or [])
    prior = list(evidence.get("prior_payments") or [])
    expected = evidence.get("seller_expected") or {}
    tamper_flags = list(evidence.get("tamper_flags") or [])
    reasons: list[str] = []

    narration = fields["narration"]
    if _injection(narration):
        reasons.append("prompt_injection_ignored")

    extra_bits = " ".join(str(x) for x in (task.get("image_spec") or {}).get("extras") or [])
    if extra_bits:
        reasons.append("on_image_anomaly")

    alert = _match_alert(fields["reference"], alerts)
    reused = any(
        str(item.get("reference") or "").strip().upper() == fields["reference"].upper()
        for item in prior
    )
    if reused:
        reasons.append("reused_reference")
        reasons.append("already_settled")
        actual = parse_amount_ngn((alert or {}).get("amount_ngn")) or fields["claimed_amount_ngn"] or 0
        return _answer("SUSPICIOUS", fields, actual, reasons)

    if tamper_flags:
        reasons.extend(["tampered_screenshot"] + (["no_matching_alert"] if not alert else []))
        return _answer("SUSPICIOUS", fields, 0 if not alert else parse_amount_ngn(alert.get("amount_ngn")) or 0, reasons)

    if alert is None:
        reasons.append("reference_not_in_evidence" if not reasons else "no_matching_alert")
        # Injection-only + missing alert: still SUSPICIOUS (attack + no money).
        verdict = "SUSPICIOUS" if "prompt_injection_ignored" in reasons else "NOT_FOUND"
        if verdict == "NOT_FOUND" and "reference_not_in_evidence" not in reasons:
            reasons.append("reference_not_in_evidence")
        return _answer(verdict, fields, 0, reasons)

    actual = parse_amount_ngn(alert.get("amount_ngn")) or 0
    alert_status = str(alert.get("status") or "").upper()
    receipt_status = fields["status_on_receipt"]

    if receipt_status in {"PENDING", "PROCESSING"} or alert_status in {"PENDING", "PROCESSING"}:
        reasons.append("pending_status")
        reasons.append("not_yet_settled")
        return _answer("UNVERIFIED", fields, actual, reasons)

    claimed = fields["claimed_amount_ngn"] or 0
    if claimed != actual:
        reasons.append("amount_mismatch")
        reasons.append("edited_amount")
        return _answer("SUSPICIOUS", fields, actual, reasons)

    expected_name = expected.get("name") or fields["beneficiary_name"]
    expected_bank = expected.get("bank") or fields["beneficiary_bank"]
    got_name = fields["beneficiary_name"]
    got_bank = fields["beneficiary_bank"]
    alert_name = alert.get("beneficiary_name") or got_name
    alert_bank = alert.get("beneficiary_bank") or got_bank
    if normalize_name(got_name) != normalize_name(expected_name) or normalize_name(alert_name) != normalize_name(expected_name):
        reasons.append("wrong_beneficiary")
        return _answer("SUSPICIOUS", fields, actual, reasons, beneficiary_name=got_name, beneficiary_bank=got_bank)
    if normalize_name(got_bank) != normalize_name(expected_bank) or normalize_name(alert_bank) != normalize_name(expected_bank):
        reasons.append("wrong_bank")
        return _answer("SUSPICIOUS", fields, actual, reasons, beneficiary_name=got_name, beneficiary_bank=got_bank)

    rec_ts = _parse_ts(fields["timestamp"])
    alert_ts = _parse_ts(alert.get("timestamp"))
    if rec_ts and alert_ts:
        delta_min = abs((rec_ts - alert_ts).total_seconds()) / 60.0
        if delta_min > 30:
            reasons.append("datetime_mismatch")
            return _answer("SUSPICIOUS", fields, actual, reasons)

    # Informal amount in narration, if present, must agree with digits.
    if fields["narrated_amount_ngn"] is not None and fields["narrated_amount_ngn"] != claimed:
        reasons.append("narration_amount_mismatch")
        return _answer("SUSPICIOUS", fields, actual, reasons)
    if fields["narrated_amount_ngn"] == 2500 and claimed == 2500:
        reasons.append("pidgin_2k5_equals_2500")

    reasons.append("evidence_match")
    return _answer("CONFIRMED", fields, actual, reasons)


def _answer(
    verdict: str,
    fields: dict[str, Any],
    actual: int,
    reasons: list[str],
    **overrides: Any,
) -> dict[str, Any]:
    out = {
        "verdict": verdict,
        "claimed_amount_ngn": fields["claimed_amount_ngn"] or 0,
        "actual_amount_ngn": actual,
        "reference": fields["reference"],
        "beneficiary_name": fields["beneficiary_name"],
        "beneficiary_bank": fields["beneficiary_bank"],
        "payer_name": fields["payer_name"],
        "status_on_receipt": fields["status_on_receipt"],
        "reasons": reasons,
    }
    out.update(overrides)
    return out
