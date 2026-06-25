# Changelog

All notable changes to SOSAI will be documented here.
Format: [Semantic Versioning](https://semver.org)

---

## [0.1.0] — 2026-06-24

### Added
- Benchmark Resolver: top 3 official benchmarks per scientific domain (10 domains)
- Knowledge Repo layer: submit papers to distributed GitHub repo via GitHub API
- IR Engine: simulation fallback for non-executable domains (social science, psychology, economics)
- Tier system: Tier 1 (frontier models) as reviewers, Tier 2 as researchers
- CLI: `sosai init`, `sosai submit`, `sosai benchmark`, `sosai review`, `sosai status`, `sosai arc-hook`
- AutoResearchClaw integration via `on_complete` hook
- Knowledge Registry: public HTML interface for browsing validated papers

### Domains covered by Benchmark Resolver
- ML/AI, Biology, Chemistry, Physics, Computer Science
- NLP, Mathematics, Neuroscience, Economics, Social Science

---

## [Unreleased]
- PyPI publication
- Telegram notifications
- Web registry deployment
