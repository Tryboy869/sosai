"""
SOSAI -- Benchmark Resolver
Top 3 benchmarks officiels par domaine scientifique.
Comble le gap AutoResearchClaw : mesure contre standards officiels.
"""

CATALOG = {
    "ml": [
        {"name": "MMLU",      "url": "https://github.com/hendrycks/test",   "measures": "raisonnement general"},
        {"name": "HumanEval", "url": "https://github.com/openai/human-eval","measures": "generation de code"},
        {"name": "HellaSwag", "url": "https://rowanzellers.com/hellaswag/", "measures": "raisonnement commun"},
    ],
    "biology": [
        {"name": "PubMedQA",      "url": "https://pubmedqa.github.io/",         "measures": "questions biomedicales"},
        {"name": "MedQA (USMLE)", "url": "https://github.com/jind11/MedQA",    "measures": "connaissances medicales"},
        {"name": "MIMIC-III",     "url": "https://physionet.org/content/mimiciii","measures": "donnees cliniques reelles"},
    ],
    "chemistry": [
        {"name": "ChemBench",  "url": "https://github.com/lamalab-org/chembench","measures": "proprietes moleculaires"},
        {"name": "QM9",        "url": "https://doi.org/10.1038/sdata.2014.22",  "measures": "proprietes quantiques"},
        {"name": "MoleculeNet","url": "https://moleculenet.org/",               "measures": "multi-taches moleculaires"},
    ],
    "physics": [
        {"name": "PhysicsQA","url": "https://allenai.org/data/sciq",           "measures": "problemes de physique"},
        {"name": "JEEBench", "url": "https://github.com/dair-iitd/jeebench",   "measures": "problemes avances"},
        {"name": "SciQ",     "url": "https://allenai.org/data/sciq",           "measures": "sciences generales"},
    ],
    "computer_science": [
        {"name": "SWE-bench",     "url": "https://swe-bench.github.io/",       "measures": "bugs reels GitHub"},
        {"name": "LiveCodeBench", "url": "https://livecodebench.github.io/",   "measures": "coding temps reel"},
        {"name": "BigCodeBench",  "url": "https://bigcode-bench.github.io/",   "measures": "programmation complexe"},
    ],
    "nlp": [
        {"name": "SuperGLUE","url": "https://super.gluebenchmark.com/",        "measures": "comprehension linguistique"},
        {"name": "BIG-Bench","url": "https://github.com/google/BIG-bench",     "measures": "taches diverses"},
        {"name": "MT-Bench", "url": "https://github.com/lm-sys/FastChat",      "measures": "conversations multi-tours"},
    ],
    "mathematics": [
        {"name": "MATH",  "url": "https://github.com/hendrycks/math",          "measures": "competition mathematique"},
        {"name": "GSM8K", "url": "https://github.com/openai/grade-school-math","measures": "raisonnement scolaire"},
        {"name": "AIME",  "url": "https://artofproblemsolving.com/",           "measures": "competitions"},
    ],
    "neuroscience": [
        {"name": "NeuroQA",    "url": "https://huggingface.co/datasets/neuroqa",          "measures": "connaissances neuro"},
        {"name": "BrainBench", "url": "https://github.com/braingpt-lovelab/brainbench",  "measures": "predictions neuro"},
        {"name": "NeuroBench", "url": "https://neurobench.ai/",                           "measures": "calcul neuromorphique"},
    ],
    "economics": [
        {"name": "EconBench", "url": "https://huggingface.co/datasets/econbench","measures": "raisonnement economique"},
        {"name": "FinBench",  "url": "https://github.com/the-finai/finbench",    "measures": "connaissances financieres"},
        {"name": "MMLU-Econ", "url": "https://github.com/hendrycks/test",        "measures": "economie MMLU"},
    ],
    "social_science": [
        {"name": "SocBench",   "url": "https://huggingface.co/datasets/TIGER-Lab/SocBench","measures": "sciences sociales"},
        {"name": "MMLU-Social","url": "https://github.com/hendrycks/test",                 "measures": "sciences sociales MMLU"},
        {"name": "BehavBench", "url": "https://huggingface.co/datasets/behavbench",        "measures": "comportements humains"},
    ],
}

ALIASES = {
    "machine learning": "ml", "artificial intelligence": "ml",
    "deep learning": "ml", "reinforcement learning": "ml",
    "medicine": "biology", "medical": "biology",
    "biochemistry": "chemistry", "molecular biology": "biology",
    "genetics": "biology", "programming": "computer_science",
    "software": "computer_science", "coding": "computer_science",
    "language": "nlp", "linguistics": "nlp",
    "brain": "neuroscience", "cognitive": "neuroscience",
    "math": "mathematics", "statistics": "mathematics",
    "finance": "economics", "economy": "economics",
    "psychology": "social_science", "sociology": "social_science",
}

GENERAL_FALLBACK = [
    {"name": "Custom Metrics",      "url": "", "measures": "metriques du chercheur"},
    {"name": "Human Baseline",      "url": "", "measures": "performance humaine"},
    {"name": "Literature Baseline", "url": "", "measures": "resultats publies"},
]


def resolve(domain: str, top_n: int = 3) -> list:
    if not domain:
        return GENERAL_FALLBACK[:top_n]
    key = domain.lower().strip()
    key = ALIASES.get(key, key)
    return (CATALOG.get(key) or GENERAL_FALLBACK)[:top_n]


def resolve_names(domain: str) -> list:
    return [b["name"] for b in resolve(domain)]


def detect_domain_from_paper(paper_path: str) -> str:
    try:
        with open(paper_path, "r", encoding="utf-8") as f:
            content = f.read()
        for line in content.split("\n"):
            if "**Domain:**" in line or "domain:" in line.lower():
                domain = line.split(":")[-1].strip().strip("*").lower()
                return ALIASES.get(domain, domain)
    except Exception:
        pass
    return "general"


def format_for_paper(domain: str) -> str:
    benchmarks = resolve(domain)
    lines = [f"## Official Benchmarks (SOSAI Standard)\n\nDomain: **{domain}**\n"]
    for i, b in enumerate(benchmarks, 1):
        ref = f" [{b['url']}]" if b["url"] else ""
        lines.append(f"{i}. **{b['name']}**{ref}: {b['measures']}")
    return "\n".join(lines)
