import streamlit as st
import pandas as pd

COL_SCH = "학교"
COL_GRADE = "전문항학년"
COL_SUBJECT = "전문항과목"
COL_DIFF = "난이도"
COL_TYPE = "유형"

DIFF_ORDER = ["상", "중상", "중", "중하", "하"]
TYPE_ORDER = ["객관식", "주관식", "기타"]
SCH_LABEL = {
    "PRI": "초등",
    "JHS": "중등",
    "HSC": "고등",
}
def _options(df: pd.DataFrame, col: str):
    s = df[col].dropna().astype(str).str.strip()
    # 공백/NaN 문자열/0 제거
    s = s[~s.isin(["", "nan", "None", "0", "0.0"])]
    return sorted(s.unique().tolist())

def render_filters(df_use: pd.DataFrame):
    with st.sidebar:
        st.header("필터")

        # 1) 학교 (최상위)
        opt_sch = _options(df_use, COL_SCH)
        f_sch = st.multiselect("학교", opt_sch, key="f_school",format_func=lambda x: SCH_LABEL.get(x, x))

        # 학교 선택 반영한 임시 df
        df1 = df_use[df_use[COL_SCH].isin(f_sch)] if f_sch else df_use

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

    return {
        COL_SCH: f_sch,
        COL_GRADE: f_grade,
        COL_SUBJECT: f_subj,
        COL_DIFF: f_diff,
        COL_TYPE: f_type,
    }

def apply_filters(df: pd.DataFrame, f: dict):
    out = df
    for col, vals in f.items():
        if vals:
            out = out[out[col].isin(vals)]
    return out
