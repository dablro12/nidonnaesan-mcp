from experience_value import (
    competition_label,
    experience_value_label,
    parse_benefit_value,
)


def test_parse_benefit_won():
    assert parse_benefit_value("제공 50,000원 상당") == 50000


def test_experience_value_high():
    assert experience_value_label(50000, "블로그") == "높음"


def test_competition_label():
    label, level = competition_label(120, 30)
    assert "4.0:1" in label
    assert level == "치열"
