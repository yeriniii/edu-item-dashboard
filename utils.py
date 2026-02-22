import pandas as pd
import streamlit as st

# ====== 컬럼명(엑셀 헤더와 100% 동일해야 함) ======
COL_KEY = "문항번호"
COL_SCH="학교"
COL_GRADE = "전문항학년"
COL_SUBJECT = "전문항과목"
COL_DIFF = "난이도"
COL_TYPE = "유형"
COL_STD = "성취기준"
COL_COPY = "저작권"          # 1/0
COL_NOEXPL = "해설없는문항" # 1/0
COL_SCH_LVL = "학교급"

REQUIRED_COLS = [
    COL_KEY, COL_SCH, COL_GRADE, COL_SUBJECT, COL_DIFF, COL_TYPE, COL_STD,
    COL_COPY, COL_NOEXPL
]

@st.cache_data(show_spinner="엑셀 읽는 중...")
def load_data_excel(file_bytes: bytes, sheet_name: str = "data") -> pd.DataFrame:
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


@st.cache_data(show_spinner="데이터 전처리 중...")
def make_usable_df(df_raw: pd.DataFrame) -> pd.DataFrame:

    df=df_raw.copy()
    # 1) 저작권/해설없는문항 플래그(1/0) 정리 + 제외
    df[COL_COPY] = pd.to_numeric(df[COL_COPY], errors="coerce").fillna(0).astype(int)
    df[COL_NOEXPL] = pd.to_numeric(df[COL_NOEXPL], errors="coerce").fillna(0).astype(int)
    df = df[(df[COL_COPY] == 0) & (df[COL_NOEXPL] == 0)].copy()

    # 2) 유형 코드 -> 라벨 (34 제외, 나머지는 기타)
    df[COL_TYPE] = pd.to_numeric(df[COL_TYPE], errors="coerce")
    df = df[df[COL_TYPE] != 34].copy()

    type_map = {21: "객관식", 31: "주관식"}
    df[COL_TYPE] = df[COL_TYPE].map(type_map).fillna("기타")

    # 3) 난이도 코드 -> 라벨 (맵 없는 건 제외)
    df[COL_DIFF] = pd.to_numeric(df[COL_DIFF], errors="coerce")
    diff_map = {2: "상", 3: "중", 4: "하", 6: "중상", 7: "중하"}
    df = df[df[COL_DIFF].isin(diff_map.keys())].copy()
    df[COL_DIFF] = df[COL_DIFF].map(diff_map)
    
    # 4) 과목 이상값 정리 (0/빈값 제거)
    df[COL_SUBJECT] = df[COL_SUBJECT].astype(str).str.strip()
    df.loc[df[COL_SUBJECT].isin(["", "nan", "None", "0", "0.0"]), COL_SUBJECT] = pd.NA
    df = df[df[COL_SUBJECT].notna()].copy()

    school_map = {"PRI": "초등", "JHS": "중등", "HSC": "고등"}
    order = ["초등", "중등", "고등"]

    df[COL_SCH_LVL] = df[COL_SCH].map(school_map)
    df[COL_SCH_LVL] = pd.Categorical(df[COL_SCH_LVL], categories=order, ordered=True)

    return df
