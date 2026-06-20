import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

@st.cache_data(ttl=60)
def load_data():
    sheet_url = "https://docs.google.com/spreadsheets/d/1U0bVw8G5jyMDwR6ohaqrU6k5KRwEhYIcCENMyoZoyyw/export?format=csv"
    df = pd.read_csv(sheet_url, encoding='utf-8-sig')
    perms_df = pd.read_csv("permissions.csv", encoding='utf-8-sig')
    # เพิ่มโค้ดนี้หลังโหลด df จาก Google Sheets
    # ใช้ regex เพื่อตัดตัวเลขท้ายชื่อหน่วยงานออก (สมมติว่าตัวเลขอยู่ท้ายชื่อ)
    df['หน่วยงาน'] = df['หน่วยงาน'].astype(str).str.replace(r'\s*\d+$', '', regex=True).str.strip()
    return df, perms_df

# ตารางเป้าหมาย (นำมาวางไว้ตรงนี้เพื่อให้เรียกใช้ได้ทุกจุด)
target_map = {
    "กุมารเวชกรรม 1": 0, "กุมารเวชกรรม 2": 0, "งานเวชศาสตร์ใต้น้ำ": 0, "งานไตเทียม HD/CAPD": 0,
    "น้อมเกล้า 2": 0, "น้อมเกล้า 3": 0, "น้อมเกล้า 4": 0, "นรีเวชกรรม": 0,
    "พิเศษอายุรกรรม 5": 0, "พิเศษอายุรกรรม 7": 0, "รติพัฒน์": 0, "รส.200 ปี บน": 0,
    "รส. 200 ปี ล่าง": 0, "หลวงพ่อแช่มชั้น 2": 0, "หลวงพ่อแช่มชั้น 3": 0, "หลวงพ่อแช่มชั้น 4": 0,
    "ศัลยกรรมกระดูก": 0, "ศัลยกรรมชาย": 0, "ศัลยกรรมประสาท": 0, "ศัลยกรรมหญิง": 0,
    "หลังคลอด": 0, "ห้องคลอด": 0, "อายุรกรรม 2": 0, "อายุรกรรม 3": 0, "อายุรกรรม 4": 0,
    "อายุรกรรม 5": 0, "อายุรกรรม 6": 0, "อายุรกรรม 7": 0, "วิสัญญี": 0, "CCU": 0,
    "Cath lab": 0, "Intervention": 0, "EENT": 0, "ER/ศูนย์ refer": 0, "ICCU": 0, "MICU": 0,
    "NICU": 0, "OPD": 0, "ศูนย์ ODS&MIS": 0, "ห้องผ่าตัด": 0, "PICU": 0, "Sick newborn": 0,
    "SICU": 0, "Stroke unit": 0, "RCU": 0, "สงฆ์อาพาธ": 0, "Wound care": 0, "Echo": 0,
    "OPD จิตเวช": 0, "เคมีบำบัด": 0, "OPD นรีเวช": 0, "OPD ศัลยกรรม": 0, "OPD กระดูก": 0,
    "OPD อายุรกรรม": 0, "OPD เบาหวาน": 0, "OPD งานเอดส์": 0, "OPDให้คำปรึกษา": 0,
    "OPD วัณโรค": 0, "OPD กุมารเวช": 0, "OPDAdmit+refer": 0, "OPD WCC": 0, "OPD ENT": 0,
    "OPD ตา": 0, "OPD Admit": 0, "OPD จุดคัดกรอง": 0, "OPD วชิระคลินิก": 0, "OPD ARI": 0,
    "OPD ทำแผล": 0, "OPD ฉีดยา": 0, "OPD เคมีบำบัด": 0, "OPD ฝากครรภ์": 0, "ศูนย์ใจรักษ์": 0
}

st.title("📊 Dashboard สรุปผลสำหรับผู้บริหาร")

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

        # 1. การกรองข้อมูลและกำหนดตัวเลือกหน่วยงาน
        if access_list == "ALL":
            df_filtered = df
            all_wards = ["ภาพรวมทั้งหมด"] + sorted(df['หน่วยงาน'].unique().tolist())
            allowed_wards = df['หน่วยงาน'].unique().tolist()
        else:
            allowed_wards = [w.strip() for w in access_list.split(',')]
            df_filtered = df[df['หน่วยงาน'].isin(allowed_wards)]
            all_wards = ["กลุ่มงานทั้งหมด"] + sorted(allowed_wards)

        # 2. เลือกหน่วยงาน
        if 'selected_ward' not in st.session_state or st.session_state.selected_ward not in all_wards:
            st.session_state.selected_ward = all_wards[0]

        selected_ward = st.selectbox("เลือกดูข้อมูล:", all_wards, key='selected_ward')
        
        # 3. เตรียมข้อมูลและเป้าหมาย
        if selected_ward == "ภาพรวมทั้งหมด":
            df_display = df_filtered
            display_target = 780
        elif selected_ward == "กลุ่มงานทั้งหมด":
            df_display = df_filtered
            display_target = sum([target_map.get(w, 10) for w in allowed_wards])
        else:
            df_display = df_filtered[df_filtered['หน่วยงาน'] == selected_ward]
            display_target = target_map.get(selected_ward, 10)

        # 4. ส่วนแสดงผล
        score_cols = df_display.select_dtypes(include=[np.number]).columns.drop('อายุผู้ประเมิน (ปี)', errors='ignore')

        st.subheader("ส่วนที่ 1: ร้อยละจำนวนผู้ประเมิน")
        if selected_ward in ["ภาพรวมทั้งหมด", "กลุ่มงานทั้งหมด"]:
            counts = df_display['หน่วยงาน'].value_counts().reset_index()
            counts.columns = ['หน่วยงาน', 'Count']
            chart1 = alt.Chart(counts).mark_bar().encode(x='หน่วยงาน', y='Count', color='หน่วยงาน')
            st.altair_chart(chart1, use_container_width=True)
            
        total_count = int(df_display.shape[0])
        total_percent = (total_count / display_target * 100) if display_target > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        col1.metric("จำนวนรวม", f"{total_count} คน")
        col2.metric("เป้าหมายรวม", f"{display_target} คน")
        col3.metric("ร้อยละความสำเร็จ", f"{total_percent:.1f}%")

        st.subheader("ส่วนที่ 2: ผลการประเมินภาพรวม")
        avg_data = (df_display[score_cols].mean() / 5 * 100).reset_index()
        avg_data.columns = ['หัวข้อ', 'Score']
        chart2 = alt.Chart(avg_data).mark_bar().encode(x=alt.X('Score', scale=alt.Scale(domain=[0, 100])), y='หัวข้อ')
        st.altair_chart(chart2, use_container_width=True)

        st.subheader("ส่วนที่ 3: คะแนนเฉลี่ย (Mean) และ SD")
        stats = df_display[score_cols].agg(['mean', 'std']).round(2).T
        st.dataframe(stats, use_container_width=True)

        if st.button("ออกจากระบบ"):
            st.session_state.password_correct = False
            st.rerun()

    except Exception as e:
        st.error(f"เกิดข้อผิดพลาด: {e}")
