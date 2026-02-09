import streamlit as st

def render_table(df):
    st.subheader("상세 데이터")
    st.dataframe(df, use_container_width=True)

    st.download_button(
        "필터 결과 CSV 다운로드",
        df.to_csv(index=False).encode("utf-8-sig"),
        file_name="filtered.csv",
        mime="text/csv"
    )
