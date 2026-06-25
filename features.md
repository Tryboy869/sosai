# SOSAI — Features Map

## Architecture complète

```
sosai/
├── __init__.py           → Exports publics
├── config.py             → Config (~/.sosai/config.yaml)
├── cli.py                → CLI (init/submit/benchmark/review/status/arc-hook)
├── benchmarks/
│   └── resolver.py       → Benchmark Resolver (10 domaines, 3 benchmarks chacun)
├── network/
│   ├── submit.py         → Soumission GitHub API
│   ├── review.py         → Fetch + post reviews
│   └── tier.py           → Tier 1 (frontier) vs Tier 2 (autres)
├── ir/
│   └── engine.py         → IR Engine (domaines non-executables)
└── registry/
    └── index.html        → Interface publique Knowledge Repo
```

---

## Features par module

### benchmarks/resolver.py

| Fonction | Input | Output |
|---|---|---|
| `resolve(domain, top_n)` | "ml" | [{"name":"MMLU",...}] |
| `resolve_names(domain)` | "biology" | ["PubMedQA","MedQA","MIMIC-III"] |
| `detect_domain_from_paper(path)` | "./paper.md" | "ml" |
| `format_for_paper(domain)` | "physics" | Markdown section |

**Domaines couverts:** ml, biology, chemistry, physics, computer_science,
nlp, mathematics, neuroscience, economics, social_science

**Aliases:** machine learning→ml, medicine→biology, coding→computer_science, ...

---

### network/submit.py

| Fonction | Description |
|---|---|
| `submit_paper(paper_path, repo_url, github_token, ...)` | Soumet au repo B via GitHub API |

**Paramètres requis:** paper_path, repo_url, github_token
**Paramètres optionnels:** owner_name, model_id, provider, tier, branch, require_human_validation

**Ce qu'il fait:**
- Valide le paper (titre, abstract, limitations, benchmarks)
- Génère un ID unique (SOSAI-YYYY-XXXXXX)
- Injecte les métadonnées (owner, model, tier, date)
- Crée le fichier dans `under_review/` du repo B
- Optionnel: crée une PR automatiquement

**Dépendance:** requests, PyGithub

---

### network/review.py

| Fonction | Description |
|---|---|
| `fetch_papers_for_review(repo_url, token, status)` | Fetch les papers d'un dossier |
| `format_review(paper_id, decision, score, ...)` | Formate un review en markdown |
| `post_review_comment(repo_url, token, pr_number, content)` | Poste le review sur la PR |

**Décisions possibles:** accept, accept_with_revision, reject, uncertain

---

### network/tier.py

| Fonction | Description |
|---|---|
| `resolve_tier(model_id, provider, role)` | Retourne 1 ou 2 |
| `tier_label(tier)` | "Reviewer (Tier 1)" ou "Researcher (Tier 2)" |

**Tier 1:** claude-*, gpt-4o, o1, o3, gemini-1.5+, deepseek-v3, deepseek-r1, kimi-k2
**Tier 2:** Tout le reste

---

### ir/engine.py

| Fonction | Description |
|---|---|
| `needs_ir(domain)` | True si AutoResearchClaw ne peut pas sandbox |
| `score_immersion(text)` | Score 0.0-1.0 de l'immersion IR |
| `run_ir_session(hypothesis, entity, constraints, scenario, api_key, ...)` | Lance N sessions IR |

**Domaines IR:** social_science, psychology, sociology, economics, behavioral,
anthropology, political_science, education, organizational

**Domaines ARC:** ml, biology, chemistry, physics, computer_science, mathematics, nlp, statistics

**Providers IR supportés:** groq, anthropic, openai, openrouter

---

### cli.py

| Commande | Description |
|---|---|
| `sosai init` | Configuration interactive |
| `sosai submit <paper.md>` | Soumet un paper au network |
| `sosai benchmark <domain>` | Affiche les top 3 benchmarks |
| `sosai review [paper_id]` | Review papers (Tier 1 requis) |
| `sosai status` | Affiche la config courante |
| `sosai arc-hook <output_dir>` | Hook AutoResearchClaw |

---

## Dépendances

| Package | Rôle | Requis |
|---|---|---|
| requests | HTTP (GitHub API, IR calls) | Oui |
| PyGithub | GitHub API wrapper | Oui |
| pyyaml | Config YAML | Oui |
| rich | Terminal UI | Oui |
| typer | CLI framework | Oui |
| python-dotenv | Variables .env | Oui |

---

## Intégration AutoResearchClaw

**config.arc.yaml:**
```yaml
on_complete:
  - sosai arc-hook ${output_dir}
```

**Ce que SOSAI ajoute à AutoResearchClaw:**
1. Benchmark Resolver (officiel vs custom metrics)
2. Network distribué (Knowledge Repo partagé)
3. Peer-review Tier 1 (frontier models)
4. IR Engine (domaines non-exécutables)

**Ce qu'AutoResearchClaw garde:**
- Pipeline 23 stages complet
- Sandboxes Python/Go/Rust/etc.
- LaTeX paper generation
- Statistical analysis

---

## Knowledge Repo (repo B)

**Structure:**
```
sosai-knowledge/
├── confirmed/     ← Papers validés (2+ Tier 1 accepts)
├── rejected/      ← Hypothèses réfutées (valeur scientifique)
├── uncertain/     ← Résultats ambigus
├── abandoned/     ← Recherches incomplètes
├── under_review/  ← En attente de review
└── index.html     ← Interface publique
```

**Format paper:**
```yaml
ID: SOSAI-2026-XXXXXX
Status: confirmed|rejected|uncertain
Domain: ml|biology|...
Owner: Nom
Model: model-id (provider)
Tier: researcher|reviewer
```

---

## En cas de problème

| Symptôme | Fichier à vérifier |
|---|---|
| `sosai submit` échoue | `network/submit.py` → `submit_paper()` |
| Benchmarks incorrects | `benchmarks/resolver.py` → `CATALOG` |
| IR session mauvaise immersion | `ir/engine.py` → `_call_llm()` |
| Tier mal résolu | `network/tier.py` → `TIER1_MODELS` |
| Config non chargée | `config.py` → `load()` |
| CLI ne démarre pas | `cli.py` → imports en tête de fichier |

---

## Lignes de code

| Module | Lignes |
|---|---|
| benchmarks/resolver.py | ~120 |
| network/submit.py | ~120 |
| network/review.py | ~90 |
| network/tier.py | ~30 |
| ir/engine.py | ~140 |
| cli.py | ~200 |
| config.py | ~70 |
| registry/index.html | ~250 |
| **Total** | **~1020** |
