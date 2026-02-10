import streamlit as st
from .overview import render_overview
from .filters import render_filters, apply_filters
from .kpi import compute_kpis, render_kpis
from .charts import render_charts
from .std_top import render_std_top

def render_dashboard(df_use, df_raw=None):
    # ✅ 탭 대신 선택형 네비게이션 (선택값이 생겨서 조건 분기가 가능)
    mode = st.segmented_control(
        "보기",
        options=["📌 전체개요", "🔎 상세분석"],
        default="📌 전체개요",
    )
    # segmented_control이 없는 버전이면 아래로 대체:
    # mode = st.radio("보기", ["📌 전체개요", "🔎 상세분석"], horizontal=True)

    if mode == "📌 전체개요":
        # ✅ 사이드바: 안내만
        with st.sidebar:
            st.header("안내")
            st.info(
                "현재 화면은 **전체개요(고정)** 입니다.\n\n"
                "필터를 적용한 상세 분석은 **[🔎 상세분석]**에서 진행해주세요."
            )

        st.subheader("📌 전체 개요")
        render_overview(df_use)
        return

    # =========================
    # 🔎 상세분석 모드
    # =========================
    filters = render_filters(df_use)
    df_f = apply_filters(df_use, filters)

    kpis = compute_kpis(df_raw=df_raw, df_use=df_use, df_filtered=df_f)
    render_kpis(kpis)

    if not any(filters.values()):
        st.info("상세 분석은 필터를 1개 이상 선택하면 더 정확하게 보여줘요. (예: 학교/학년/과목)")
        return

    sub1, sub2 = st.tabs(["📊 분포 차트", "🎯 성취기준별"])
    with sub1:
        render_charts(df_f)
    with sub2:
        render_std_top(df_f)
