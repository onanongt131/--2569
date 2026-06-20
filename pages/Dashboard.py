import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import os # <--- เพิ่ม import นี้ครับ แก้ปัญหา NameError

# ฟังก์ชันโหลดข้อมูล - ใช้การอ่านไฟล์ตรงๆ เพื่อความสดของข้อมูล
# แก้ไขฟังก์ชัน load_data เป็นแบบนี้ครับ
@st.cache_data(ttl=60)
def load_data():
    # เปลี่ยนจากการอ่านไฟล์ data.csv มาเป็น URL ของ Google Sheets
    sheet_url = "https://docs.google.com/spreadsheets/d/1U0bVw8G5jyMDwR6ohaqrU6k5KRwEhYIcCENMyoZoyyw/export?format=csv"
    df = pd.read_csv(sheet_url, encoding='utf-8-sig')
    
    # หมายเหตุ: สำหรับ permissions.csv และ targets.csv 
    # หากคุณยังเก็บไว้ใน GitHub เหมือนเดิม ก็สามารถอ่านด้วยวิธีปกติได้ครับ
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
        # ส่วนที่ 1: ร้อยละตามเป้าหมาย
        st.subheader("ส่วนที่ 1: ร้อยละจำนวนผู้ประเมิน (เทียบตามเป้าหมาย)")
        
        target_map = {
            "กุมารเวชกรรม 1": 10, "กุมารเวชกรรม 2": 10, "งานเวชศาสตร์ใต้น้ำ": 5, "งานไตเทียม HD/CAPD": 10,
            "น้อมเกล้า 2": 10, "น้อมเกล้า 3": 10, "น้อมเกล้า 4": 10, "นรีเวชกรรม": 10,
            "พิเศษอายุรกรรม 5": 10, "พิเศษอายุรกรรม 7": 10, "รติพัฒน์": 10, "รส.200 ปี บน": 10,
            "รส. 200 ปี ล่าง": 10, "หลวงพ่อแช่มชั้น 2": 10, "หลวงพ่อแช่มชั้น 3": 10, "ศัลยกรรมกระดูก": 15,
            "ศัลยกรรมชาย": 15, "ศัลยกรรมประสาท": 15, "ศัลยกรรมหญิง": 15, "หลวงพ่อแช่มชั้น 4": 10,
            "หลังคลอด": 15, "ห้องคลอด": 10, "อายุรกรรม 4": 15, "อายุรกรรม 2": 15,
            "อายุรกรรม 3": 15, "อายุรกรรม 5": 15, "อายุรกรรม 6": 15, "อายุรกรรม 7": 15,
            "วิสัญญี": 20, "CCU": 8, "Cath lab": 6, "Intervention": 7, "EENT": 10, "ER/ศูนย์ refer": 35,
            "ICCU": 10, "MICU": 10, "NICU": 10, "OPD": 10, "ศูนย์ ODS&MIS": 10, "ห้องผ่าตัด": 20,
            "PICU": 5, "Sick newborn": 10, "SICU": 5, "Stroke unit": 5, "RCU": 10, "สงฆ์อาพาธ": 10,
            "Wound care": 6, "Echo": 6, "OPD จิตเวช": 10, "เคมีบำบัด": 7, "OPD นรีเวช": 10,
            "OPD ศัลยกรรม": 10, "OPD กระดูก": 10, "OPD อายุรกรรม": 10, "OPD เบาหวาน": 10,
            "OPD งานเอดส์": 10, "OPDให้คำปรึกษา": 10, "OPD วัณโรค": 10, "OPD กุมารเวช": 10,
            "OPDAdmit+refer": 10, "OPD WCC": 10, "OPD ENT": 10, "OPD ตา": 10, "OPD Admit": 10,
            "OPD จุดคัดกรอง": 10, "OPD วชิระคลินิก": 10, "OPD ARI": 10, "OPD ทำแผล": 10,
            "OPD ฉีดยา": 10, "OPD เคมีบำบัด": 10, "OPD ฝากครรภ์": 10, "ศููนย์ใจรักษ์": 10
        }

        counts = df_display['หน่วยงาน'].value_counts().reset_index()
        counts.columns = ['หน่วยงาน', 'Count']
        
        counts['Target'] = counts['หน่วยงาน'].map(target_map).fillna(1)
        counts['Percent'] = (counts['Count'] / counts['Target'] * 100).clip(upper=100)
        
        chart1 = alt.Chart(counts).mark_bar().encode(
            x='หน่วยงาน', y=alt.Y('Percent', scale=alt.Scale(domain=[0, 100]))
        )
        st.altair_chart(chart1, use_container_width=True)
        
        # แสดง Metrics สรุปผล
        total_count = int(counts['Count'].sum())
        total_target = 780 
        total_percent = (total_count / total_target * 100)
        
        col1, col2, col3 = st.columns(3)
        col1.metric("จำนวนผู้ประเมินทั้งหมด", f"{total_count} คน")
        col2.metric("เป้าหมายทั้งหมด", f"{total_target} คน")
        col3.metric("ร้อยละความสำเร็จรวม", f"{total_percent:.1f}%")
        
        st.write("---") # เส้นคั่นก่อนขึ้นส่วนที่ 2
        
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
