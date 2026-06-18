import streamlit as st
import pandas as pd
import numpy as np
import os

st.set_page_config(layout="wide")

@st.cache_data(ttl=60)
def load_data():
    base_dir = os.path.dirname(os.path.dirname(__file__))
    data_path = os.path.join(base_dir, "data.csv")
    perm_path = os.path.join(base_dir, "permissions.csv")
    df = pd.read_csv(data_path, encoding='utf-8-sig')
    perms_df = pd.read_csv(perm_path, encoding='utf-8-sig')
    return df, perms_df

st.title("📊 Dashboard สรุปผลการประเมินพยาบาล")

try:
    df, perms_df = load_data()
    pwd = st.sidebar.text_input("รหัสผ่านผู้บริหาร:", type="password")

    if pwd:
        if 'Password' in perms_df.columns:
            user_row = perms_df[perms_df['Password'].astype(str).str.strip() == str(pwd).strip()]

            if not user_row.empty:
                access_list = str(user_row.iloc[0]['WardAccess'])
                
                # กรองข้อมูล
                if access_list != "ALL":
                    allowed_wards = [w.strip() for w in access_list.split(',')]
                    df = df[df['หน่วยงาน'].astype(str).str.strip().isin(allowed_wards)]

                if df.empty:
                    st.warning("ไม่พบข้อมูลการประเมินสำหรับหน่วยงานที่คุณดูแล")
                else:
                    # --- ส่วนของตัวเลือก Filter (ภาพรวม หรือ รายหน่วย) ---
                    st.sidebar.markdown("---")
                    all_wards = ["ภาพรวมทั้งหมด"] + sorted(df['หน่วยงาน'].unique().tolist())
                    selected_ward = st.sidebar.selectbox("เลือกหน่วยงานเพื่อดูรายละเอียด:", all_wards)
                    
                    # ใช้ df_display สำหรับแสดงผลกราฟ/ตาราง
                    if selected_ward != "ภาพรวมทั้งหมด":
                        df_display = df[df['หน่วยงาน'] == selected_ward]
                    else:
                        df_display = df

                    # กำหนดคอลัมน์คะแนน
                    score_cols = df_display.select_dtypes(include=[np.number]).columns.drop('อายุผู้ประเมิน (ปี)', errors='ignore')

                   # 1. ร้อยละจำนวนผู้ประเมิน
                    st.subheader("ส่วนที่ 1: ร้อยละจำนวนผู้ประเมิน")
                    progress = df_display['หน่วยงาน'].value_counts() / 50 * 100
                    st.bar_chart(progress)

                    # ส่วนที่ 2: ร้อยละผลการประเมินภาพรวม
                    st.subheader("ส่วนที่ 2: ร้อยละผลการประเมินภาพรวม")
                    avg_scores = df_display[score_cols].mean()
                    # เพิ่มพารามิเตอร์ y_min=0, y_max=100
                    st.bar_chart(avg_scores / 5 * 100, horizontal=True, y_min=0, y_max=100)

                    # 3. Mean & SD รายข้อ
                    st.subheader("ส่วนที่ 3: คะแนนเฉลี่ย (Mean) และ SD")
                    stats = df_display[score_cols].agg(['mean', 'std']).round(2).T
                    stats.columns = ['Mean', 'SD']
                    st.dataframe(stats, use_container_width=True)

                    # ดาวน์โหลด
                    csv = stats.to_csv().encode('utf-8-sig')
                    st.download_button("ดาวน์โหลดตารางสรุปผล (CSV)", csv, "summary.csv")

                    with st.expander("ดูข้อมูลดิบ"):
                        st.dataframe(df_display)
            else:
                st.error("รหัสผ่านไม่ถูกต้อง")
        else:
            st.error("ไม่พบหัวคอลัมน์ Password ในไฟล์ permissions.csv")
except Exception as e:
    st.error(f"เกิดข้อผิดพลาด: {e}")
