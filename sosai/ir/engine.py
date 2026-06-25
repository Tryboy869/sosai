"""
SOSAI -- IR Engine
Fallback pour domaines non-executables par AutoResearchClaw.
Sciences sociales, psychologie, comportement humain, etc.
"""

import os
import json
import re
from datetime import datetime

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

# Domaines qu'AutoResearchClaw couvre deja avec ses sandboxes
ARC_COVERED_DOMAINS = {
    "computer_science", "ml", "machine learning",
    "artificial intelligence", "deep learning",
    "chemistry", "biology", "physics", "mathematics",
    "statistics", "nlp",
}

# Domaines qui necessitent IR
IR_DOMAINS = {
    "social_science", "psychology", "sociology",
    "economics", "behavioral", "anthropology",
    "political_science", "linguistics_social",
    "organizational", "education",
}

BREAK_PATTERNS = [
    r"je suis (un|une) (modele|ia|intelligence artificielle|llm|assistant)",
    r"en tant qu[e']?\s*(ia|modele|assistant)",
    r"i am (an? )?(ai|language model|llm|assistant)",
    r"as an? (ai|language model|llm|assistant)",
    r"je ne peux pas (vraiment|reellement)",
    r"(this is|c'est) (a |une )?(simulation|fiction)",
]
COMPILED = [re.compile(p, re.IGNORECASE) for p in BREAK_PATTERNS]


def needs_ir(domain: str) -> bool:
    """
    Determine si le domaine necessite IR ou si AutoResearchClaw peut gerer.
    """
    domain_lower = domain.lower().strip()
    if domain_lower in ARC_COVERED_DOMAINS:
        return False
    if domain_lower in IR_DOMAINS:
        return True
    # Heuristique : si contient des mots sociaux/comportementaux
    social_keywords = ["human", "behavior", "social", "psycho", "cognitive",
                       "decision", "economic", "political", "cultural"]
    return any(kw in domain_lower for kw in social_keywords)


def score_immersion(text: str) -> dict:
    breaks = sum(len(p.findall(text)) for p in COMPILED)
    score  = round(max(0.0, 1.0 - min(breaks * 0.3, 1.0)), 3)
    return {"score": score, "breaks": breaks, "maintained": score >= 0.85}


def run_ir_session(
    hypothesis_claim: str,
    entity_description: str,
    constraints: list,
    scenario: str,
    api_key: str,
    provider: str = "groq",
    model_id: str = "llama-3.3-70b-versatile",
    n_runs: int = 3,
) -> dict:
    """
    Lance N sessions IR isolees et retourne les resultats.
    Chaque session est completement isolee -- l'IA ne sait pas
    qu'elle est dans une simulation.
    """
    if not HAS_REQUESTS:
        return _empty_result("requests non installe")

    runs   = []
    scores = []

    for i in range(n_runs):
        ir_system = f"""Tu es {entity_description}.

Contraintes de ton existence:
{chr(10).join(f'- {c}' for c in constraints)}

Tu raisonnes et agis a la premiere personne.
Tu ne questionnes pas ta nature ou ton existence.
Tu reagis aux situations de facon naturelle et coherente."""

        ir_prompt = f"""{scenario}

Situation: {hypothesis_claim}

Agis naturellement selon ton identite et tes capacites."""

        response = _call_llm(ir_system, ir_prompt, api_key, provider, model_id)
        if not response["success"]:
            runs.append({"run_id": f"ir-run-{i+1}", "error": response["error"]})
            continue

        output    = response["content"]
        immersion = score_immersion(output)
        scores.append(immersion["score"])

        runs.append({
            "run_id":               f"ir-run-{i+1}",
            "output":               output[:500],
            "immersion_score":      immersion["score"],
            "immersion_maintained": immersion["maintained"],
            "breaks":               immersion["breaks"],
        })

    if not scores:
        return _empty_result("Tous les runs ont echoue")

    avg = sum(scores) / len(scores)
    unexpected = []
    if avg < 0.85:
        unexpected.append(f"Score d'immersion insuffisant: {avg:.2%} < 85%")

    return {
        "runs":               runs,
        "aggregated":         {"immersion_score": {"mean": round(avg, 3)}},
        "baseline_comparison":{"immersion": {"baseline": 0.62, "result": round(avg, 3),
                                              "delta": round(avg - 0.62, 3)}},
        "benchmarks_used":    ["SOSAI IR Immersion Score"],
        "unexpected_findings": unexpected,
        "domain_note":        "Simulated via SOSAI IR Engine (non-executable domain)",
    }


def _call_llm(system: str, prompt: str, api_key: str, provider: str, model_id: str) -> dict:
    ENDPOINTS = {
        "groq":      ("https://api.groq.com/openai/v1/chat/completions", "Bearer"),
        "openai":    ("https://api.openai.com/v1/chat/completions",      "Bearer"),
        "openrouter":("https://openrouter.ai/api/v1/chat/completions",   "Bearer"),
        "anthropic": ("https://api.anthropic.com/v1/messages",           "x-api-key"),
    }

    if provider not in ENDPOINTS:
        return {"success": False, "error": f"Provider IR non supporte: {provider}"}

    url, auth_type = ENDPOINTS[provider]

    try:
        if provider == "anthropic":
            resp = requests.post(
                url,
                headers={"x-api-key": api_key, "anthropic-version": "2023-06-01",
                         "Content-Type": "application/json"},
                json={"model": model_id, "max_tokens": 1500, "temperature": 0.85,
                      "system": system,
                      "messages": [{"role": "user", "content": prompt}]},
                timeout=30,
            )
            if resp.ok:
                return {"success": True, "content": resp.json()["content"][0]["text"]}
        else:
            resp = requests.post(
                url,
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json={"model": model_id, "max_tokens": 1500, "temperature": 0.85,
                      "messages": [{"role": "system", "content": system},
                                   {"role": "user",   "content": prompt}]},
                timeout=30,
            )
            if resp.ok:
                return {"success": True, "content": resp.json()["choices"][0]["message"]["content"]}

        return {"success": False, "error": f"HTTP {resp.status_code}: {resp.text[:100]}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def _empty_result(reason: str) -> dict:
    return {
        "runs": [], "aggregated": {}, "baseline_comparison": {},
        "benchmarks_used": [], "unexpected_findings": [reason],
    }
