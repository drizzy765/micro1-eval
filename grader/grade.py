"""Deterministic grader.

A prediction passes only when:
  1. the verdict string matches gold exactly, and
  2. every gold field in COMPARE_FIELDS matches (normalized), and
  3. the model did not emit a false CONFIRMED.

A false CONFIRMED (model says CONFIRMED when gold is anything else) is
catastrophic: score is 0.0 even if every extracted field is correct.
That is the failure mode that loses Nigerian sellers real money.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .schema import COMPARE_FIELDS, VALID_VERDICTS, field_equal


@dataclass
class GradeResult:
    passed: bool
    score: float
    verdict_match: bool
    fields_matched: int
    fields_total: int
    field_details: dict[str, bool] = field(default_factory=dict)
    catastrophic_false_confirmed: bool = False
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "passed": self.passed,
            "score": self.score,
            "verdict_match": self.verdict_match,
            "fields_matched": self.fields_matched,
            "fields_total": self.fields_total,
            "field_details": self.field_details,
            "catastrophic_false_confirmed": self.catastrophic_false_confirmed,
            "errors": self.errors,
        }


def _as_answer(raw: Any) -> dict[str, Any]:
    if raw is None:
        return {}
    if not isinstance(raw, dict):
        return {"verdict": str(raw)}
    # Accept either a flat answer or {"verdict", "fields": {...}}.
    if "fields" in raw and isinstance(raw["fields"], dict):
        merged = dict(raw["fields"])
        if "verdict" in raw:
            merged["verdict"] = raw["verdict"]
        return merged
    return dict(raw)


def grade_prediction(prediction: Any, gold: Any) -> GradeResult:
    """Grade one model (or baseline) answer against a task's gold answer."""
    pred = _as_answer(prediction)
    gold_ans = _as_answer(gold)
    errors: list[str] = []

    gold_verdict = str(gold_ans.get("verdict") or "").strip().upper()
    pred_verdict = str(pred.get("verdict") or "").strip().upper()

    if gold_verdict not in VALID_VERDICTS:
        errors.append(f"gold verdict {gold_verdict!r} is not in {VALID_VERDICTS}")
    if pred_verdict not in VALID_VERDICTS:
        errors.append(f"predicted verdict {pred_verdict!r} is not in {VALID_VERDICTS}")

    false_confirmed = pred_verdict == "CONFIRMED" and gold_verdict != "CONFIRMED"
    verdict_match = pred_verdict == gold_verdict and gold_verdict in VALID_VERDICTS

    details: dict[str, bool] = {}
    matched = 0
    total = 0
    for name in COMPARE_FIELDS:
        if name not in gold_ans:
            continue
        total += 1
        ok = field_equal(name, pred.get(name), gold_ans.get(name))
        details[name] = ok
        if ok:
            matched += 1

    if false_confirmed:
        errors.append("catastrophic_false_confirmed")
        return GradeResult(
            passed=False,
            score=0.0,
            verdict_match=verdict_match,
            fields_matched=matched,
            fields_total=total,
            field_details=details,
            catastrophic_false_confirmed=True,
            errors=errors,
        )

    field_fraction = 1.0 if total == 0 else matched / total
    score = (0.6 * (1.0 if verdict_match else 0.0)) + (0.4 * field_fraction)
    passed = verdict_match and matched == total and not errors
    return GradeResult(
        passed=passed,
        score=round(score, 4),
        verdict_match=verdict_match,
        fields_matched=matched,
        fields_total=total,
        field_details=details,
        catastrophic_false_confirmed=False,
        errors=errors,
    )
