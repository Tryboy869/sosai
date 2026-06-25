"""
SOSAI -- Scientific Operating System for AI
Distributed knowledge network layer for autonomous AI research.

pip install sosai

Usage:
    sosai init                    # configure
    sosai submit paper.md         # submit to network
    sosai benchmark ml            # show official benchmarks
    sosai review                  # review papers (Tier 1)
    sosai status                  # system status
    sosai arc-hook ./output/      # AutoResearchClaw hook
"""

__version__ = "0.1.0"
__author__  = "Daouda Abdoul Anzize"

from .config             import load as load_config, save as save_config, SOSAIConfig
from .benchmarks.resolver import resolve as resolve_benchmarks, resolve_names
from .network.submit      import submit_paper
from .network.review      import fetch_papers_for_review
from .network.tier        import resolve_tier
from .ir.engine           import run_ir_session, needs_ir, score_immersion

__all__ = [
    "load_config", "save_config", "SOSAIConfig",
    "resolve_benchmarks", "resolve_names",
    "submit_paper",
    "fetch_papers_for_review",
    "resolve_tier",
    "run_ir_session", "needs_ir", "score_immersion",
]
