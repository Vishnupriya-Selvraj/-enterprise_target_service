import os
from typing import Any, Dict

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.markdown import Markdown
    from rich.theme import Theme

    custom_theme = Theme({
        "info": "dim cyan",
        "warning": "magenta",
        "danger": "bold red",
        "success": "bold green"
    })
    console = Console(theme=custom_theme)
    HAS_RICH = True
except ImportError:
    HAS_RICH = False
    console = None

class IncidentPresenter:
    """CLI Presentation layer for live streaming demonstration."""

    @staticmethod
    def print_header(project_name: str, model_name: str) -> None:
        title = "⚡ ENTERPRISE AGENTIC WORKBENCH: INCIDENT TRIAGE ⚡"
        subtitle = (
            f"Stack: LangChain (Tools) + LangGraph (Cyclic Engine) + LangSmith (Observability)\n"
            f"Model: [bold green]{model_name}[/bold green] | Tracing Project: [bold yellow]{project_name}[/bold yellow]"
        )
        if HAS_RICH:
            console.print(Panel.fit(f"[bold cyan]{title}[/bold cyan]\n[dim]{subtitle}[/dim]", border_style="bright_blue"))
        else:
            print("=" * 75)
            print(title)
            print(f"Model: {model_name} | Tracing Project: {project_name}")
            print("=" * 75)

    @staticmethod
    def print_alert(alert_text: str) -> None:
        if HAS_RICH:
            console.print(Panel(f"[bold white]{alert_text}[/bold white]", title="🚨 [bold red]Incoming Production Alert[/bold red]", border_style="red"))
        else:
            print(f"\n[ALERT]: {alert_text}\n")

    @staticmethod
    def print_step(step_number: int, tool_name: str, tool_args: Dict[str, Any]) -> None:
        if HAS_RICH:
            console.print(
                f"[bold yellow]Step {step_number} (Reasoning ➔ Action):[/bold yellow] "
                f"Calling Tool [bold cyan]`{tool_name}`[/bold cyan] with args: [dim]{tool_args}[/dim]"
            )
        else:
            print(f"Step {step_number} (Agent): Requesting tool '{tool_name}' with args {tool_args}")

    @staticmethod
    def print_tool_output(output_content: str) -> None:
        preview = output_content.strip()
        if len(preview) > 200:
            preview = preview[:200] + "..."
        if HAS_RICH:
            console.print(f"  [dim cyan]└── Tool Response:[/dim cyan] [dim]{preview}[/dim]\n")
        else:
            print(f"  └── Tool Response: {preview}\n")

    @staticmethod
    def print_resolution(markdown_text: str) -> None:
        if HAS_RICH:
            console.print(Panel(Markdown(markdown_text), title="[bold green]Executive Incident Resolution Report[/bold green]", border_style="green"))
        else:
            print("\n" + "=" * 75)
            print("=== EXECUTIVE INCIDENT RESOLUTION REPORT ===")
            print(markdown_text)
            print("=" * 75)

    @staticmethod
    def print_footer(project_name: str) -> None:
        footer_text = (
            f"✅ [bold green]EXECUTION COMPLETE & TRACE DISPATCHED[/bold green]\n"
            f"🔗 [bold]Inspect Live Telemetry in LangSmith:[/bold] https://smith.langchain.com\n"
            f"📁 [bold]Project Target:[/bold] [cyan]{project_name}[/cyan]"
        )
        if HAS_RICH:
            console.print(Panel(footer_text, border_style="bright_magenta"))
        else:
            print("\n" + "=" * 75)
            print(f"EXECUTION COMPLETE. View live traces at https://smith.langchain.com (Project: {project_name})")
            print("=" * 75)
