import streamlit as st
import pandas as pd

st.set_page_config(page_title="Dashboard ผู้บริหาร", layout="wide")

# ระบบล็อกอิน
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state.password_correct = False
    
    if not st.session_state.password_correct:
        pwd = st.text_input("รหัสผ่านสำหรับผู้บริหาร:", type="password")
        if pwd == "Admin1234": # ตั้งรหัสผ่านที่นี่
            st.session_state.password_correct = True
            st.rerun()
        return False
    return True

if check_password():
    st.title("📊 Dashboard สรุปผลการประเมิน")
    
    # ดึงข้อมูลผ่าน Public CSV link ของ Google Sheet
    # 1. ที่ Google Sheet ให้กด Share > Anyone with the link = Viewer
    # 2. นำ URL มาวาง และเปลี่ยน /edit... เป็น /export?format=csv
    sheet_url = "https://docs.google.com/spreadsheets/d/1U0bVw8G5jyMDwR6ohaqrU6k5KRwEhYIcCENMyoZoyyw/export?format=csv"
    try:
        df = pd.read_csv(sheet_url.replace('/edit#gid=', '/export?format=csv&gid='))
        
        # กราฟแสดงจำนวนผู้ประเมินแต่ละหน่วยงาน
        st.subheader("จำนวนผู้ประเมินรายหน่วยงาน")
        chart_data = df['ward'].value_counts()
        st.bar_chart(chart_data)
        
        # รายงานแยกรายหน่วยงาน
        st.subheader("ตารางข้อมูลดิบแยกตามหน่วยงาน")
        selected_ward = st.selectbox("เลือกหน่วยงาน:", df['ward'].unique())
        filtered_df = df[df['ward'] == selected_ward]
        st.dataframe(filtered_df)
        
    except Exception as e:
        st.error(f"ไม่สามารถดึงข้อมูลได้: โปรดตรวจสอบว่า Sheet ถูกแชร์เป็น Public หรือยัง? {e}")"ดาวน์โหลดข้อมูลเป็น CSV", csv, "report.csv", "text/csv")
