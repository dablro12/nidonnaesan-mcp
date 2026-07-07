from dataclasses import dataclass


@dataclass(frozen=True)
class RiskFinding:
    category: str
    reason: str
    suggestion: str


RISK_PATTERNS = [
    (
        "무례/가벼움",
        ["ㅇㅋ", "ok", "네넵", "ㄱㄱ", "ㅎㅎ", "ㅋ"],
        "공손 표현으로 교체하세요. 예: '확인했습니다. 말씀하신 방향으로 진행하겠습니다.'",
    ),
    (
        "모호한 일정",
        ["빨리", "가능하면", "조만간", "곧"],
        "구체 날짜/시간을 명시하세요. 예: '내일 15시까지 초안 전달드리겠습니다.'",
    ),
    (
        "책임회피/소극",
        ["어쩔 수", "힘들 것 같", "아마", "잘 모르겠"],
        "대안/계획을 함께 제시하세요. 예: '현재 어려움이 있어, 3일 뒤까지 전달드리면 어떨지 문의드립니다.'",
    ),
    (
        "근거 없는 확답",
        ["무조건", "문제없습니다", "확실히 됩니다"],
        "조건과 근거를 함께 표현하세요. 예: '확인 후 오늘 18시까지 가능 여부를 회신드리겠습니다.'",
    ),
]


def analyze_risk(message: str) -> dict:
    findings: list[RiskFinding] = []
    lowered = message.lower()
    for category, patterns, suggestion in RISK_PATTERNS:
        if any(p in lowered for p in patterns):
            findings.append(
                RiskFinding(
                    category=category,
                    reason=f"'{category}'에 해당할 수 있는 표현이 포함되어 있습니다.",
                    suggestion=suggestion,
                )
            )

    score = max(0, 100 - (len(findings) * 20))
    return {
        "risk_score": score,
        "summary": "낮음" if score >= 80 else "중간" if score >= 60 else "높음",
        "findings": [f.__dict__ for f in findings],
    }
