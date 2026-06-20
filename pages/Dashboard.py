import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import os # <--- เพิ่ม import นี้ครับ แก้ปัญหา NameError

# ฟังก์ชันโหลดข้อมูล - ใช้การอ่านไฟล์ตรงๆ เพื่อความสดของข้อมูล
def load_data():
    df = pd.read_csv("data.csv", encoding='utf-8-sig')
    perms_df = pd.read_csv("permissions.csv", encoding='utf-8-sig')
    targets_df = pd.read_csv("targets.csv", encoding='utf-8-sig')
    return df, perms_df, targets_df

st.title("📊 Dashboard สรุปผลสำหรับผู้บริหาร")

# ระบบตรวจสอบสิทธิ์
if "password_correct" not in st.session_state:
    st.session_state.password_correct = False

if not st.session_state.password_correct:
    pwd = st.text_input("รหัสผ่านผู้บริหาร:", type="password")
    if st.button("เข้าสู่ระบบ"):
        _, perms_df, _ = load_data()
        user_row = perms_df[perms_df['Password'].astype(str).str.strip() == str(pwd).strip()]
        if not user_row.empty:
            st.session_state.password_correct = True
            st.session_state.user_info = user_row.iloc[0]
            st.rerun()
        else:
            st.error("รหัสผ่านไม่ถูกต้อง")
else:
    # เมื่อ Login สำเร็จ
    try:
        # ใช้การโหลดข้อมูลแบบปกติ ไม่ใช้ @st.cache_data เพื่อให้ได้ข้อมูลล่าสุดเสมอ
        df, _, targets_df = load_data()
        user_info = st.session_state.user_info
        
        # ปุ่มรีเฟรชหน้าเว็บ (เป็นวิธีที่ง่ายที่สุดในการดึงข้อมูลใหม่จาก GitHub)
        if st.button("🔄 อัปเดตข้อมูลล่าสุด"):
            st.rerun()

        # กรองข้อมูลตามสิทธิ์
        access_list = str(user_info['WardAccess'])
        if access_list == "ALL":
            df_filtered = df
        else:
            allowed_wards = [w.strip() for w in access_list.split(',')]
            df_filtered = df[df['หน่วยงาน'].isin(allowed_wards)]
        
        # เลือกหน่วยงาน
        all_wards = ["ภาพรวมทั้งหมด"] + sorted(df_filtered['หน่วยงาน'].unique().tolist())
        selected_ward = st.selectbox("เลือกหน่วยงาน:", all_wards)
        df_display = df_filtered if selected_ward == "ภาพรวมทั้งหมด" else df_filtered[df_filtered['หน่วยงาน'] == selected_ward]
        
        # ส่วนแสดงผลกราฟ 3 ส่วน
        score_cols = df_display.select_dtypes(include=[np.number]).columns.drop('อายุผู้ประเมิน (ปี)', errors='ignore')

        # ส่วนที่ 1
        st.subheader("ส่วนที่ 1: ร้อยละจำนวนผู้ประเมิน (เทียบตามเป้าหมาย)")
        counts = df_display['หน่วยงาน'].value_counts().reset_index()
        counts.columns = ['หน่วยงาน', 'Count']
        progress_df = pd.merge(counts, targets_df, on='หน่วยงาน', how='left').fillna({'Target': 10})
        progress_df['Percent'] = (progress_df['Count'] / progress_df['Target'] * 100).clip(upper=100)
        chart1 = alt.Chart(progress_df).mark_bar().encode(x='หน่วยงาน', y=alt.Y('Percent', scale=alt.Scale(domain=[0, 100])))
        st.altair_chart(chart1, use_container_width=True)

        # ส่วนที่ 2
        st.subheader("ส่วนที่ 2: ร้อยละผลการประเมินภาพรวม")
        avg_data = (df_display[score_cols].mean() / 5 * 100).reset_index()
        avg_data.columns = ['หัวข้อ', 'Score']
        chart2 = alt.Chart(avg_data).mark_bar().encode(x=alt.X('Score', scale=alt.Scale(domain=[0, 100])), y='หัวข้อ')
        st.altair_chart(chart2, use_container_width=True)

        # ส่วนที่ 3
        st.subheader("ส่วนที่ 3: คะแนนเฉลี่ย (Mean) และ SD")
        stats = df_display[score_cols].agg(['mean', 'std']).round(2).T
        stats.columns = ['Mean', 'SD']
        stats['SD'] = stats['SD'].fillna(0)
        st.dataframe(stats, use_container_width=True)

        if st.button("ออกจากระบบ"):
            st.session_state.password_correct = False
            st.rerun()
            
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการโหลดข้อมูล: {e}")
