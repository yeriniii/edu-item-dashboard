import duckdb
import pandas as pd
import streamlit as st
import altair as alt

from utils import (
    COL_KEY, COL_GRADE, COL_SUBJECT, COL_DIFF, COL_TYPE, COL_STD,
    COL_COPY, COL_NOEXPL
)

# -----------------------------
# SQL helpers
# -----------------------------
def q_ident(name: str) -> str:
    name = str(name)
    return '"' + name.replace('"', '""') + '"'

def q_str(val) -> str:
    s = str(val)
    return "'" + s.replace("'", "''") + "'"

def options_from_df(df: pd.DataFrame, col: str) -> list[str]:
    s = df[col].dropna().astype(str)
    s = s[s.str.strip() != ""]
    return sorted(s.unique().tolist())

def build_where(filters: dict) -> str:
    parts = []
    for col, vals in filters.items():
        if not vals:
            continue
        in_list = ", ".join(q_str(v) for v in vals)
        parts.append(f"{q_ident(col)} IN ({in_list})")
    return ("WHERE " + " AND ".join(parts)) if parts else ""


# -----------------------------
# Dashboard
# -----------------------------
def render_dashboard(df: pd.DataFrame):
    con = duckdb.connect(database=":memory:")
    con.register("data", df)

    st.sidebar.header("필터")

    # ✅ 핵심 필터만: 학년/과목/난이도/유형
    opt_grade = options_from_df(df, COL_GRADE)
    opt_subject = options_from_df(df, COL_SUBJECT)
    opt_diff = options_from_df(df, COL_DIFF)
    opt_type = options_from_df(df, COL_TYPE)

    f_grade = st.sidebar.multiselect("학년", opt_grade)
    f_subject = st.sidebar.multiselect("과목", opt_subject)
    f_diff = st.sidebar.multiselect("난이도", opt_diff)
    f_type = st.sidebar.multiselect("유형", opt_type)

    # 계약/검토 관점에서 유용한 토글(필터)
    exclude_copyright = st.sidebar.checkbox("저작권 문항 제외", value=True)
    only_with_expl = st.sidebar.checkbox(
    "해설 있는 문항만 보기", value=True
)

    # 성취기준 Top에서만 쓸 옵션
    top_n = st.sidebar.slider("성취기준 Top N", 5, 50, 20)

    filters = {
        COL_GRADE: f_grade,
        COL_SUBJECT: f_subject,
        COL_DIFF: f_diff,
        COL_TYPE: f_type,
    }
    where_sql = build_where(filters)

    # 토글 조건 추가
    extra_parts = []
    if exclude_copyright:
        extra_parts.append(f"{q_ident(COL_COPY)} <> '저작권' OR {q_ident(COL_COPY)} IS NULL")
    if only_with_expl:
        extra_parts.append(
            f"{q_ident(COL_NOEXPL)} <> '해설없음' OR {q_ident(COL_NOEXPL)} IS NULL"
    )

    if extra_parts:
        if where_sql:
            where_sql = where_sql + " AND " + " AND ".join(extra_parts)
        else:
            where_sql = "WHERE " + " AND ".join(extra_parts)

    metric = f"COUNT(DISTINCT {q_ident(COL_KEY)})"

    # -----------------------------
    # KPI (요약)
    # -----------------------------
    
# 표준화된 조건 (공백/NULL 안전)
    copy_is_bad = f"COALESCE(TRIM(CAST({q_ident(COL_COPY)} AS VARCHAR)), '') = '저작권'"
    noexpl_is_bad = f"COALESCE(TRIM(CAST({q_ident(COL_NOEXPL)} AS VARCHAR)), '') = '해설없음'"

    metric = f"COUNT(DISTINCT {q_ident(COL_KEY)})"
    total = con.execute(f"SELECT {metric} FROM data").fetchone()[0]
    # 1) 필터 적용 문항수
    kpi_filtered = con.execute(f"""
    SELECT {metric} FROM data
    {where_sql}
    """).fetchone()[0]

    # 2) 필터 내 저작권 문제 문항수
    kpi_copy = con.execute(f"""
    SELECT {metric} FROM data
    {where_sql}
    AND {copy_is_bad}
    """ if where_sql else f"""
    SELECT {metric} FROM data
    WHERE {copy_is_bad}
    """).fetchone()[0]

   # 전체 기준 해설 없는 문항수
    kpi_noex = con.execute(f"""
        SELECT {metric} FROM data
        WHERE {noexpl_is_bad}
    """).fetchone()[0]

    # 4) 필터 내 사용가능 문항수 (저작권X & 해설있음)
    kpi_usable = con.execute(f"""
    SELECT {metric} FROM data
    {where_sql}
    AND NOT ({copy_is_bad})
    AND NOT ({noexpl_is_bad})
    """ if where_sql else f"""
    SELECT {metric} FROM data
    WHERE NOT ({copy_is_bad})
        AND NOT ({noexpl_is_bad})
    """).fetchone()[0]

    # 화면 표시
    c1, c2, c3 = st.columns(3)
    c1.metric("전체 문항수", f"{total:,}")
    c2.metric("선택 조건 문항수", f"{kpi_filtered:,}")
    #c2.metric("저작권 문제", f"{kpi_copy:,}")
    #c3.metric("해설 없음", f"{kpi_noex:,}")
    c3.metric("비율", f"{(kpi_filtered / total * 100 if total else 0):.1f}%")
    #c4.metric("사용가능(저작권X·해설있음)", f"{kpi_usable:,}")
    # -----------------------------
    # Tabs: 요약/교차표/성취기준Top
    # -----------------------------
    tab1, tab2, tab3, tab4 = st.tabs([
        "과목/학년/난이도 차트",
        "교차표: 학년×과목",
        "교차표: 과목×난이도",
        "성취기준 Top"
    ])

    # 공통 집계 함수
    def agg_count(dim_col: str, alias: str):
        q = f"""
        SELECT {q_ident(dim_col)} AS {alias}, {metric} AS 문항수
        FROM data
        {where_sql}
        GROUP BY 1
        ORDER BY 2 DESC
        """
        return con.execute(q).df()

    with tab1:
        st.subheader("한눈에 보기(막대 차트)")

        colA, colB = st.columns(2)
        with colA:
            st.markdown("### 과목별")
            res = agg_count(COL_SUBJECT, "과목")
            st.dataframe(res, use_container_width=True, height=260)
            if not res.empty:
                st.bar_chart(res.set_index("과목")["문항수"])

        with colB:
            st.markdown("### 학년별")
            res = agg_count(COL_GRADE, "학년")
            st.dataframe(res, use_container_width=True, height=260)
            if not res.empty:
                st.bar_chart(res.set_index("학년")["문항수"])

        st.markdown("### 난이도별")
        res = agg_count(COL_DIFF, "난이도")
        st.dataframe(res, use_container_width=True, height=260)
        if not res.empty:
            st.bar_chart(res.set_index("난이도")["문항수"])

    with tab2:
        st.subheader("교차표: 학년 × 과목 (히트맵)")
        q = f"""
        SELECT
          {q_ident(COL_GRADE)} AS 학년,
          {q_ident(COL_SUBJECT)} AS 과목,
          {metric} AS 문항수
        FROM data
        {where_sql}
        GROUP BY 1,2
        """
        long_df = con.execute(q).df()

        if long_df.empty:
            st.info("선택 조건에서 데이터가 없어요.")
        else:
            heat = (
                alt.Chart(long_df)
                .mark_rect()
                .encode(
                    x=alt.X("과목:N", sort="-y"),
                    y=alt.Y("학년:N"),
                    color=alt.Color("문항수:Q"),
                    tooltip=["학년", "과목", "문항수"]
                )
                .properties(height=420)
            )
            st.altair_chart(heat, use_container_width=True)

    with tab3:
        st.subheader("교차표: 과목 × 난이도 (히트맵)")
        q = f"""
        SELECT
          {q_ident(COL_SUBJECT)} AS 과목,
          {q_ident(COL_DIFF)} AS 난이도,
          {metric} AS 문항수
        FROM data
        {where_sql}
        GROUP BY 1,2
        """
        long_df = con.execute(q).df()

        if long_df.empty:
            st.info("선택 조건에서 데이터가 없어요.")
        else:
            heat = (
                alt.Chart(long_df)
                .mark_rect()
                .encode(
                    x=alt.X("난이도:N"),
                    y=alt.Y("과목:N", sort="-x"),
                    color=alt.Color("문항수:Q"),
                    tooltip=["과목", "난이도", "문항수"]
                )
                .properties(height=520)
            )
            st.altair_chart(heat, use_container_width=True)

    with tab4:
        st.subheader("성취기준 Top")
        q = f"""
        SELECT {q_ident(COL_STD)} AS 성취기준, {metric} AS 문항수
        FROM data
        {where_sql}
        GROUP BY 1
        ORDER BY 2 DESC
        LIMIT {int(top_n)}
        """
        res = con.execute(q).df()
        st.dataframe(res, use_container_width=True)
        if not res.empty:
            st.bar_chart(res.set_index("성취기준")["문항수"])
