import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Dashboard ผู้บริหาร", layout="wide")

# ระบบล็อกอินง่ายๆ
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
    st.title("📊 Dashboard สรุปผลการประเมินพยาบาล")
    
    # 1. ดึงข้อมูลจาก Google Sheets (ใช้ URL ของ Google Sheet)
    # หมายเหตุ: คุณต้องตั้งค่า Sheet ให้ "Anyone with the link can view"
    sheet_url = "URL_GOOGLE_SHEET_ของคุณ" 
    df = pd.read_csv(sheet_url.replace('/edit#gid=', '/export?format=csv&gid='))
    
    # 2. คำนวณร้อยละการทำแบบประเมิน (สมมติเทียบกับเป้าหมายที่ตั้งไว้)
    target = 100 # เป้าหมายต่อหน่วยงาน
    summary = df['ward'].value_counts().reset_index()
    summary.columns = ['หน่วยงาน', 'จำนวน']
    summary['ร้อยละความสำเร็จ'] = (summary['จำนวน'] / target) * 100
    
    st.subheader("ภาพรวมความสำเร็จรายหน่วยงาน")
    st.bar_chart(summary.set_index('หน่วยงาน')['ร้อยละความสำเร็จ'])
    
    # 3. เลือกหน่วยงานเพื่อดูรายงานแยกรายหน่วยงาน
    selected_ward = st.selectbox("เลือกหน่วยงานที่ต้องการดูรายงาน:", df['ward'].unique())
    ward_data = df[df['ward'] == selected_ward]
    
    st.subheader(f"รายงานละเอียด: {selected_ward}")
    st.dataframe(ward_data)
    
    # ดาวน์โหลดรายงาน
    csv = ward_data.to_csv(index=False).encode('utf-8')
    st.download_button("ดาวน์โหลดข้อมูลเป็น CSV", csv, "report.csv", "text/csv")
