import streamlit as st
import pandas as pd
import numpy as np
import os

st.set_page_config(layout="wide")

@st.cache_data(ttl=60)
def load_data():
    # ใช้ os เพื่อหา path ปัจจุบันให้ชัวร์
    base_dir = os.path.dirname(os.path.dirname(__file__))
    data_path = os.path.join(base_dir, "data.csv")
    perm_path = os.path.join(base_dir, "permissions.csv")
    
    # อ่านไฟล์โดยระบุ encoding ให้รองรับภาษาไทย
    df = pd.read_csv(data_path, encoding='utf-8-sig')
    perms_df = pd.read_csv(perm_path, encoding='utf-8-sig')
    
    return df, perms_df

st.title("📊 Dashboard สรุปผลการประเมินพยาบาล")

# โหลดข้อมูลและตรวจสอบ Error
try:
    df, perms_df = load_data()
    
    pwd = st.sidebar.text_input("รหัสผ่านผู้บริหาร:", type="password")
    
    if pwd:
        # ตรวจสอบคอลัมน์ใน perms_df ว่าตรงกับที่เขียนไหม
        if 'Password' in perms_df.columns:
            user_row = perms_df[perms_df['Password'].astype(str).str.strip() == str(pwd).strip()]
            
            if not user_row.empty:
                # ส่วนการแสดงผลเดิมของคุณ...
                st.success("เข้าสู่ระบบสำเร็จ")
            else:
                st.error("รหัสผ่านไม่ถูกต้อง")
        else:
            st.error(f"ไม่พบหัวคอลัมน์ 'Password' ในไฟล์ (คอลัมน์ที่พบคือ: {perms_df.columns.tolist()})")
            
except Exception as e:
    st.error(f"เกิดข้อผิดพลาด: {e}")
