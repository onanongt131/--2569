import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

@st.cache_data(ttl=60)
def load_data():
    sheet_url = "https://docs.google.com/spreadsheets/d/1U0bVw8G5jyMDwR6ohaqrU6k5KRwEhYIcCENMyoZoyyw/export?format=csv"
    df = pd.read_csv(sheet_url, encoding='utf-8-sig')
    perms_df = pd.read_csv("permissions.csv", encoding='utf-8-sig')
    return df, perms_df

st.title("📊 Dashboard สรุปผลสำหรับผู้บริหาร")

# ระบบ Login
if "password_correct" not in st.session_state:
    st.session_state.password_correct = False

if not st.session_state.password_correct:
    pwd = st.text_input("รหัสผ่านผู้บริหาร:", type="password")
    if st.button("เข้าสู่ระบบ"):
        _, perms_df = load_data()
        user_row = perms_df[perms_df['Password'].astype(str).str.strip() == str(pwd).strip()]
        if not user_row.empty:
            st.session_state.password_correct = True
            st.session_state.user_info = user_row.iloc[0]
            st.rerun()
        else:
            st.error("รหัสผ่านไม่ถูกต้อง")
else:
    try:
        df, _ = load_data()
        user_info = st.session_state.user_info
        access_list = str(user_info['WardAccess'])

        # 1. กำหนดตัวแปร df_filtered ให้ปลอดภัย (ทำนอก if-else)
        # 1. กำหนดตัวเลือก (เพิ่ม "กลุ่มงานทั้งหมด" เข้าไปสำหรับหัวหน้ากลุ่ม)
        if access_list != "ALL":
            all_wards = ["กลุ่มงานทั้งหมด"] + sorted(allowed_wards)
        
        # 2. เลือกหน่วยงาน
        selected_ward = st.selectbox("เลือกดูข้อมูล:", all_wards, key='selected_ward')
        
        # 3. เตรียมข้อมูล (df_display) และเป้าหมาย (display_target)
        if selected_ward == "กลุ่มงานทั้งหมด":
            df_display = df_filtered
            # รวมเป้าหมายของทุกหน่วยงานในกลุ่ม (สมมติว่าใช้ sum ของ target_map)
            display_target = sum([target_map.get(w, 10) for w in allowed_wards])
        else:
            df_display = df_filtered[df_filtered['หน่วยงาน'] == selected_ward]
            display_target = target_map.get(selected_ward, 10)

        # 4. แสดงผลส่วนที่ 1
        st.subheader("ส่วนที่ 1: ร้อยละจำนวนผู้ประเมิน")
        
        # กราฟเปรียบเทียบรายหน่วยงาน (กรณีดู "กลุ่มงานทั้งหมด")
        if selected_ward == "กลุ่มงานทั้งหมด":
            counts = df_display['หน่วยงาน'].value_counts().reset_index()
            counts.columns = ['หน่วยงาน', 'Count']
            chart1 = alt.Chart(counts).mark_bar().encode(
                x='หน่วยงาน', y='Count', color='หน่วยงาน'
            )
            st.altair_chart(chart1, use_container_width=True)
            
        # Metric
        total_count = int(df_display.shape[0])
        total_percent = (total_count / display_target * 100) if display_target > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        col1.metric("จำนวนรวม", f"{total_count} คน")
        col2.metric("เป้าหมายรวม", f"{display_target} คน")
        col3.metric("ร้อยละความสำเร็จ", f"{total_percent:.1f}%")

        # ส่วนที่ 2
        st.subheader("ส่วนที่ 2: ผลการประเมินภาพรวม")
        avg_data = (df_display[score_cols].mean() / 5 * 100).reset_index()
        avg_data.columns = ['หัวข้อ', 'Score']
        chart2 = alt.Chart(avg_data).mark_bar().encode(x=alt.X('Score', scale=alt.Scale(domain=[0, 100])), y='หัวข้อ')
        st.altair_chart(chart2, use_container_width=True)

        # ส่วนที่ 3
        st.subheader("ส่วนที่ 3: คะแนนเฉลี่ย (Mean) และ SD")
        stats = df_display[score_cols].agg(['mean', 'std']).round(2).T
        st.dataframe(stats, use_container_width=True)

        if st.button("ออกจากระบบ"):
            st.session_state.password_correct = False
            st.rerun()

    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการโหลดข้อมูล: {e}")
