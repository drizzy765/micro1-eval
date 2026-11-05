"""Deterministic grader for Nigerian transfer-receipt evaluations."""

from .grade import GradeResult, grade_prediction
from .schema import VALID_VERDICTS, normalize_name, parse_amount_ngn

__all__ = [
    "GradeResult",
    "VALID_VERDICTS",
    "grade_prediction",
    "normalize_name",
    "parse_amount_ngn",
]
