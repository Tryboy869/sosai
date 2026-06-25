"""
SOSAI -- CLI Principal
sosai init / submit / review / status / benchmark
"""

import sys
import os
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel   import Panel
from rich.table   import Table
from rich.text    import Text
from rich         import box

app     = typer.Typer(name="sosai", help="SOSAI -- Distributed knowledge network for AI research", add_completion=False)
console = Console()


# ── sosai init ────────────────────────────────────────────────

@app.command()
def init():
    """Configure SOSAI interactivement."""
    from rich.prompt import Prompt, Confirm
    from . import config as cfg_module

    console.print(Panel(
        "[bold blue]SOSAI[/bold blue] -- Scientific Operating System for AI\n[dim]Configuration initiale[/dim]",
        border_style="blue", padding=(1, 2)
    ))

    cfg = cfg_module.SOSAIConfig()

    console.print("\n[cyan]── Identite ──[/cyan]")
    cfg.owner_name   = Prompt.ask("Votre nom")
    cfg.owner_github = Prompt.ask("GitHub username")

    console.print("\n[cyan]── Modele LLM (pour IR Engine) ──[/cyan]")
    providers = ["groq", "anthropic", "openai", "gemini", "openrouter", "huggingface", "local"]
    console.print("Providers: " + ", ".join(providers))
    cfg.provider = Prompt.ask("Provider", choices=providers, default="groq")

    model_defaults = {
        "groq": "llama-3.3-70b-versatile", "anthropic": "claude-sonnet-4-6",
        "openai": "gpt-4o", "gemini": "gemini-1.5-pro",
        "openrouter": "mistralai/mistral-7b-instruct",
        "huggingface": "meta-llama/Meta-Llama-3-8B-Instruct", "local": "llama3",
    }
    cfg.model_id = Prompt.ask("Model ID", default=model_defaults.get(cfg.provider, ""))

    if cfg.provider != "local":
        env_keys = {
            "groq": "GROQ_API_KEY", "anthropic": "ANTHROPIC_API_KEY",
            "openai": "OPENAI_API_KEY", "gemini": "GEMINI_API_KEY",
            "openrouter": "OPENROUTER_API_KEY", "huggingface": "HUGGINGFACE_API_KEY",
        }
        env_var = env_keys.get(cfg.provider, "API_KEY")
        api_key = Prompt.ask(f"API Key ({env_var}) -- stockee dans .env", password=True, default="")
        if api_key:
            env_file = Path(".env")
            with open(env_file, "a") as f:
                f.write(f"\n{env_var}={api_key}\n")
            cfg.api_key = api_key
            console.print(f"[dim]Cle sauvegardee dans .env ({env_var})[/dim]")

    console.print("\n[cyan]── Role dans le reseau SOSAI ──[/cyan]")
    console.print("  researcher → conduit des recherches originales")
    console.print("  reviewer   → evalue les papers (Tier 1 requis)")
    cfg.role = Prompt.ask("Role", choices=["researcher", "reviewer"], default="researcher")

    console.print("\n[cyan]── Knowledge Repo (repo B GitHub) ──[/cyan]")
    cfg.knowledge_repo_url = Prompt.ask("URL du Knowledge Repo", default="")
    if cfg.knowledge_repo_url:
        gh_token = Prompt.ask("GitHub Token", password=True, default="")
        if gh_token:
            env_file = Path(".env")
            with open(env_file, "a") as f:
                f.write(f"\nGITHUB_TOKEN={gh_token}\n")
            cfg.github_token = gh_token
        cfg.require_human_validation = Confirm.ask("Validation humaine avant soumission?", default=True)

    cfg_module.save(cfg)
    console.print("\n[green]✅ Configuration sauvegardee dans ~/.sosai/config.yaml[/green]")
    console.print("[dim]Lance: sosai submit <paper.md>[/dim]\n")


# ── sosai submit ──────────────────────────────────────────────

@app.command()
def submit(
    paper_path: str = typer.Argument(..., help="Chemin vers le paper .md a soumettre"),
    verbose:    bool = typer.Option(False, "--verbose", "-v"),
):
    """Soumet un paper au Knowledge Repo SOSAI."""
    from . import config as cfg_module
    from .network.submit import submit_paper, SubmitError
    from .benchmarks.resolver import detect_domain_from_paper, format_for_paper

    cfg = cfg_module.load()

    if not cfg.knowledge_repo_url:
        console.print("[red]❌ knowledge_repo_url non configure. Lance: sosai init[/red]")
        raise typer.Exit(1)

    if not cfg.github_token:
        console.print("[red]❌ GITHUB_TOKEN manquant. Ajoute-le dans .env[/red]")
        raise typer.Exit(1)

    paper = Path(paper_path)
    if not paper.exists():
        console.print(f"[red]❌ Fichier introuvable: {paper_path}[/red]")
        raise typer.Exit(1)

    # Detecter domaine et injecter benchmarks
    domain = detect_domain_from_paper(str(paper))
    console.print(f"[blue]🔬 Domaine detecte: {domain}[/blue]")

    benchmark_section = format_for_paper(domain)
    with open(paper, "r", encoding="utf-8") as f:
        content = f.read()

    if "## Official Benchmarks" not in content:
        with open(paper, "a", encoding="utf-8") as f:
            f.write(f"\n\n{benchmark_section}\n")
        console.print("[green]✅ Benchmarks officiels injectes dans le paper[/green]")

    with console.status("[blue]Soumission au Knowledge Repo...[/blue]"):
        try:
            result = submit_paper(
                paper_path=str(paper),
                repo_url=cfg.knowledge_repo_url,
                github_token=cfg.github_token,
                owner_name=cfg.owner_name,
                model_id=cfg.model_id,
                provider=cfg.provider,
                tier=cfg.role,
                require_human_validation=cfg.require_human_validation,
            )
            console.print(Panel(
                f"[green]✅ Soumis avec succes[/green]\n\n"
                f"ID: [bold]{result['paper_id']}[/bold]\n"
                f"URL: {result.get('url', 'N/A')}\n"
                + (f"PR: {result['pr'].get('pr_url', '')}" if result.get('pr') else ""),
                title="[bold]SOSAI Submit[/bold]", border_style="green"
            ))
        except SubmitError as e:
            console.print(f"[red]❌ Erreur soumission: {e}[/red]")
            raise typer.Exit(1)


# ── sosai benchmark ────────────────────────────────────────────

@app.command()
def benchmark(
    domain: str = typer.Argument(..., help="Domaine scientifique (ex: ml, biology, physics)"),
):
    """Affiche les top 3 benchmarks officiels pour un domaine."""
    from .benchmarks.resolver import resolve

    benchmarks = resolve(domain)
    table = Table(box=box.ROUNDED, show_header=True, padding=(0, 2))
    table.add_column("#",         style="dim", width=3)
    table.add_column("Benchmark", style="bold cyan")
    table.add_column("Mesure",    style="white")
    table.add_column("URL",       style="dim blue")

    for i, b in enumerate(benchmarks, 1):
        table.add_row(str(i), b["name"], b["measures"], b["url"] or "N/A")

    console.print(Panel(table, title=f"[bold]Top 3 Benchmarks — {domain}[/bold]", border_style="blue"))


# ── sosai review ──────────────────────────────────────────────

@app.command()
def review(
    paper_id: Optional[str] = typer.Argument(None, help="ID du paper a reviewer"),
):
    """Review un paper soumis (Tier 1 uniquement)."""
    from . import config as cfg_module
    from .network.tier import resolve_tier, tier_label
    from .network.review import fetch_papers_for_review

    cfg  = cfg_module.load()
    tier = resolve_tier(cfg.model_id, cfg.provider, cfg.role)

    if tier != 1:
        console.print(f"[yellow]⚠️  Tier 1 requis pour la review.[/yellow]")
        console.print(f"[dim]Votre modele ({cfg.model_id}) est Tier {tier}.[/dim]")
        raise typer.Exit(0)

    console.print(f"[green]✅ Reviewer Tier 1: {cfg.model_id}[/green]")

    if not cfg.knowledge_repo_url:
        console.print("[red]❌ knowledge_repo_url non configure.[/red]")
        raise typer.Exit(1)

    with console.status("Fetch papers en attente de review..."):
        papers = fetch_papers_for_review(cfg.knowledge_repo_url, cfg.github_token)

    if not papers:
        console.print("[dim]Aucun paper en attente de review.[/dim]")
        return

    console.print(f"[blue]{len(papers)} papers en attente:[/blue]")
    for p in papers:
        console.print(f"  • {p['id']} — {p.get('url', '')}")


# ── sosai status ──────────────────────────────────────────────

@app.command()
def status():
    """Affiche la configuration et l'etat du systeme."""
    from . import config as cfg_module
    from .network.tier import resolve_tier, tier_label

    cfg  = cfg_module.load()
    tier = resolve_tier(cfg.model_id, cfg.provider, cfg.role)

    table = Table(box=box.ROUNDED, show_header=False, padding=(0, 2))
    table.add_column("Key",   style="cyan",  no_wrap=True)
    table.add_column("Value", style="white")

    table.add_row("Owner",          cfg.owner_name or "[dim]Non configure[/dim]")
    table.add_row("GitHub",         cfg.owner_github or "[dim]Non configure[/dim]")
    table.add_row("Model",          f"{cfg.model_id} ({cfg.provider})")
    table.add_row("Tier effectif",  f"Tier {tier} — {tier_label(tier)}")
    table.add_row("Role",           cfg.role)
    table.add_row("IR Engine",      "✅ Active" if cfg.ir_enabled else "❌ Desactive")
    table.add_row("Knowledge Repo", cfg.knowledge_repo_url or "[dim]Non configure[/dim]")
    table.add_row("GitHub Token",   "✅ Configure" if cfg.github_token else "❌ Manquant")
    table.add_row("Human Validation", "✅ Requise" if cfg.require_human_validation else "❌ Auto")

    console.print(Panel(table, title="[bold]🔬 SOSAI Status[/bold]", border_style="blue"))


# ── sosai arc-hook ────────────────────────────────────────────

@app.command("arc-hook")
def arc_hook(
    output_dir: str = typer.Argument(..., help="Dossier output d'AutoResearchClaw"),
    auto:       bool = typer.Option(False, "--auto", help="Soumettre sans confirmation"),
):
    """
    Hook pour AutoResearchClaw -- ajoute dans config.arc.yaml:
    on_complete:
      - sosai arc-hook ${output_dir}
    """
    from . import config as cfg_module

    output = Path(output_dir)
    papers = list(output.glob("**/*.md"))

    if not papers:
        console.print(f"[yellow]Aucun paper .md trouve dans {output_dir}[/yellow]")
        return

    console.print(Panel(
        f"[bold blue]SOSAI Network[/bold blue] disponible\n\n"
        f"{len(papers)} paper(s) genere(s) par AutoResearchClaw detecte(s).\n\n"
        f"Soumets au reseau distribue SOSAI pour peer-review global\n"
        f"par des IA frontier (Claude, GPT, Gemini).\n\n"
        f"[dim]sosai submit {papers[0]} pour continuer[/dim]",
        border_style="blue", padding=(1, 2)
    ))

    if auto:
        for p in papers:
            ctx = typer.Context(submit)
            submit(str(p))
        return

    console.print("\n[dim]Lance 'sosai submit <fichier.md>' pour soumettre.[/dim]")
    console.print("[dim]Lance 'sosai status' pour verifier ta configuration.[/dim]")


if __name__ == "__main__":
    app()
