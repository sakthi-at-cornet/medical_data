"""Command-line interface for EL pipeline."""

import logging
import sys
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.logging import RichHandler

from .config import PipelineConfig
from .pipeline import ELPipeline

# Setup rich console
console = Console()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(console=console, rich_tracebacks=True)]
)

logger = logging.getLogger(__name__)


def run_full_sync():
    """Run full sync of all sources."""
    console.print("\n[bold cyan]EL Pipeline - Full Sync[/bold cyan]\n")

    try:
        # Load configuration
        config = PipelineConfig.from_env(".env.el")
        pipeline = ELPipeline(config)

        # Run sync
        start_time = datetime.now()
        console.print("[yellow]Starting full sync...[/yellow]\n")

        stats = pipeline.run_full_sync()

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # Display results
        console.print("\n[bold green]✓ Sync completed successfully![/bold green]\n")

        table = Table(title="Sync Statistics")
        table.add_column("Source", style="cyan")
        table.add_column("Records", justify="right", style="magenta")

        table.add_row("Refills", str(stats['refills_count']))
        table.add_row("Bodies", str(stats['bodies_count']))
        table.add_row("Springs", str(stats['springs_count']))
        table.add_row("[bold]Total[/bold]", f"[bold]{sum(stats.values())}[/bold]")

        console.print(table)
        console.print(f"\n[dim]Duration: {duration:.2f}s[/dim]\n")

        # Verify warehouse
        warehouse_stats = pipeline.get_warehouse_stats()
        console.print("[bold]Warehouse verification:[/bold]")
        console.print(f"  Refills: {warehouse_stats['refills_count']} records")
        console.print(f"  Bodies: {warehouse_stats['bodies_count']} records")
        console.print(f"  Springs: {warehouse_stats['springs_count']} records\n")

        pipeline.close()

    except Exception as e:
        console.print(f"\n[bold red]✗ Error: {e}[/bold red]\n")
        logger.exception("Pipeline failed")
        sys.exit(1)


def check_warehouse():
    """Check warehouse statistics."""
    console.print("\n[bold cyan]Warehouse Statistics[/bold cyan]\n")

    try:
        config = PipelineConfig.from_env(".env.el")
        pipeline = ELPipeline(config)

        stats = pipeline.get_warehouse_stats()

        table = Table(title="Warehouse Contents")
        table.add_column("Table", style="cyan")
        table.add_column("Records", justify="right", style="magenta")

        table.add_row("raw.refills_production", str(stats['refills_count']))
        table.add_row("raw.bodies_production", str(stats['bodies_count']))
        table.add_row("raw.springs_production", str(stats['springs_count']))
        table.add_row("[bold]Total[/bold]", f"[bold]{sum(stats.values())}[/bold]")

        console.print(table)
        console.print()

        pipeline.close()

    except Exception as e:
        console.print(f"\n[bold red]✗ Error: {e}[/bold red]\n")
        logger.exception("Failed to check warehouse")
        sys.exit(1)


def main():
    """Main CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="EL Pipeline for Manufacturing Data")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Full sync command
    sync_parser = subparsers.add_parser("sync", help="Run full sync")

    # Check warehouse command
    check_parser = subparsers.add_parser("check", help="Check warehouse statistics")

    args = parser.parse_args()

    if args.command == "sync":
        run_full_sync()
    elif args.command == "check":
        check_warehouse()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
