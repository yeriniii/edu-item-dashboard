import streamlit as st
from utils import load_data_excel,make_usable_df
from dashboard.page import render_dashboard
import pandas as pd

st.set_page_config(page_title="대시보드", layout="wide")
st.title("📊 대시보드")

uploads = st.file_uploader("엑셀 업로드 (.xlsx) — 시트명은 data로 고정", type=["xlsx"],accept_multiple_files=True)
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
