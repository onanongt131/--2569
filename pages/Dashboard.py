import streamlit as st
import pandas as pd

st.set_page_config(page_title="Dashboard ผู้บริหาร", layout="wide")

# ระบบล็อกอิน
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state.password_correct = False
    if not st.session_state.password_correct:
        pwd = st.text_input("รหัสผ่าน:", type="password")
        if pwd == "Admin1234":
            st.session_state.password_correct = True
            st.rerun()
        return False
    return True

if check_password():
    st.title("📊 Dashboard สรุปผลการประเมินพยาบาล")
    sheet_url = "https://docs.google.com/spreadsheets/d/1U0bVw8G5jyMDwR6ohaqrU6k5KRwEhYIcCENMyoZoyyw/export?format=csv"
    
    try:
        df = pd.read_csv(sheet_url)
        # ปรับชื่อคอลัมน์ให้เหมาะสม (ถ้าชื่อใน Sheet คือ 'หน่วยงาน')
        ward_col = 'หน่วยงาน' if 'หน่วยงาน' in df.columns else 'ward'
        
        # ส่วนที่ 1: เลือกดูภาพรวมหรือรายหน่วยงาน
        st.subheader("เลือกขอบเขตการดูข้อมูล")
        view_mode = st.radio("โหมดการดู:", ["ภาพรวมทั้งหมด", "แยกรายหน่วยงาน"], horizontal=True)
        
        target_df = df
        if view_mode == "แยกรายหน่วยงาน":
            selected_ward = st.selectbox("เลือกหน่วยงาน:", df[ward_col].unique())
            target_df = df[df[ward_col] == selected_ward]
        
        # ส่วนที่ 2: สรุปคะแนนเฉลี่ยรายข้อ
        st.subheader("คะแนนเฉลี่ยรายหัวข้อ")
        # เลือกเฉพาะคอลัมน์ที่เป็นตัวเลข (คะแนน)
        score_cols = target_df.select_dtypes(include=['number']).columns
        # ลบเฉพาะคอลัมน์ 'อายุผู้ประเมิน (ปี)' ออกจากการคำนวณคะแนน
        score_cols = [c for c in score_cols if "อายุ" not in c]
        
        means = target_df[score_cols].mean()
        st.bar_chart(means)
        
        # ส่วนที่ 3: ข้อมูลดิบ
        with st.expander("ดูตารางข้อมูลดิบ"):
            st.dataframe(target_df)
            csv = target_df.to_csv(index=False).encode('utf-8')
            st.download_button("ดาวน์โหลดข้อมูล CSV", csv, "report.csv", "text/csv")
            
    except Exception as e:
        st.error(f"ไม่สามารถดึงข้อมูลได้: {e}")
