"""CLI entry point for AI PBOM."""

import click

from aipbom.pipeline import run_scan, run_build, run_report, run_all


@click.group()
@click.version_option()
def main():
    """AI PBOM - AI Privacy Posture & Data Map."""


@main.command()
@click.option("--config", required=True, type=click.Path(exists=True), help="Scan configuration file.")
@click.option("--apps", required=True, type=click.Path(exists=True), help="Application manifest file.")
@click.option("--out", required=True, type=click.Path(), help="Output directory.")
def scan(config, apps, out):
    """Discover assets, sample sources, run detectors."""
    run_scan(config, apps, out)


@main.command()
@click.option("--config", required=True, type=click.Path(exists=True), help="Scan configuration file.")
@click.option("--apps", required=True, type=click.Path(exists=True), help="Application manifest file.")
@click.option("--out", required=True, type=click.Path(), help="Output directory.")
def build(config, apps, out):
    """Map assets to applications, compute risk scores, assemble PBOM."""
    run_build(config, apps, out)


@main.command()
@click.option("--pbom", required=True, type=click.Path(exists=True), help="PBOM JSON file.")
@click.option("--out", required=True, type=click.Path(), help="Output report path.")
def report(pbom, out):
    """Render human-readable report from PBOM."""
    run_report(pbom, out)


@main.command()
@click.option("--config", required=True, type=click.Path(exists=True), help="Scan configuration file.")
@click.option("--apps", required=True, type=click.Path(exists=True), help="Application manifest file.")
@click.option("--out", required=True, type=click.Path(), help="Output directory.")
def run(config, apps, out):
    """Execute scan, build, and report in one command."""
    run_all(config, apps, out)
