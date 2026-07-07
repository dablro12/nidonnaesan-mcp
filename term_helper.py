import re


TERM_DB = {
    "IP": "Intellectual Property(지식재산권)의 약자입니다. 특허, 상표, 디자인, 저작권 등 독창적 자산을 포함합니다.",
    "IITP": "정보통신기획평가원(IITP)입니다. ICT 연구개발 과제 기획/평가/관리를 수행하는 기관입니다.",
    "RFP": "Request For Proposal(제안요청서)입니다. 발주처가 요구사항을 제시하는 문서입니다.",
    "POC": "Proof of Concept(개념검증)입니다. 아이디어/기술의 실현 가능성을 확인하는 단계입니다.",
}


def extract_hard_terms(text: str) -> list[str]:
    tokens = re.findall(r"\b[A-Z]{2,6}\b", text)
    unique = []
    for token in tokens:
        if token not in unique:
            unique.append(token)
    return unique


def explain_terms(text: str) -> list[dict]:
    terms = extract_hard_terms(text)
    results = []
    for term in terms:
        if term in TERM_DB:
            results.append({"term": term, "explanation": TERM_DB[term]})
    return results
