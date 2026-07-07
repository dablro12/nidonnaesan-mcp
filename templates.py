from tone_profiles import get_profile


def build_reply_variants(
    instruction: str, recipient_role: str, context: str = "", include_plan: bool = True
) -> dict:
    profile = get_profile(recipient_role)
    base_plan = (
        "요청 주신 내용을 확인 후 오늘 중 1차 정리본을 공유드리고, "
        "세부 진행 계획은 점검받아 반영하겠습니다."
        if include_plan
        else "요청 주신 내용 확인 후 말씀하신 방향으로 진행하겠습니다."
    )
    if context:
        base_plan = f"{context} {base_plan}"

    short = f"{profile.greeting} {instruction} 확인했습니다. {profile.closing}"
    standard = f"{profile.greeting} {instruction} 확인했습니다. {base_plan} {profile.closing}"
    formal = (
        f"{profile.greeting} 말씀 주신 {instruction} 내용을 확인했습니다. "
        f"우선순위에 맞춰 일정과 산출물을 정리하여 공유드리고, "
        f"추가 지시사항이 있다면 반영해 진행하겠습니다. {profile.closing}"
    )
    return {"short": short, "standard": standard, "formal": formal}


def build_followup_message(topic: str, role: str) -> str:
    profile = get_profile(role)
    return (
        f"{profile.greeting} 이전에 전달드린 {topic} 건 관련하여 "
        "확인 가능하실지 조심스럽게 문의드립니다. "
        f"{profile.closing}"
    )


def build_confirmation_note(items: list[str], role: str) -> str:
    profile = get_profile(role)
    joined = " / ".join(items)
    return (
        f"{profile.greeting} 확인차 정리드립니다. {joined}. "
        "제가 이해한 내용이 맞는지 확인 부탁드리며, 맞다면 해당 방향으로 진행하겠습니다. "
        f"{profile.closing}"
    )


def build_recovery_apology(missed_task: str, recovery_plan: str, role: str) -> str:
    profile = get_profile(role)
    return (
        f"{profile.greeting} {missed_task} 전달이 지연된 점 죄송합니다. "
        f"{recovery_plan} 일정으로 만회하겠습니다. "
        "재발하지 않도록 사전 점검 후 공유드리겠습니다. "
        f"{profile.closing}"
    )
