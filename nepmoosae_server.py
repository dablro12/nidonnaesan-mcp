from mcp.server.fastmcp import FastMCP

from risk_engine import analyze_risk
from term_helper import explain_terms
from templates import (
    build_confirmation_note,
    build_followup_message,
    build_recovery_apology,
    build_reply_variants,
)
from tool_descriptions import TOOL_DESCRIPTIONS

mcp = FastMCP("yes-parrot-mcp")


@mcp.tool(description=TOOL_DESCRIPTIONS["analyze_and_rewrite_reply"])
def analyze_and_rewrite_reply(
    incoming_message: str,
    user_intent: str,
    recipient_role: str = "PROFESSOR",
    context: str = "",
) -> dict:
    risk = analyze_risk(user_intent)
    variants = build_reply_variants(
        instruction=incoming_message,
        recipient_role=recipient_role,
        context=context,
    )
    return {
        "analysis_target": incoming_message,
        "risk_analysis": risk,
        "reply_variants": variants,
    }


@mcp.tool(description=TOOL_DESCRIPTIONS["explain_message_terms"])
def explain_message_terms(message_text: str) -> dict:
    return {"terms": explain_terms(message_text)}


@mcp.tool(description=TOOL_DESCRIPTIONS["generate_polite_followup"])
def generate_polite_followup(topic: str, recipient_role: str = "PROFESSOR") -> dict:
    return {"message": build_followup_message(topic, recipient_role)}


@mcp.tool(description=TOOL_DESCRIPTIONS["generate_confirmation_message"])
def generate_confirmation_message(items: list[str], recipient_role: str = "MANAGER") -> dict:
    return {"message": build_confirmation_note(items, recipient_role)}


@mcp.tool(description=TOOL_DESCRIPTIONS["generate_recovery_apology"])
def generate_recovery_apology(
    missed_task: str, recovery_plan: str, recipient_role: str = "PROFESSOR"
) -> dict:
    return {"message": build_recovery_apology(missed_task, recovery_plan, recipient_role)}


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
