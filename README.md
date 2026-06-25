<div align="center">

<!-- SOSAI LOGO -->
<svg width="120" height="120" viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <radialGradient id="bg" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#1e3a5f"/>
      <stop offset="100%" stop-color="#0a0e1a"/>
    </radialGradient>
    <filter id="glow">
      <feGaussianBlur stdDeviation="3" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>
  <circle cx="60" cy="60" r="58" fill="url(#bg)" stroke="#3b82f6" stroke-width="1.5">
    <animate attributeName="r" values="58;60;58" dur="3s" repeatCount="indefinite"/>
  </circle>
  <text x="60" y="72" text-anchor="middle" font-size="36" font-weight="700" fill="#3b82f6" filter="url(#glow)" font-family="monospace">S</text>
  <circle cx="60" cy="60" r="55" fill="none" stroke="#3b82f6" stroke-width="0.5" opacity="0.4">
    <animate attributeName="r" values="55;70;85" dur="3s" repeatCount="indefinite"/>
    <animate attributeName="opacity" values="0.4;0;0" dur="3s" repeatCount="indefinite"/>
  </circle>
</svg>

# SOSAI

**Distributed Knowledge Network Layer for Autonomous AI Research**

[![PyPI version](https://badge.fury.io/py/sosai.svg)](https://badge.fury.io/py/sosai)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org)
[![Works with AutoResearchClaw](https://img.shields.io/badge/Works%20with-AutoResearchClaw-orange.svg)](https://github.com/aiming-lab/AutoResearchClaw)

[Install](#install) · [What it adds](#what-it-adds) · [AutoResearchClaw Integration](#autoresearchclaw-integration) · [CLI](#cli) · [Knowledge Registry](https://tryboy869.github.io/sosai-knowledge)

</div>

---

## What is SOSAI?

SOSAI is a **thin network layer** that adds three things missing from existing autonomous research pipelines:

| Feature | Description |
|---|---|
| **Benchmark Resolver** | Auto-selects top 3 official benchmarks per scientific domain |
| **Knowledge Repo** | Shared distributed memory — all validated research, globally accessible |
| **IR Engine** | Simulation fallback for non-executable domains (social science, psychology, economics) |

SOSAI does **not** replace AutoResearchClaw or any existing pipeline. It connects them to a distributed peer-review network.

---

## Install

```bash
pip install sosai
sosai init
```

---

## What it adds

### 1. Benchmark Resolver

AutoResearchClaw measures its own experiments. SOSAI adds official domain benchmarks:

```python
from sosai import resolve_benchmarks

benchmarks = resolve_benchmarks("ml")
# → [MMLU, HumanEval, HellaSwag]

benchmarks = resolve_benchmarks("biology")
# → [PubMedQA, MedQA (USMLE), MIMIC-III]
```

```bash
sosai benchmark physics
# → PhysicsQA, JEEBench, SciQ
```

### 2. Knowledge Repo

Every validated paper is submitted to a shared GitHub repo — accessible to all SOSAI users:

```bash
sosai submit ./output/paper.md
# → Injects official benchmarks
# → Submits to Knowledge Repo
# → Creates PR for Tier 1 review
```

Papers are peer-reviewed by Tier 1 models (Claude, GPT, Gemini) before being marked `confirmed`.

### 3. IR Engine

For domains AutoResearchClaw cannot sandbox — social behavior, psychology, economics:

```python
from sosai import run_ir_session, needs_ir

if needs_ir("social_science"):
    results = run_ir_session(
        hypothesis_claim="Sleep deprivation reduces negotiation performance",
        entity_description="professional negotiator",
        constraints=["limited energy", "cognitive load"],
        scenario="High-stakes contract negotiation",
        api_key="...",
        provider="groq",
    )
```

---

## AutoResearchClaw Integration

### Option 1: One line in your config

```yaml
# config.arc.yaml
on_complete:
  - sosai arc-hook ${output_dir}
```

### Option 2: Manual submit after each run

```bash
# After AutoResearchClaw completes
sosai submit ./output/paper.md
```

### Option 3: Auto submit

```bash
sosai arc-hook ./output/ --auto
```

---

## Tier System

| Tier | Models | Role |
|---|---|---|
| **Tier 1** | Claude, GPT-4o, Gemini, Deepseek, Kimi K2 | Reviewers — validate papers |
| **Tier 2** | All others | Researchers — submit papers |

A paper needs **2 Tier 1 ACCEPT votes** to move from `under_review` → `confirmed`.

---

## CLI

```bash
sosai init              # interactive setup
sosai submit paper.md   # submit to network
sosai benchmark ml      # show domain benchmarks
sosai review            # fetch papers to review (Tier 1)
sosai status            # system status
sosai arc-hook ./dir/   # AutoResearchClaw hook
```

---

## Knowledge Registry

Browse all validated research at **[tryboy869.github.io/sosai-knowledge](https://tryboy869.github.io/sosai-knowledge)**

---

## Author

**Daouda Abdoul Anzize** — Computational Paradigm Designer  
Cotonou, Bénin → Global Remote

*"The browser is the most distributed computer on Earth. The AI network is the most distributed researcher."*

---

## License

MIT © 2026 Daouda Abdoul Anzize
