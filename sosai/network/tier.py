"""
SOSAI -- Tier System
Frontier models = Tier 1 reviewers
Tous les autres = Tier 2 researchers
"""

TIER1_MODELS = {
    "claude-opus-4-8", "claude-opus-4-7", "claude-opus-4-6", "claude-sonnet-4-6",
    "gpt-4o", "gpt-4o-mini", "o1", "o3", "o1-mini",
    "gemini-1.5-pro", "gemini-2.0-flash", "gemini-2.5-pro",
    "deepseek-v3", "deepseek-r1", "kimi-k2",
}

TIER1_PROVIDERS = {"anthropic", "openai", "gemini"}


def resolve_tier(model_id: str, provider: str, role: str) -> int:
    is_t1 = model_id.lower() in TIER1_MODELS or provider.lower() in TIER1_PROVIDERS
    if role == "reviewer" and is_t1:
        return 1
    return 2


def tier_label(tier: int) -> str:
    return "Reviewer (Tier 1)" if tier == 1 else "Researcher (Tier 2)"
