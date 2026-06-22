import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

st.set_page_config(layout="wide") 

@st.cache_data(ttl=60)
def load_data():
    sheet_url = "https://docs.google.com/spreadsheets/d/1U0bVw8G5jyMDwR6ohaqrU6k5KRwEhYIcCENMyoZoyyw/export?format=csv"
    df = pd.read_csv(sheet_url, encoding='utf-8-sig')
    perms_df = pd.read_csv("permissions.csv", encoding='utf-8-sig')
    return df, perms_df

# ตารางเป้าหมาย
target_map = {
    "กุมารเวชกรรม 1": 10, "กุมารเวชกรรม 2": 10, "งานเวชศาสตร์ใต้น้ำ": 5, "งานไตเทียม HD/CAPD": 10,
    "น้อมเกล้า 2": 10, "น้อมเกล้า 3": 10, "น้อมเกล้า 4": 10, "นรีเวชกรรม": 10,
    "พิเศษอายุรกรรม 5": 10, "พิเศษอายุรกรรม 7": 10, "รติพัฒน์": 10, "รส.200 ปี บน": 10,
    "รส. 200 ปี ล่าง": 10, "หลวงพ่อแช่มชั้น 2": 10, "หลวงพ่อแช่มชั้น 3": 10, "หลวงพ่อแช่มชั้น 4": 10,
    "ศัลยกรรมกระดูก": 15, "ศัลยกรรมชาย": 15, "ศัลยกรรมประสาท": 15, "ศัลยกรรมหญิง": 15,
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
    "OPD ฉีดยา": 10, "OPD เคมีบำบัด": 10, "OPD ฝากครรภ์": 10, "ศูนย์ใจรักษ์": 10
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
        if st.button("🔄 อัพเดตข้อมูลล่าสุด"):
            st.cache_data.clear()
            st.rerun()

        user_info = st.session_state.user_info
        access_list = str(user_info['WardAccess'])
        
        if access_list == "ALL":
            df_filtered = df
            all_wards = ["ภาพรวมทั้งหมด"] + sorted(df['หน่วยงาน'].unique().tolist())
            allowed_wards = df['หน่วยงาน'].unique().tolist()
        else:
            allowed_wards = [w.strip() for w in access_list.split(',')]
            df_filtered = df[df['หน่วยงาน'].isin(allowed_wards)]
            all_wards = ["กลุ่มงานทั้งหมด"] + sorted(allowed_wards)

        if 'selected_ward' not in st.session_state or st.session_state.selected_ward not in all_wards:
            st.session_state.selected_ward = all_wards[0]

        selected_ward = st.selectbox("เลือกดูข้อมูล:", all_wards, key='selected_ward')
        
        # เตรียมข้อมูล
        if selected_ward == "ภาพรวมทั้งหมด":
            df_display = df_filtered
            display_target = 780
        elif selected_ward == "กลุ่มงานทั้งหมด":
            df_display = df_filtered
            display_target = sum([target_map.get(w, 10) for w in allowed_wards])
        else:
            df_display = df_filtered[df_filtered['หน่วยงาน'] == selected_ward]
            display_target = target_map.get(selected_ward, 10)

        score_cols = df_display.select_dtypes(include=[np.number]).columns.drop('อายุผู้ประเมิน (ปี)', errors='ignore')

        # --- ส่วนที่ 1: ร้อยละจำนวนผู้ประเมิน ---
        st.subheader("ส่วนที่ 1: ร้อยละจำนวนผู้ประเมิน")
        ward_counts = df_display['หน่วยงาน'].value_counts().reset_index()
        ward_counts.columns = ['หน่วยงาน', 'Count']
        ward_counts['Target'] = ward_counts['หน่วยงาน'].map(target_map).fillna(10)
        ward_counts['Percent'] = (ward_counts['Count'] / ward_counts['Target'] * 100).round(1)
        
        chart1 = alt.Chart(ward_counts).mark_bar().encode(
            x='หน่วยงาน', y='Percent', color='หน่วยงาน',
            tooltip=['หน่วยงาน', 'Count', 'Target', 'Percent']
        ).properties(height=400)
        st.altair_chart(chart1, use_container_width=True)
        
        with st.expander("ดูรายละเอียดร้อยละรายหน่วยงาน"):
            st.dataframe(ward_counts[['หน่วยงาน', 'Count', 'Target', 'Percent']], use_container_width=True)

        total_count = int(df_display.shape[0])
        total_percent = (total_count / display_target * 100) if display_target > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        col1.metric("จำนวนรวม", f"{total_count} คน")
        col2.metric("เป้าหมายรวม", f"{display_target} คน")
        col3.metric("ร้อยละความสำเร็จ (รวม)", f"{total_percent:.1f}%")
        
        st.divider() 

        # --- ส่วนที่ 2: สรุปผลการประเมินภาพรวม ---
        st.subheader("ส่วนที่ 2: สรุปผลการประเมินภาพรวม")
        avg_data = (df_display[score_cols].mean() / 5 * 100).reset_index()
        avg_data.columns = ['หัวข้อ', 'Score']
        chart2 = alt.Chart(avg_data).mark_bar().encode(
            x=alt.X('Score', scale=alt.Scale(domain=[0, 100])), y='หัวข้อ'
        ).properties(height=500)
        st.altair_chart(chart2, use_container_width=True)

        df_display['Mean_Score'] = df_display[score_cols].mean(axis=1)
        def classify_score(s):
            if s >= 4.21: return "ดีมาก"
            elif s >= 3.41: return "ดี"
            elif s >= 2.61: return "ปานกลาง"
            elif s >= 1.81: return "น้อย"
            else: return "ควรปรับปรุง"

        df_display['Level'] = df_display['Mean_Score'].apply(classify_score)
        overall_avg = df_display['Mean_Score'].mean()
        count_good = df_display[df_display['Level'].isin(["ดีมาก", "ดี"])].shape[0]
        percent_good = (count_good / df_display.shape[0] * 100) if df_display.shape[0] > 0 else 0

        col_a, col_b = st.columns(2)
        col_a.metric("คะแนนเฉลี่ยรวม (20 ข้อ)", f"{overall_avg:.2f} / 5.00")
        col_b.metric("ร้อยละระดับดีขึ้นไป", f"{percent_good:.1f}%")

        st.write("**สถิติระดับความพึงพอใจ:**")
        st.table(df_display['Level'].value_counts().reset_index())
        
        st.divider()

        # --- ส่วนที่ 3: สถิติละเอียด ---
        st.subheader("ส่วนที่ 3: คะแนนเฉลี่ย (Mean) และ SD")
        stats = df_display[score_cols].agg(['mean', 'std']).round(2).T
        st.dataframe(stats, use_container_width=True)

        if st.button("ออกจากระบบ"):
            st.session_state.password_correct = False
            st.rerun()

    except Exception as e:
        st.error(f"เกิดข้อผิดพลาด: {e}")
