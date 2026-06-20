import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import time

st.set_page_config(page_title="แบบประเมินพฤติกรรม", page_icon="📊", layout="wide")

@st.cache_data(ttl=60)
def load_data(url):
    # เพิ่ม timestamp เพื่อป้องกัน Cache ของ Google Sheets
    return pd.read_csv(f"{url}&t={time.time()}")

# ระบบล็อกอิน
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state.password_correct = False
    if not st.session_state.password_correct:
        pwd = st.text_input("รหัสผ่านสำหรับผู้บริหาร:", type="password")
        if pwd == "Admin1234":
            st.session_state.password_correct = True
            st.rerun()
        return False
    return True

if check_password():
    st.title("📊 แบบประเมินพฤติกรรมบริการพยาบาล")
    
    sheet_url = "https://docs.google.com/spreadsheets/d/1U0bVw8G5jyMDwR6ohaqrU6k5KRwEhYIcCENMyoZoyyw/export?format=csv"
    
    try:
        df = load_data(sheet_url)
        
        if st.button("🔄 อัปเดตข้อมูลล่าสุด"):
            st.cache_data.clear()
            st.rerun()

        # สร้างข้อมูลสมมติสำหรับ Target (ถ้าไม่มีไฟล์เป้าหมาย ให้ใช้ Target = 10 ทุกหน่วยงาน)
        wards = df['หน่วยงาน'].unique()
        targets_df = pd.DataFrame({'หน่วยงาน': wards, 'Target': 10}) 

        # ตัวเลือกหน่วยงาน
        all_wards = ["ภาพรวมทั้งหมด"] + sorted(wards.tolist())
        selected_ward = st.selectbox("เลือกหน่วยงาน:", all_wards)
        df_display = df if selected_ward == "ภาพรวมทั้งหมด" else df[df['หน่วยงาน'] == selected_ward]

        # เลือกเฉพาะคอลัมน์ที่เป็นตัวเลข (คะแนน)
        score_cols = df_display.select_dtypes(include=[np.number]).columns.drop('อายุผู้ประเมิน (ปี)', errors='ignore')

        # ส่วนที่ 1: ร้อยละตามเป้าหมาย
        st.subheader("ส่วนที่ 1: ร้อยละจำนวนผู้ประเมิน (เทียบตามเป้าหมาย)")
        counts = df_display['หน่วยงาน'].value_counts().reset_index()
        counts.columns = ['หน่วยงาน', 'Count']
        progress_df = pd.merge(counts, targets_df, on='หน่วยงาน', how='left').fillna({'Target': 10})
        progress_df['Percent'] = (progress_df['Count'] / progress_df['Target'] * 100).clip(upper=100)
        
        chart1 = alt.Chart(progress_df).mark_bar().encode(
            x='หน่วยงาน', y=alt.Y('Percent', scale=alt.Scale(domain=[0, 100]))
        )
        st.altair_chart(chart1, use_container_width=True)

        # ส่วนที่ 2: ร้อยละผลการประเมินภาพรวม
        st.subheader("ส่วนที่ 2: ร้อยละผลการประเมินภาพรวม")
        avg_data = (df_display[score_cols].mean() / 5 * 100).reset_index()
        avg_data.columns = ['หัวข้อ', 'Score']
        chart2 = alt.Chart(avg_data).mark_bar().encode(
            x=alt.X('Score', scale=alt.Scale(domain=[0, 100])), y='หัวข้อ'
        )
        st.altair_chart(chart2, use_container_width=True)

        # ส่วนที่ 3: Mean & SD
        st.subheader("ส่วนที่ 3: คะแนนเฉลี่ย (Mean) และ SD")
        stats = df_display[score_cols].agg(['mean', 'std']).round(2).T
        stats.columns = ['Mean', 'SD']
        stats['SD'] = stats['SD'].fillna(0)
        st.dataframe(stats, use_container_width=True)

        # ปุ่ม Download
        csv = df_display.to_csv(index=False).encode('utf-8-sig')
        st.download_button("ดาวน์โหลดข้อมูลนี้เป็น CSV", csv, "report.csv", "text/csv")
        
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาด: {e}")
