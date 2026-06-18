import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(layout="wide")

# --- ฟังก์ชันดึงข้อมูล ---
@st.cache_data(ttl=60)
def load_data():
    # URL ของข้อมูลประเมิน
    # ใช้รูปแบบนี้เพื่อดึงข้อมูลจาก Tab ที่ต้องการ (เปลี่ยน sheet=ชื่อชีทของคุณ)
    sheet_url = "https://docs.google.com/spreadsheets/d/1U0bVw8G5jyMDwR6ohaqrU6k5KRwEhYIcCENMyoZoyyw/gviz/tq?tqx=out:csv&sheet=Sheet1"
    
    # URL ของไฟล์สิทธิ์ (ต้องมั่นใจว่าเปิด Publish to web เป็น CSV แล้ว)
    perm_url = "https://docs.google.com/spreadsheets/d/1m3qfh3x-H1EdEPW75rfuuVtR9pAcUZisOYK5CNt2LFPzipC6TNombBJ5/pub?output=csv"
    
    df = pd.read_csv(sheet_url)
    perms_df = pd.read_csv(perm_url)
    
    return df, perms_df

# --- ส่วนแสดงผล ---
st.title("📊 Dashboard สรุปผลการประเมินพยาบาล")

# ล็อกอินที่ Sidebar
pwd = st.sidebar.text_input("รหัสผ่านผู้บริหาร:", type="password")

if pwd:
    try:
        df, perms_df = load_data()
        
        # ตรวจสอบรหัสผ่านใน Sheet สิทธิ์
        user_row = perms_df[perms_df['Password'].astype(str) == str(pwd)]
        
        if not user_row.empty:
            # กรองข้อมูลตามสิทธิ์
            access_list = str(user_row.iloc[0]['WardAccess'])
            if access_list != "ALL":
                allowed_wards = [w.strip() for w in access_list.split(',')]
                df = df[df['หน่วยงาน'].isin(allowed_wards)]
            
            # --- แสดงข้อมูล ---
            # 1. ร้อยละจำนวนผู้ประเมิน
            st.subheader("ส่วนที่ 1: ร้อยละจำนวนผู้ประเมิน")
            progress = df['หน่วยงาน'].value_counts() / 50 * 100
            st.bar_chart(progress)

            # 2. ร้อยละผลการประเมินภาพรวม
            st.subheader("ส่วนที่ 2: ร้อยละผลการประเมินภาพรวม")
            score_cols = df.select_dtypes(include=[np.number]).columns.drop('อายุผู้ประเมิน (ปี)', errors='ignore')
            if not score_cols.empty:
                avg_score = df.groupby('หน่วยงาน')[score_cols].mean().mean(axis=1) / 5 * 100
                st.bar_chart(avg_score, horizontal=True)

            # 3. Mean & SD รายข้อ
            st.subheader("ส่วนที่ 3: คะแนนเฉลี่ย (Mean) และ SD")
            stats = df.groupby('หน่วยงาน')[score_cols].agg(['mean', 'std']).round(2)
            st.dataframe(stats)
            st.download_button("ดาวน์โหลดตารางสรุปผล (CSV)", stats.to_csv().encode('utf-8'), "summary.csv")

            # 4. ข้อมูลดิบ
            with st.expander("ดูข้อมูลดิบ"):
                st.dataframe(df)
        else:
            st.error("รหัสผ่านไม่ถูกต้อง")
            
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการโหลดข้อมูล: {e}")
        st.write("คำแนะนำ: โปรดตรวจสอบว่าลิงก์ Google Sheets ทั้งสองไฟล์ได้ตั้งค่าเป็น Public และรูปแบบคอลัมน์ถูกต้อง")
else:
    st.info("กรุณาใส่รหัสผ่านที่แถบด้านซ้ายมือเพื่อดูข้อมูล")
