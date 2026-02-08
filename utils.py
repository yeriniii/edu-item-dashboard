import pandas as pd
import streamlit as st

# ====== 컬럼명(엑셀 헤더와 100% 동일해야 함) ======
COL_KEY = "문항번호"
COL_GRADE = "전문항학년"
COL_SUBJECT = "전문항과목"
COL_DIFF = "난이도2"
COL_TYPE = "유형2"
COL_STD = "성취기준"
COL_COPY = "저작권"          # 값이 '저작권'이면 제외
COL_NOEXPL = "해설없는문항"   # 값이 '해설없음'이면 제외

REQUIRED_COLS = [
    COL_KEY, COL_GRADE, COL_SUBJECT, COL_DIFF, COL_TYPE, COL_STD,
    COL_COPY, COL_NOEXPL
]

@st.cache_data(show_spinner="엑셀 읽는 중...")
def load_pri_excel(file_bytes: bytes, sheet_name: str = "PRI") -> pd.DataFrame:
    # 캐시 미스일 때만 찍힘
    print("✅ read_excel 실제 실행됨")

    df = pd.read_excel(file_bytes, sheet_name=sheet_name)

    missing = [c for c in REQUIRED_COLS if c not in df.columns]
    if missing:
        raise ValueError(
            f"필수 컬럼이 없어요: {missing}\n"
            f"현재 시트 컬럼: {list(df.columns)}"
        )

    return df

def make_usable_df(df_raw: pd.DataFrame) -> pd.DataFrame:
    """저작권 문항/해설없는 문항을 제외한 사용가능 df 반환."""
    copy_flag = df_raw[COL_COPY].fillna("").astype(str).str.strip()
    noexpl_flag = df_raw[COL_NOEXPL].fillna("").astype(str).str.strip()

    df_use = df_raw[(copy_flag != "저작권") & (noexpl_flag != "해설없음")].copy()
    return df_use
