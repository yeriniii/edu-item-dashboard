import streamlit as st
import duckdb
import plotly.express as px

COL_KEY = "문항번호"
COL_STD = "성취기준"

def render_std_top(df_filtered):
    st.subheader("성취기준 Top")

    top_n = st.slider("성취기준 Top N", 5, 50, 20)

    # ✅ 필터된 df만 DuckDB에 등록
    con = duckdb.connect(database=":memory:")
    con.register("data", df_filtered)

    q = f"""
    SELECT
      "{COL_STD}" AS 성취기준,
      COUNT(DISTINCT "{COL_KEY}") AS 문항개수
    FROM data
    WHERE COALESCE(TRIM(CAST("{COL_STD}" AS VARCHAR)), '') <> ''
    GROUP BY 1
    ORDER BY 2 DESC
    LIMIT {int(top_n)}
    """
    res = con.execute(q).df()

    st.dataframe(res, use_container_width=True)

    # ---- 표(한눈에) ----
    if res.empty:
        st.info("선택 조건에서 성취기준 데이터가 없어요.")
        return

    # 비율 컬럼 추가
    total = int(res["문항개수"].sum())
    res["비율"] = (res["문항개수"] / total * 100).round(1)

    # 보기 좋은 컬럼 순서
    res_view = res[["성취기준", "문항개수", "비율"]].copy()
    st.dataframe(
        res_view,
        use_container_width=True,
        column_config={
            "문항개수": st.column_config.NumberColumn(format="%,d"),
            "비율": st.column_config.NumberColumn(format="%.1f%%"),
        },
        hide_index=True
    )

    # ---- 차트(가로막대: 라벨이 길어도 읽기 좋음) ----
    fig = px.bar(
        res,
        x="문항개수",
        y="성취기준",
        orientation="h",
        text=res["비율"].astype(str) + "%",
        title="성취기준 Top"
    )

    # ✅ 0부터 고정 + k 제거 + 축이름
    fig.update_layout(
        xaxis=dict(
            title="문항개수",
            rangemode="tozero",
            tickformat=","   # k 제거
        ),
        yaxis=dict(
            title="",  # 성취기준은 이미 y축 라벨이라 제목 비움
        )
    )

    # ✅ hover 텍스트 커스터마이즈
    fig.update_traces(
        hovertemplate=
        "성취기준: %{y}<br>"
        "문항개수: %{x:,}<br>"
        "비율: %{text}<extra></extra>"
    )

    st.plotly_chart(fig, use_container_width=True)