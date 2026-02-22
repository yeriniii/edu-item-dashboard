import streamlit as st
import pandas as pd
from .constants import DIFF_ORDER, TYPE_ORDER, SUB_ORDER

COL_SCH = "학교"
COL_GRADE = "전문항학년"
COL_SUBJECT = "전문항과목"
COL_DIFF = "난이도"
COL_TYPE = "유형"
COL_SCH_LVL = "학교급"

# 22분류 필터: 이 5개 컬럼이 모두 있는 문항만 남김
COLS_22 = ["22분류1", "22분류2", "22분류3", "22분류4", "22분류5"]

# DIFF_ORDER = ["상", "중상", "중", "중하", "하"]
# TYPE_ORDER = ["객관식", "주관식", "기타"]
SCH_LABEL = {
    "PRI": "초등",
    "JHS": "중등",
    "HSC": "고등",
}
def _options(df: pd.DataFrame, col: str):
    s = df[col].dropna().astype(str).str.strip()
    # 공백/NaN 문자열/0 제거
    s = s[~s.isin(["", "nan", "None", "0", "0.0"])]
    unique = s.unique().tolist()
    # 과목: SUB_ORDER 순서로 정렬, 없는 과목은 뒤에
    if col == COL_SUBJECT:
        in_order = [v for v in SUB_ORDER if v in unique]
        extra = sorted([v for v in unique if v not in SUB_ORDER])
        return in_order + extra
    return sorted(unique)

def render_filters(df_use: pd.DataFrame):
    with st.sidebar:
        st.header("필터")

        # 1) 학교 (최상위)
        opt_sch = _options(df_use, COL_SCH_LVL)
        f_sch = st.multiselect("학교", opt_sch, key="f_school")

        # 학교 선택 반영한 임시 df
        df1 = df_use[df_use[COL_SCH_LVL].isin(f_sch)] if f_sch else df_use

        # 2) 학년 (학교에 따라 옵션이 달라짐)
        opt_grade = _options(df1, COL_GRADE)
        f_grade = st.multiselect("학년", opt_grade, key="f_grade")

        df2 = df1[df1[COL_GRADE].isin(f_grade)] if f_grade else df1

        # 3) 과목 (학교+학년에 따라 옵션이 달라짐)
        opt_subj = _options(df2, COL_SUBJECT)
        f_subj = st.multiselect("과목", opt_subj, key="f_subject")

        df3 = df2[df2[COL_SUBJECT].isin(f_subj)] if f_subj else df2

        # 4) 난이도 (상위 필터 반영)
        # 순서 고정 + 현재 데이터에 있는 값만
        opt_diff = [d for d in DIFF_ORDER if d in set(df3[COL_DIFF].dropna().astype(str))]
        f_diff = st.multiselect("난이도", opt_diff, key="f_diff")

        df4 = df3[df3[COL_DIFF].isin(f_diff)] if f_diff else df3

        # 5) 유형 (상위 필터 반영)
        opt_type = [t for t in TYPE_ORDER if t in set(df4[COL_TYPE].dropna().astype(str))]
        f_type = st.multiselect("유형", opt_type, key="f_type")

        # 6) 22분류 있는 문항만 (체크박스)
        has_22_cols = all(c in df_use.columns for c in COLS_22)
        f_only_22 = False
        if has_22_cols:
            f_only_22 = st.checkbox("22분류 있는 문항만", key="f_only_22", help="22분류가 완전히 된 문항만 표시")

    return {
        COL_SCH_LVL: f_sch,
        COL_GRADE: f_grade,
        COL_SUBJECT: f_subj,
        COL_DIFF: f_diff,
        COL_TYPE: f_type,
        "only_22": f_only_22 if has_22_cols else False,
    }

# 적용된 필터를 한눈에 보여주는 라벨 (한글)
FILTER_LABELS = {
    COL_SCH_LVL: "학교",
    COL_GRADE: "학년",
    COL_SUBJECT: "과목",
    COL_DIFF: "난이도",
    COL_TYPE: "유형",
    "only_22": "22분류 있는 문항만",
}


def _filter_summary_parts(filters: dict):
    """적용된 필터만 (라벨, 텍스트) 리스트로 반환. HTML/마크다운 없음."""
    parts = []
    for key, val in filters.items():
        label = FILTER_LABELS.get(key, key)
        if key == "only_22":
            if val:
                parts.append((label, "✓"))
            continue
        if val:
            if isinstance(val, (list, tuple)):
                text = ", ".join(str(v) for v in val)
            else:
                text = str(val)
            parts.append((label, text))
    return parts


def render_filter_summary(filters: dict):
    """적용 중인 필터를 상단에 요약해서 표시."""
    import html
    parts = _filter_summary_parts(filters)
    if not parts:
        return
    # 선택된 값만 쓸 색 (원하면 바꿔서 써. 예: #059669 초록)
    value_color = "#2563eb"
    st.markdown("---")
    st.caption("📋 적용 중인 필터")
    # 라벨(학교, 학년 등)은 기본 색, 값(중등, 국어, 2학년 등)만 value_color
    line = " · ".join(
        f"<strong>{html.escape(p[0])}</strong> <span style='color:{value_color}; font-weight:600;'>{html.escape(p[1])}</span>"
        for p in parts
    )
    st.markdown(f"<p style='margin: 0.25rem 0;'>{line}</p>", unsafe_allow_html=True)
    st.markdown("---")

def apply_filters(df: pd.DataFrame, f: dict):
    out = df
    for col, vals in f.items():
        if col == "only_22":
            if vals and all(c in out.columns for c in COLS_22):
                # 22분류1~5 모두 값이 있는 행만 (비어있거나 nan/0 등 제외)
                mask = pd.Series(True, index=out.index)
                for c in COLS_22:
                    s = out[c].astype(str).str.strip()
                    mask &= s.notna() & ~s.isin(["", "nan", "None", "0", "0.0"])
                out = out[mask]
            continue
        if vals:
            out = out[out[col].isin(vals)]
    return out
