"""CLI entry point for simurgh-dns."""

from __future__ import annotations

import argparse
import sys
from typing import TYPE_CHECKING

from simurgh_dns import __version__
from simurgh_dns.benchmark import run_benchmark
from simurgh_dns.display import (
    console,
    create_progress,
    display_dns_info,
    display_results,
    display_results_json,
    prompt_pick_from_list,
    prompt_set_best,
)
from simurgh_dns.servers import DEFAULT_ROUNDS, DNS_SERVERS

if TYPE_CHECKING:
    from simurgh_dns.models import BenchmarkResult
    from simurgh_dns.platform_dns.base import DNSSetter


def _get_dns_setter_or_exit() -> DNSSetter:
    """Get the platform DNS setter or exit with an error."""
    from simurgh_dns.platform_dns import get_dns_setter

    try:
        return get_dns_setter()
    except RuntimeError as e:
        console.print(f"[red]{e}[/red]")
        sys.exit(1)


def _handle_reset() -> None:
    """Handle --reset flag."""
    setter = _get_dns_setter_or_exit()
    interface = setter.get_active_interface()
    if not interface:
        console.print("[red]Could not detect active network interface.[/red]")
        sys.exit(1)
    console.print(f"Resetting DNS on [bold]{interface}[/bold] to DHCP default...")
    if setter.reset_dns(interface):
        console.print("[bold green]DNS reset to DHCP default.[/bold green]")
    else:
        console.print("[red]Failed to reset DNS. Check your privileges.[/red]")


def _handle_set(dns_ip: str) -> None:
    """Handle --set flag."""
    setter = _get_dns_setter_or_exit()
    interface = setter.get_active_interface()
    if not interface:
        console.print("[red]Could not detect active network interface.[/red]")
        sys.exit(1)
    current = setter.get_current_dns(interface)
    console.print(f"Active network interface: [bold]{interface}[/bold]")
    console.print(f"Current DNS: [cyan]{', '.join(current)}[/cyan]")
    console.print(f"Setting DNS to: [bold]{dns_ip}[/bold]")
    if setter.set_dns(interface, [dns_ip]):
        console.print("[bold green]DNS set successfully![/bold green]")
    else:
        console.print("[red]Failed to set DNS. Check your privileges.[/red]")


def _apply_dns(
    setter: DNSSetter, interface: str, provider: str, ips: list[str]
) -> None:
    """Apply DNS choice and print result."""
    if setter.set_dns(interface, ips):
        console.print(
            f"[bold green]DNS set to {provider} "
            f"({', '.join(ips)}) successfully![/bold green]"
        )
    else:
        console.print("[red]Failed to set DNS. Check your privileges.[/red]")


def _offer_set_dns(results: list[BenchmarkResult]) -> None:
    """Offer to set the best DNS server after benchmarking."""
    working = [r for r in results if not r.failed]
    if not working:
        console.print("[red]No DNS servers responded successfully.[/red]")
        return

    setter = _get_dns_setter_or_exit()
    interface = setter.get_active_interface()
    if not interface:
        console.print(
            "[yellow]Could not detect active network interface. "
            "Skipping DNS configuration.[/yellow]"
        )
        return

    best = working[0]
    best_ips = DNS_SERVERS.get(best.provider, [best.ip])
    current = setter.get_current_dns(interface)

    display_dns_info(interface, current, best, best_ips)

    if prompt_set_best(best.provider, best_ips):
        _apply_dns(setter, interface, best.provider, best_ips)
        return

    picked_idx = prompt_pick_from_list(len(results))
    if picked_idx is None:
        console.print("[dim]No changes made.[/dim]")
        return

    picked = results[picked_idx]
    if picked.failed:
        console.print(
            "[yellow]That server failed the benchmark. No changes made.[/yellow]"
        )
        return

    picked_ips = DNS_SERVERS.get(picked.provider, [picked.ip])
    _apply_dns(setter, interface, picked.provider, picked_ips)


def _run_benchmark_with_progress(
    rounds: int, json_output: bool
) -> list[BenchmarkResult]:
    """Run benchmark with Rich progress bar and display results."""
    servers = DNS_SERVERS
    total = sum(len(ips) for ips in servers.values())

    if not json_output:
        console.print("[bold]DNS Benchmark Tool[/bold]")
        console.print(f"Testing {len(servers)} providers ({total} servers)")
        console.print(f"Rounds: {rounds} | Domains: 5 | Timeout: 3s\n")

    progress = create_progress(total, f"Benchmarking {total} DNS servers...")
    with progress:
        task_id = next(iter(progress._tasks.keys()))

        def on_progress(completed: int, _total: int) -> None:
            progress.update(task_id, completed=completed)

        results = run_benchmark(
            rounds=rounds,
            progress_callback=on_progress,
        )

    if json_output:
        display_results_json(results)
    else:
        display_results(results)

    return results


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="simurgh-dns",
        description=(
            "Benchmark public DNS servers and set the fastest one. "
            "Works on macOS, Linux, and Windows."
        ),
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    parser.add_argument(
        "--rounds",
        type=int,
        default=DEFAULT_ROUNDS,
        help=f"Number of benchmark rounds per server (default: {DEFAULT_ROUNDS})",
    )
    parser.add_argument(
        "--set",
        dest="set_dns",
        metavar="DNS_IP",
        help="Directly set a specific DNS server IP (e.g., 1.1.1.1)",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Reset DNS to DHCP default",
    )
    parser.add_argument(
        "--no-set",
        action="store_true",
        help="Benchmark only — don't offer to set DNS",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON",
    )

    args = parser.parse_args()

    if args.reset:
        _handle_reset()
        return

    if args.set_dns:
        _handle_set(args.set_dns)
        return

    results = _run_benchmark_with_progress(args.rounds, args.json)

    if not args.no_set and not args.json:
        _offer_set_dns(results)
