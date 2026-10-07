"""Optional Streamlit disagreement explorer (#4).

  streamlit run src/eval/disagreement_app.py
"""
from __future__ import annotations

from pathlib import Path

from src.eval.harness import evaluate_methods, METHOD_CLASSES

try:
    import streamlit as st
except ImportError as e:  # pragma: no cover
    raise SystemExit("Install streamlit to use the disagreement UI") from e

st.set_page_config(page_title="Method disagreements", layout="wide")
st.title("URL method disagreement explorer")

golden = Path("tests/fixtures/urls.jsonl")
report = evaluate_methods(golden)
st.subheader("Metrics")
st.dataframe(report["metrics"])

urls = list(report["per_url"])
pick = st.selectbox("URL", urls)
labels = report["per_url"][pick]
st.write({m: labels.get(m) for m in METHOD_CLASSES})
