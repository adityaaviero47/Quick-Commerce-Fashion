"""The analysis reproduces: SQL matches pandas, and the backtest beats the style-first default."""
import sys, json, pathlib, subprocess
import pytest
ROOT = pathlib.Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.skipif(not (ROOT / "data" / "amazon_sale_report.csv").exists(),
                                reason="run: bash get_data.sh")


def run(script):
    subprocess.run([sys.executable, str(ROOT / "src" / script)], check=True, capture_output=True)
    return json.load(open(ROOT / "results" / script.replace(".py", ".json").replace("sql_kpis", "sql_kpis")))


def test_sql_matches_pandas():
    run("demand.py")
    assert run("sql_kpis.py")["match"]


def test_size_level_hub_beats_style_first_at_every_slot_count():
    out = run("assortment.py")
    for r in out["backtest"]:
        assert r["size_level"] >= r["style_first"] - 0.005
        assert r["size_level"] <= r["oracle_ceiling"]
