#!/usr/bin/env bash
set -e

echo "=== AI PBOM Demo ==="
echo ""
echo "This demo scans sample AI data assets for privacy risks."
echo "No database or external services required."
echo ""

# Ensure we're in the project root
cd "$(dirname "$0")"

# Clean previous output
rm -rf demo/output
mkdir -p demo/output

echo "[1/3] Scanning sample data for assets and privacy signals..."
aipbom scan --config demo/config.yaml --apps demo/apps.yaml --out demo/output/
echo ""

echo "[2/3] Building PBOM (mapping apps, scoring risks)..."
aipbom build --config demo/config.yaml --apps demo/apps.yaml --out demo/output/
echo ""

echo "[3/3] Generating report..."
aipbom report --pbom demo/output/pbom.json --out demo/output/report.md
echo ""

echo "=== Done ==="
echo ""
echo "Outputs:"
echo "  demo/output/assets.json    — Discovered assets"
echo "  demo/output/findings.json  — Privacy findings"
echo "  demo/output/pbom.json      — Full PBOM artifact"
echo "  demo/output/report.md      — Human-readable report"
echo ""
echo "Open demo/output/report.md to see the results."
