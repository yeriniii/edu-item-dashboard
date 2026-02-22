import streamlit as st
import numbers
def compute_kpis(df_raw, df_use, df_filtered):
    kpis = {}
    if df_raw is not None:
        kpis["전체 문항수(원본)"] = len(df_raw)
        # df_raw에 저작권/해설없음 1/0 유지된다면
        if "저작권" in df_raw.columns:
            kpis["저작권 문항수(원본)"] = int(df_raw["저작권"].sum())
        if "해설없는문항" in df_raw.columns:
            kpis["해설없는 문항수(원본)"] = int(df_raw["해설없는문항"].sum())

    kpis["전체 문항수(해설없음, 저작권 문항 제외 후)"] = len(df_use)
    kpis["필터기준 문항수"] = len(df_filtered)
    ratio = (len(df_filtered) / len(df_use) * 100) if len(df_use) else 0
    kpis["필터기준 비율(%)"] = ratio
    return kpis

def render_kpis(kpis: dict):
    cols = st.columns(len(kpis))
    for col, (k, v) in zip(cols, kpis.items()):
        if isinstance(v, numbers.Number):
            if "(%)" in k:
                col.metric(k, f"{v:.1f}%")
            else:
                col.metric(k, f"{v:,}")
        else:
            col.metric(k, str(v))
