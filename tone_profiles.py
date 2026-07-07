from dataclasses import dataclass


@dataclass(frozen=True)
class ToneProfile:
    role: str
    greeting: str
    closing: str
    style_hint: str
    avoid_hint: str


PROFILES = {
    "PROFESSOR": ToneProfile(
        role="PROFESSOR",
        greeting="교수님 안녕하세요.",
        closing="확인 부탁드립니다. 감사합니다.",
        style_hint="높은 공손도, 완곡한 요청, 일정/액션 명확화",
        avoid_hint="이모지, 단답, 명령형 어투",
    ),
    "SENIOR": ToneProfile(
        role="SENIOR",
        greeting="안녕하세요 선배님.",
        closing="확인 부탁드립니다. 감사합니다.",
        style_hint="공손+간결, 실행 계획 중심",
        avoid_hint="핑계성 표현, 불필요한 장문",
    ),
    "MANAGER": ToneProfile(
        role="MANAGER",
        greeting="안녕하세요.",
        closing="진행 후 공유드리겠습니다. 감사합니다.",
        style_hint="결론 먼저, 일정/산출물 중심",
        avoid_hint="모호한 기한, 근거 없는 확답",
    ),
    "CLIENT": ToneProfile(
        role="CLIENT",
        greeting="안녕하세요.",
        closing="검토 부탁드립니다. 감사합니다.",
        style_hint="비즈니스 중립 톤, 책임 범위 명확화",
        avoid_hint="내부 용어 남발, 감정 표현",
    ),
}


def get_profile(role: str) -> ToneProfile:
    return PROFILES.get(role.upper(), PROFILES["MANAGER"])
