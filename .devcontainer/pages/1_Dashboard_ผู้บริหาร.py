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
    
    sheet_url = "https://docs.google.com/spreadsheets/d/1U0bVw8G5jyMDwR6ohaqrU6k5KRwEhYIcCENMyoZoyyw/export?format=csv"
    
    try:
        # ดึงข้อมูล
        df = pd.read_csv(sheet_url)
        
        # 1. กราฟแสดงจำนวนผู้ประเมินแต่ละหน่วยงาน
        st.subheader("จำนวนผู้ประเมินรายหน่วยงาน")
        chart_data = df['ward'].value_counts()
        st.bar_chart(chart_data)
        
        # 2. ตารางข้อมูลดิบแยกตามหน่วยงาน
        st.subheader("ตารางข้อมูลดิบแยกตามหน่วยงาน")
        selected_ward = st.selectbox("เลือกหน่วยงาน:", df['ward'].unique())
        filtered_df = df[df['ward'] == selected_ward]
        st.dataframe(filtered_df)
        
        # 3. ปุ่มดาวน์โหลดข้อมูล
        csv = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="ดาวน์โหลดข้อมูลหน่วยงานนี้เป็น CSV",
            data=csv,
            file_name=f"report_{selected_ward}.csv",
            mime="text/csv"
        )
    except Exception as e:
        st.error(f"ไม่สามารถดึงข้อมูลได้: โปรดตรวจสอบว่า Sheet ถูกแชร์เป็น Public หรือยัง? (Error: {e})")
