import streamlit as st
from .filters import render_filters, apply_filters
from .kpi import compute_kpis, render_kpis
from .charts import render_charts
from .tables import render_table
from .std_top import render_std_top 
def render_dashboard(df_use, df_raw=None):
    # 1) 필터 UI
    filters = render_filters(df_use)

    # 2) 필터 적용 데이터
    df_f = apply_filters(df_use, filters)

    # 3) KPI는 공통상단
    kpis = compute_kpis(df_raw=df_raw, df_use=df_use, df_filtered=df_f)
    render_kpis(kpis)
    # 탭 분리
    tab1, tab2, tab3 = st.tabs(["📊 분포 차트", "📋 상세 표", "성취기준별"])

    with tab1:
        render_charts(df_f)

    #with tab2:
        #render_table(df_f)

    with tab3:
        render_std_top(df_f)