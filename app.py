import streamlit as st
from utils import load_data_excel,make_usable_df
from dashboard.page import render_dashboard
import pandas as pd

st.set_page_config(page_title="대시보드", layout="wide")
st.title("📊 대시보드")

# 엑셀 업로드: 업로드 후에는 접어두고, 필요할 때만 펼쳐서 확인/변경
if "excel_upload_count" not in st.session_state:
    st.session_state.excel_upload_count = 0
if "excel_expanded" not in st.session_state:
    st.session_state.excel_expanded = True

excel_count = st.session_state.excel_upload_count
label = f"📁 엑셀 파일 ({excel_count}개)" if excel_count > 0 else "📁 엑셀 업로드"
expanded = st.session_state.excel_expanded

with st.expander(label, expanded=expanded):
    uploads = st.file_uploader("엑셀 업로드 (.xlsx) — 시트명은 data로 고정", type=["xlsx"], accept_multiple_files=True)

if uploads:
    st.session_state.excel_upload_count = len(uploads)
    st.session_state.excel_expanded = False
else:
    st.session_state.excel_upload_count = 0
    st.session_state.excel_expanded = True

if not uploads:
    st.info("엑셀파일을 1개 이상 업로드하세요. (시트 이름: data)")
    st.stop()

try:
    dfs=[]
    for f in uploads:
        df=load_data_excel(f.getvalue(),sheet_name="data")
        dfs.append(df)

    df_raw = pd.concat(dfs, ignore_index=True)
    df_use = make_usable_df(df_raw)

except Exception as e:
    st.error(str(e))
    st.stop()

render_dashboard(df_use)
