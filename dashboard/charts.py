import streamlit as st
import pandas as pd
import plotly.express as px
from .constants import DIFF_ORDER, TYPE_ORDER,SUB_ORDER


def bar_count_ratio(df, col, title, order=None, vertical=True, show_table=True):
    s = df[col].copy()

    # 순서 고정
    if order is not None:
        s = pd.Categorical(s, categories=order, ordered=True)

    vc = pd.Series(s).value_counts(sort=False).reset_index()
    vc.columns = [col, "문항개수"]
    vc["비율"] = (vc["문항개수"] / vc["문항개수"].sum() * 100).round(1)

    # ✅ 표 먼저(또는 원하면 아래로 내려도 됨)
    if show_table:
        st.dataframe(
            vc[[col, "문항개수", "비율"]],
            use_container_width=True,
            hide_index=True,
            column_config={
                "문항개수": st.column_config.NumberColumn(format="%,d"),
                "비율": st.column_config.NumberColumn(format="%.1f%%"),
            },
            height=260 if len(vc) <= 12 else 420
        )

    # Plotly에서 text로 쓸 문자열
    text_pct = vc["비율"].astype(str) + "%"

    if vertical:
        # 세로 막대: 글자(카테고리) 가로 고정
        fig = px.bar(
            vc,
            x=col,
            y="문항개수",
            text=text_pct,
            title=title
        )
        fig.update_layout(
            xaxis_tickangle=0,              # 글자 가로
            yaxis=dict(title="문항개수",rangemode="tozero",tickformat=",")  # 0부터
        )
        fig.update_traces(
            hovertemplate=
            f"{col}: %{{x}}<br>"
            "문항개수: %{y:,}<br>"
            "비율: %{text}<extra></extra>"
        )
    else:
        # 가로 막대: 카테고리 길거나 많을 때 추천
        fig = px.bar(
            vc,
            x="문항개수",
            y=col,
            orientation="h",
            text=text_pct,
            title=title
        )
        fig.update_layout(
            xaxis=dict(title="문항개수",rangemode="tozero",tickformat=",")  # ✅ 0부터
        )
        fig.update_traces(
            hovertemplate=
            f"{col}: %{{y}}<br>"
            "문항개수: %{x:,}<br>"
            "비율: %{text}<extra></extra>"
        )

    st.plotly_chart(fig, use_container_width=True)


def render_charts(df):
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("난이도 분포")
        bar_count_ratio(df, col="난이도", title="난이도 분포",order=DIFF_ORDER, vertical=True, show_table=True)

    with c2:
        st.subheader("유형 분포")
        bar_count_ratio(df, col="유형", title="유형 분포",order=TYPE_ORDER, vertical=True, show_table=True)

    st.subheader("학년 분포")
    bar_count_ratio(df, col="전문항학년", title="학년 분포",vertical=True, show_table=True)

    st.subheader("과목 분포")
    # 과목은 항목이 길고 많아서 세로막대면 글자 회전/겹침이 심함 → 가로막대 추천
    bar_count_ratio(df, col="전문항과목", title="과목 분포",order=SUB_ORDER,vertical=False, show_table=True)
