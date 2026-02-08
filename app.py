import streamlit as st
from utils import load_pri_excel,make_usable_df
from dashboard import render_dashboard

st.set_page_config(page_title="PRI 대시보드", layout="wide")
st.title("📊 PRI 대시보드")

uploaded = st.file_uploader("엑셀 업로드 (.xlsx) — 시트명은 PRI로 고정", type=["xlsx"])
if uploaded is None:
    st.info("엑셀 파일을 업로드하세요. (원본 데이터 시트 이름: PRI)")
    st.stop()

try:
    df_raw = load_pri_excel(uploaded.getvalue(), sheet_name="PRI")
    df_use = make_usable_df(df_raw)
except Exception as e:
    st.error(str(e))
    st.stop()

render_dashboard(df_use)
