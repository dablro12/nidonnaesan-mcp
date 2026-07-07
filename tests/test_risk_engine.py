from risk_engine import analyze_risk


def test_risk_score_drops_when_risky_tokens_exist() -> None:
    result = analyze_risk("ㅇㅋ 조만간 보낼게요")
    assert result["risk_score"] < 100
    assert len(result["findings"]) >= 1


def test_risk_score_full_for_clean_message() -> None:
    result = analyze_risk("확인했습니다. 내일 15시까지 공유드리겠습니다.")
    assert result["risk_score"] == 100
