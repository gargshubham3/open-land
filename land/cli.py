import click
import sys
import os
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from land.converter import LandAreaConverter
from land.parsers.maharashtra import MaharashtraSatbaraParser
from land.parsers.up_haryana import UPHaryanaJamabandiParser
from land.auditor import TitleRiskAuditor
from land.report import TitleReportGenerator

console = Console()

@click.group()
@click.version_option(version="0.1.0", prog_name="open-land")
def cli():
    """🗺️ open-land: Cadastral Land Record Parser & Title Risk Auditor for Indian Property Due Diligence."""
    pass

@cli.command()
@click.argument("input_path_or_text")
@click.option("--state", default="Maharashtra", type=click.Choice(["Maharashtra", "Uttar Pradesh"], case_sensitive=False))
def audit(input_path_or_text: str, state: str):
    """Audit a land record (7/12 or Jamabandi) for critical title defects and encumbrances."""
    if os.path.exists(input_path_or_text):
        with open(input_path_or_text, "r", encoding="utf-8") as f:
            text = f.read()
    else:
        text = input_path_or_text

    if state.lower() in ["maharashtra", "mh"]:
        record = MaharashtraSatbaraParser.parse_text(text)
    else:
        record = UPHaryanaJamabandiParser.parse_text(text)

    report = TitleRiskAuditor.audit(record)

    score_color = "green" if report.is_clear_marketable else "red"
    console.print(Panel(
        f"[bold]Parcel:[/bold] {report.survey_identifier}\n"
        f"[bold]Location:[/bold] {report.village_location}\n"
        f"[bold]Marketability Score:[/bold] [{score_color}]{report.marketability_score} / 100[/{score_color}]\n"
        f"[bold]Status:[/bold] {'[bold green]CLEAR & MARKETABLE[/bold green]' if report.is_clear_marketable else '[bold red]DEFECTIVE / ENCUMBERED[/bold red]'}",
        title="🏛️ Property Title Due Diligence Audit",
        border_style=score_color
    ))

    if report.flags:
        console.print(f"\n[bold red]Detected Legal Title Red Flags ({len(report.flags)}):[/bold red]")
        for f in report.flags:
            col = "red" if f.severity == "CRITICAL" else "yellow"
            console.print(Panel(
                f"[bold {col}][{f.severity}] {f.title}[/bold {col}]\n\n"
                f"{f.violation_detail}\n\n"
                f"[bold cyan]Statute:[/bold cyan] {f.statutory_reference}\n"
                f"[bold green]Precedent:[/bold green] {f.judicial_precedent}\n"
                f"[bold yellow]Required Action:[/bold yellow] {f.recommendation}",
                border_style=col
            ))

@cli.command()
@click.option("--hec", default=1.0, type=float, help="Hectares")
@click.option("--are", "ares", default=20.0, type=float, help="Ares")
def convert(hec: float, ares: float):
    """Convert Hectare/Are to Gunthas, Acres, Square Meters, and Bigha."""
    area = LandAreaConverter.from_hectare_are(hec, ares)
    table = Table(title=f"Indian Land Area Conversion for {hec}H {ares}R", show_header=True, header_style="bold green")
    table.add_column("Unit", style="bold yellow")
    table.add_column("Measurement", style="white")

    table.add_row("Square Meters", f"{area.sq_meters:,.2f} sq.m")
    table.add_row("Gunthas", f"{area.gunthas:,.2f} Gunthas (40 Gunthas = 1 Acre)")
    table.add_row("Acres", f"{area.acres:,.4f} Acres")
    table.add_row("Hectares", f"{area.hectares:,.4f} Hectares")
    table.add_row("Standard Bigha", f"{area.bigha:,.4f} Pucca Bigha")

    console.print(table)

@cli.command()
@click.argument("input_path_or_text")
@click.option("--state", default="Maharashtra")
@click.option("--output", default=None, help="Output Word .docx file path")
def report(input_path_or_text: str, state: str, output: str):
    """Generate a formal 30-year bank-ready Title Search Report."""
    if os.path.exists(input_path_or_text):
        with open(input_path_or_text, "r", encoding="utf-8") as f:
            text = f.read()
    else:
        text = input_path_or_text

    if state.lower() in ["maharashtra", "mh"]:
        record = MaharashtraSatbaraParser.parse_text(text)
    else:
        record = UPHaryanaJamabandiParser.parse_text(text)

    audit_res = TitleRiskAuditor.audit(record)
    rep = TitleReportGenerator.generate_report(record, audit_res)

    console.print(Panel(rep.formatted_document, title="Title Search Legal Report", border_style="cyan"))

    if output:
        out_path = Path(output)
        TitleReportGenerator.export_docx(rep, out_path)
        console.print(f"[bold green]Saved 30-Year Title Search Report to: {out_path}[/bold green]")

@cli.command()
@click.option("--host", default="127.0.0.1", help="Host interface")
@click.option("--port", default=8002, help="Port to listen on")
def serve(host: str, port: int):
    """Start the interactive open-land web dashboard."""
    import uvicorn
    console.print(f"[bold green]Starting OpenLand at http://{host}:{port}[/bold green]")
    uvicorn.run("land.web:app", host=host, port=port, reload=False)

if __name__ == "__main__":
    cli()
