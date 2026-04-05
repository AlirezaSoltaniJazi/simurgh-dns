"""Rich-based display rendering for benchmark results."""

from rich.console import Console
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.prompt import Confirm
from rich.table import Table

from simurgh_dns.models import BenchmarkResult

console = Console()


def create_progress(total: int, description: str) -> Progress:
    """Create a Rich progress bar for benchmark tracking."""
    progress = Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console,
    )
    progress.add_task(description, total=total)
    return progress


def display_results(results: list[BenchmarkResult]) -> None:
    """Display benchmark results in a rich table."""
    table = Table(title="\nDNS Benchmark Results", show_lines=False)
    table.add_column("#", style="bold", width=4, justify="right")
    table.add_column("Provider", style="bold", min_width=16)
    table.add_column("IP Address", min_width=16)
    table.add_column("Avg (ms)", justify="right", min_width=10)
    table.add_column("Min (ms)", justify="right", min_width=10)
    table.add_column("Max (ms)", justify="right", min_width=10)
    table.add_column("Reliability", justify="right", min_width=12)

    for i, r in enumerate(results, 1):
        if r.failed:
            avg_str = "FAIL"
            min_str = "-"
            max_str = "-"
        else:
            avg_str = f"{r.avg:.1f}"
            min_str = f"{r.min:.1f}"
            max_str = f"{r.max:.1f}"

        rel_str = f"{r.reliability:.0f}%"

        if i <= 3:
            style = "bold green"
        elif i <= 5:
            style = "green"
        elif r.failed:
            style = "dim red"
        else:
            style = ""

        table.add_row(
            str(i), r.provider, r.ip, avg_str, min_str, max_str, rel_str, style=style
        )

    console.print(table)


def display_results_json(results: list[BenchmarkResult]) -> None:
    """Display benchmark results as JSON."""
    import json

    data = [
        {
            "rank": i,
            "provider": r.provider,
            "ip": r.ip,
            "avg_ms": r.avg if not r.failed else None,
            "min_ms": r.min if not r.failed else None,
            "max_ms": r.max if not r.failed else None,
            "reliability": r.reliability,
        }
        for i, r in enumerate(results, 1)
    ]
    console.print_json(json.dumps(data))


def display_dns_info(
    interface: str, current_dns: list[str], best: BenchmarkResult, best_ips: list[str]
) -> None:
    """Display current DNS info and recommendation."""
    console.print(f"\nActive network interface: [bold]{interface}[/bold]")
    console.print(f"Current DNS: [cyan]{', '.join(current_dns)}[/cyan]")
    console.print(
        f"Recommended: [bold green]{best.provider}[/bold green] "
        f"({', '.join(best_ips)}) — avg {best.avg:.1f} ms"
    )


def prompt_set_best(provider: str, ips: list[str]) -> bool:
    """Prompt the user to set the best DNS."""
    try:
        return Confirm.ask(f"\nSet DNS to {provider} ({', '.join(ips)})?")
    except EOFError:
        console.print("\n[dim]Non-interactive mode — skipping DNS change.[/dim]")
        return False


def prompt_pick_from_list(total: int) -> int | None:
    """Prompt the user to pick a DNS server by rank number.

    Returns the 0-based index or None to exit.
    """
    console.print(
        "\n[dim]Enter a [bold]#ID[/bold] from the results table to set that DNS, "
        "or [bold]n[/bold] to exit:[/dim]"
    )
    while True:
        try:
            choice = console.input("[bold]> [/bold]").strip().lower()
        except EOFError:
            return None

        if choice in ("n", "no", "q", "quit", "exit", ""):
            return None

        try:
            idx = int(choice)
        except ValueError:
            console.print(
                "[yellow]Enter a number from the list or 'n' to exit.[/yellow]"
            )
            continue

        if idx < 1 or idx > total:
            console.print(
                f"[yellow]Please enter a number between 1 and {total}.[/yellow]"
            )
            continue

        return idx - 1
