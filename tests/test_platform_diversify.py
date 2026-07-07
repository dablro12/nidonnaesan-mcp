"""플랫폼 다양화 테스트."""

from campaign_filters import diversify_by_platform


def _c(pid: str, platform: str, applicants: int) -> dict:
    return {
        "id": pid,
        "platform": platform,
        "applicants": applicants,
        "recruitCount": 10,
        "dDay": 3,
    }


def test_diversify_limits_single_platform() -> None:
    campaigns = [
        _c("r1", "레뷰", 1000),
        _c("r2", "레뷰", 900),
        _c("r3", "레뷰", 800),
        _c("g1", "강남맛집", 700),
        _c("d1", "디너의여왕", 600),
    ]
    picked = diversify_by_platform(campaigns, top_n=5, max_per_platform=2)
    platforms = [c["platform"] for c in picked]
    assert platforms.count("레뷰") <= 2
    assert len(set(platforms)) >= 3
