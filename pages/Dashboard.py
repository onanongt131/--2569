import streamlit as st
import pandas as pd
import numpy as np
import os
import altair as alt

st.set_page_config(layout="wide")

@st.cache_data(ttl=60)
def load_data():
    base_dir = os.path.dirname(os.path.dirname(__file__))
    df = pd.read_csv(os.path.join(base_dir, "data.csv"), encoding='utf-8-sig')
    perms_df = pd.read_csv(os.path.join(base_dir, "permissions.csv"), encoding='utf-8-sig')
    targets_df = pd.read_csv(os.path.join(base_dir, "targets.csv"), encoding='utf-8-sig')
    return df, perms_df, targets_df

st.title("📊 Dashboard สรุปผลการประเมินพยาบาล")

try:
    df, perms_df, targets_df = load_data()
    pwd = st.sidebar.text_input("รหัสผ่านผู้บริหาร:", type="password")

    if pwd:
        user_row = perms_df[perms_df['Password'].astype(str).str.strip() == str(pwd).strip()]
        
        if not user_row.empty:
            access_list = str(user_row.iloc[0]['WardAccess'])
            if access_list != "ALL":
                allowed_wards = [w.strip() for w in access_list.split(',')]
                df = df[df['หน่วยงาน'].astype(str).str.strip().isin(allowed_wards)]

            if df.empty:
                st.warning("ไม่พบข้อมูลการประเมินสำหรับหน่วยงานที่คุณดูแล")
            else:
                st.sidebar.markdown("---")
                all_wards = ["ภาพรวมทั้งหมด"] + sorted(df['หน่วยงาน'].unique().tolist())
                selected_ward = st.sidebar.selectbox("เลือกหน่วยงาน:", all_wards)
                
                df_display = df[df['หน่วยงาน'] == selected_ward] if selected_ward != "ภาพรวมทั้งหมด" else df
                score_cols = df_display.select_dtypes(include=[np.number]).columns.
