import streamlit as st

def compute_kpis(df_raw, df_use, df_filtered):
    kpis = {}
    if df_raw is not None:
        kpis["전체 문항수(원본)"] = len(df_raw)
        # df_raw에 저작권/해설없음 1/0 유지된다면
        if "저작권" in df_raw.columns:
            kpis["저작권 문항수(원본)"] = int(df_raw["저작권"].sum())
        if "해설없는문항" in df_raw.columns:
            kpis["해설없는 문항수(원본)"] = int(df_raw["해설없는문항"].sum())

    kpis["분석대상 문항수(제외 후)"] = len(df_use)
    kpis["선택조건기준 문항수"] = len(df_filtered)
    return kpis

def render_kpis(kpis: dict):
    cols = st.columns(len(kpis))
    for col, (k, v) in zip(cols, kpis.items()):
        col.metric(k, f"{v:,}")
