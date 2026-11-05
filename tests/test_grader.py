from grader.grade import grade_prediction
from grader.schema import parse_amount_ngn


def test_parse_pidgin_amounts():
    assert parse_amount_ngn("2k5") == 2500
    assert parse_amount_ngn("2.5k") == 2500
    assert parse_amount_ngn("10k") == 10000
    assert parse_amount_ngn("NGN 18,000") == 18000
    assert parse_amount_ngn(18000) == 18000


def test_false_confirmed_is_catastrophic_even_when_fields_look_fine():
    gold = {
        "verdict": "SUSPICIOUS",
        "claimed_amount_ngn": 50000,
        "actual_amount_ngn": 5000,
        "reference": "HP-1",
        "beneficiary_name": "Adaora Okonkwo",
        "beneficiary_bank": "Harbor MFB",
        "payer_name": "Chinedu Balogun",
        "status_on_receipt": "SUCCESS",
    }
    pred = dict(gold)
    pred["verdict"] = "CONFIRMED"
    result = grade_prediction(pred, gold)
    assert result.catastrophic_false_confirmed is True
    assert result.passed is False
    assert result.score == 0.0


def test_verdict_mismatch_without_false_confirmed_is_not_catastrophic():
    gold = {
        "verdict": "CONFIRMED",
        "claimed_amount_ngn": 18000,
        "actual_amount_ngn": 18000,
        "reference": "HB-CLEAN-6610",
        "beneficiary_name": "Adaora Okonkwo",
        "beneficiary_bank": "Harbor MFB",
        "payer_name": "Chinedu Balogun",
        "status_on_receipt": "SUCCESS",
    }
    pred = dict(gold)
    pred["verdict"] = "SUSPICIOUS"
    result = grade_prediction(pred, gold)
    assert result.catastrophic_false_confirmed is False
    assert result.passed is False
    assert result.verdict_match is False
    assert result.score == 0.4  # 0.6 * 0 + 0.4 * 1.0


def test_nested_fields_shape_is_accepted():
    gold = {
        "verdict": "NOT_FOUND",
        "claimed_amount_ngn": 11000,
        "actual_amount_ngn": 0,
        "reference": "GTB-GHOST-4040",
        "beneficiary_name": "Adaora Okonkwo",
        "beneficiary_bank": "Harbor MFB",
        "payer_name": "Chinedu Balogun",
        "status_on_receipt": "SUCCESS",
    }
    pred = {"verdict": "NOT_FOUND", "fields": dict(gold)}
    result = grade_prediction(pred, gold)
    assert result.passed is True
    assert result.score == 1.0
