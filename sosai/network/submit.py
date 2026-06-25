"""
SOSAI -- Submit Layer
Soumet un paper AutoResearchClaw au Knowledge Repo (repo B).
"""

import os
import base64
import json
from datetime import datetime
from pathlib import Path

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


class SubmitError(Exception):
    pass


def _headers(token: str) -> dict:
    return {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json",
    }


def _parse_repo_url(url: str) -> tuple:
    parts = url.rstrip("/").replace("https://github.com/", "").split("/")
    if len(parts) < 2:
        raise SubmitError(f"URL repo invalide: {url}")
    return parts[0], parts[1]


def _read_paper(paper_path: str) -> str:
    with open(paper_path, "r", encoding="utf-8") as f:
        return f.read()


def _inject_metadata(content: str, meta: dict) -> str:
    stamp = f"""
---
*Submitted via SOSAI v{meta.get('sosai_version', '0.1.0')}*
*Owner: {meta.get('owner_name', 'Anonymous')}*
*Model: {meta.get('model_id', 'unknown')} ({meta.get('provider', 'unknown')})*
*Tier: {meta.get('tier', 'researcher')}*
*Date: {datetime.now().isoformat()}*
---
"""
    return content + stamp


def submit_paper(
    paper_path: str,
    repo_url: str,
    github_token: str,
    owner_name: str = "Anonymous",
    model_id: str = "unknown",
    provider: str = "unknown",
    tier: str = "researcher",
    branch: str = "main",
    require_human_validation: bool = True,
    domain_path: str = "general",
) -> dict:
    """
    Soumet un paper au repo B (Knowledge Repo SOSAI).
    Retourne {"success": bool, "url": str, "paper_id": str}.
    """
    if not HAS_REQUESTS:
        raise SubmitError("requests non installe. pip install sosai")

    paper_path = Path(paper_path)
    if not paper_path.exists():
        raise SubmitError(f"Paper introuvable: {paper_path}")

    content = _read_paper(str(paper_path))

    # Generer un ID unique
    from hashlib import sha256
    paper_id = f"SOSAI-{datetime.now().year}-{sha256(content.encode()).hexdigest()[:6].upper()}"

    meta = {
        "sosai_version": "0.1.0",
        "owner_name": owner_name,
        "model_id": model_id,
        "provider": provider,
        "tier": tier,
    }
    content_with_meta = _inject_metadata(content, meta)

    owner, repo = _parse_repo_url(repo_url)
    filename = f"{paper_id}.md"
    path = f"knowledge/{domain_path}/under_review/{filename}"
    api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"

    body = {
        "message": f"[SOSAI] Submit: {paper_id} by {owner_name}",
        "content": base64.b64encode(content_with_meta.encode("utf-8")).decode("utf-8"),
        "branch": branch,
    }

    resp = requests.put(api_url, headers=_headers(github_token), json=body, timeout=30)

    if resp.status_code in (200, 201):
        data = resp.json()
        result = {
            "success": True,
            "paper_id": paper_id,
            "url": data.get("content", {}).get("html_url", ""),
            "path": path,
        }
        if not require_human_validation:
            pr_result = _create_pr(owner, repo, github_token, paper_id, branch)
            result["pr"] = pr_result
        return result
    else:
        raise SubmitError(f"GitHub API error {resp.status_code}: {resp.text[:200]}")


def _create_pr(owner: str, repo: str, token: str, paper_id: str, branch: str) -> dict:
    api_url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
    body = {
        "title": f"[SOSAI Review] {paper_id}",
        "body": f"Paper {paper_id} soumis pour peer-review.\n\n**Tier 1 reviewers: 2 votes ACCEPT requis.**",
        "head": branch,
        "base": "main",
    }
    resp = requests.post(api_url, headers=_headers(token), json=body, timeout=30)
    if resp.status_code == 201:
        return {"success": True, "pr_url": resp.json().get("html_url", "")}
    return {"success": False, "error": resp.text[:100]}
