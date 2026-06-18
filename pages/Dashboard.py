import streamlit as st
import pandas as pd

st.set_page_config(page_title="Dashboard ผู้บริหาร", layout="wide")

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
    st.title("📊 Dashboard สรุปผลการประเมิน")
    
    # URL ของ Google Sheet (ต้องเป็นไฟล์ที่เปิด Public Viewer ไว้)
    sheet_url = "https://docs.google.com/spreadsheets/d/1U0bVw8G5jyMDwR6ohaqrU6k5KRwEhYIcCENMyoZoyyw/export?format=csv"
    
    try:
        df = pd.read_csv(sheet_url)
        st.subheader("จำนวนผู้ประเมินรายหน่วยงาน")
        chart_data = df['หน่วยงาน'].value_counts()
        st.bar_chart(chart_data)
        
        st.subheader("ตารางข้อมูลดิบแยกตามหน่วยงาน")
        selected_ward = st.selectbox("เลือกหน่วยงาน:", df['หน่วยงาน'].unique())
        filtered_df = df[df['หน่วยงาน'] == selected_ward]
        st.dataframe(filtered_df)
        
        csv = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button("ดาวน์โหลดข้อมูลหน่วยงานนี้เป็น CSV", csv, f"report_{selected_ward}.csv", "text/csv")
    except Exception as e:
        st.error(f"ไม่สามารถดึงข้อมูลได้: {e}")
