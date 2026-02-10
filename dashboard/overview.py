import streamlit as st
import pandas as pd
import plotly.express as px
from .constants import DIFF_ORDER
from utils import COL_TYPE, COL_DIFF

order = ["초등", "중등", "고등"]
COL_SCH_LVL = "학교급"
@st.cache_data(show_spinner=False)
def render_overview(df: pd.DataFrame):
    #초/중/고 정렬
    df_ov = df.copy()

    df_ov[COL_SCH_LVL] = pd.Categorical(
        df_ov[COL_SCH_LVL],
        categories=order,
        ordered=True
    )

    # 1) 학교급별 문항수
    c1, c2 = st.columns([1, 1])

    with c1:
        sch_counts = (
            df_ov
            .groupby(COL_SCH_LVL)
            .size()
            .reindex(order)
            .reset_index(name="문항수")
        )
        fig = px.bar(sch_counts, x="학교급", y="문항수", text="문항수")
        fig.update_traces(textposition="outside", cliponaxis=False)
        fig.update_xaxes(categoryorder="array", categoryarray=order)
        fig.update_layout(margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig, use_container_width=True)

    # 2) 학교급별 유형 비율 (100% 누적)
    with c2:
        ct = (
        pd.crosstab(df_ov[COL_SCH_LVL], df_ov[COL_TYPE])
        .reindex(order)
    )
        pct = ct.div(ct.sum(axis=1), axis=0).fillna(0)

        long = (
            pct.reset_index()
               .melt(id_vars=COL_SCH_LVL, var_name="유형", value_name="비율")
        )
        fig2 = px.bar(long, x=COL_SCH_LVL, y="비율", color="유형", barmode="stack")
        fig2.update_xaxes(categoryorder="array", categoryarray=order)
        fig2.update_layout(yaxis_tickformat=".0%", margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig2, use_container_width=True)

    c3, c4 = st.columns([1, 1])

    with c3:
        ct_d = pd.crosstab(df_ov[COL_SCH_LVL], df_ov[COL_DIFF]).reindex(order)
        ct_d = ct_d.reindex(columns=[d for d in DIFF_ORDER if d in ct_d.columns])
        pct_d = ct_d.div(ct_d.sum(axis=1), axis=0).fillna(0)

        long_d = (
            pct_d.reset_index()
                 .melt(id_vars=COL_SCH_LVL, var_name="난이도", value_name="비율")
        )

        fig3 = px.bar(long_d, x=COL_SCH_LVL, y="비율", color="난이도", barmode="stack")
        fig3.update_layout(title="학교급별 난이도 비율", yaxis_tickformat=".0%", margin=dict(l=10, r=10, t=40, b=10))
        fig3.update_layout(legend_traceorder="normal")
        fig3.update_xaxes(categoryorder="array", categoryarray=order)
        st.plotly_chart(fig3, use_container_width=True)

    with c4:
        st.subheader("전체 요약 KPI")

        total_n = len(df_ov)
        mid_up = df_ov[COL_DIFF].isin(["상", "중상", "중"]).mean() * 100
        obj_rate = (df_ov[COL_TYPE] == "객관식").mean() * 100

        k1, k2, k3 = st.columns(3)

        k1.metric("전체 문항수", f"{total_n:,}")
        k2.metric("중 이상 비율", f"{mid_up:.1f}%")
        k3.metric("객관식 비율", f"{obj_rate:.1f}%")

        st.caption("※ 전체 기준 요약 (필터 미적용)")


    # 3) 학교급 요약표 (문항수 + 유형% + 난이도%)
    st.caption("학교급별 요약 (문항수/유형비율/난이도비율)")

    n = (
        df_ov
        .groupby(COL_SCH_LVL)
        .size()
        .reindex(order)
        .rename("문항수")
    )

    type_pct = pd.crosstab(df_ov[COL_SCH_LVL], df_ov[COL_TYPE], normalize="index").reindex(order).add_prefix("유형_")
    diff_pct = pd.crosstab(df_ov[COL_SCH_LVL], df_ov[COL_DIFF], normalize="index").reindex(order).add_prefix("난이도_")

    summary = pd.concat([n, type_pct, diff_pct], axis=1).reset_index()

    # 보기 좋게 퍼센트 컬럼만 %로 표시하고 싶으면 st.dataframe은 그대로 두고,
    # 표시용으로 round만 해도 충분함
    pct_cols = [c for c in summary.columns if c.startswith("유형_") or c.startswith("난이도_")]
    summary[pct_cols] = summary[pct_cols].round(4)

    st.dataframe(summary, use_container_width=True)
