import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(layout="wide")

# --- ฟังก์ชันดึงข้อมูลสิทธิ์และประเมิน ---
@st.cache_data(ttl=60)
def load_data():
    sheet_url = "https://docs.google.com/spreadsheets/d/1U0bVw8G5jyMDwR6ohaqrU6k5KRwEhYIcCENMyoZoyyw/export?format=csv"
    # เปลี่ยน URL นี้เป็นลิงก์ไฟล์สิทธิ์ของคุณ
    perm_url = "https://docs.google.com/spreadsheets/d/ใส่_ID_ชีท_สิทธิ์ของคุณ/export?format=csv"
    
    df = pd.read_csv(sheet_url)
    perms_df = pd.read_csv(perm_url)
    
    # Debug: ให้แสดงชื่อคอลัมน์ที่ระบบอ่านได้ ถ้ายัง error
    st.write("คอลัมน์ที่พบในไฟล์สิทธิ์:", perms_df.columns.tolist()) 
    
    return df, perms_df

# --- ส่วนแสดงผล ---
st.title("📊 Dashboard สรุปผลการประเมินพยาบาล")

pwd = st.sidebar.text_input("รหัสผ่านผู้บริหาร:", type="password")
if pwd:
    df, perms_df = load_data()
    user_row = perms_df[perms_df['Password'] == pwd]
    
    if not user_row.empty:
        # กรองข้อมูลตามสิทธิ์
        access_list = user_row.iloc[0]['WardAccess']
        if access_list != "ALL":
            allowed_wards = [w.strip() for w in access_list.split(',')]
            df = df[df['หน่วยงาน'].isin(allowed_wards)]
        
        # ส่วนที่ 1: % การทำแบบประเมิน (สมมติเป้าหมาย 50 ต่อหน่วย)
        st.subheader("ส่วนที่ 1: ร้อยละจำนวนผู้ประเมิน")
        progress = df['หน่วยงาน'].value_counts() / 50 * 100
        st.bar_chart(progress)

        # ส่วนที่ 2: ร้อยละภาพรวม (กราฟแนวนอน)
        st.subheader("ส่วนที่ 2: ร้อยละผลการประเมินภาพรวม")
        score_cols = df.select_dtypes(include=[np.number]).columns.drop('อายุผู้ประเมิน (ปี)', errors='ignore')
        avg_score = df.groupby('หน่วยงาน')[score_cols].mean().mean(axis=1) / 5 * 100
        st.bar_chart(avg_score, horizontal=True)

        # ส่วนที่ 3: Mean & SD รายข้อ
        st.subheader("ส่วนที่ 3: คะแนนเฉลี่ย (Mean) และ SD")
        stats = df.groupby('หน่วยงาน')[score_cols].agg(['mean', 'std']).round(2)
        st.dataframe(stats)
        
        # ดาวน์โหลดไฟล์
        csv = stats.to_csv().encode('utf-8')
        st.download_button("ดาวน์โหลดตารางสรุปผล (CSV)", csv, "summary.csv")

        # ส่วนที่ 4: ข้อมูลดิบ
        with st.expander("ดูข้อมูลดิบ"):
            st.dataframe(df)
            raw_csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("ดาวน์โหลดข้อมูลดิบ (CSV)", raw_csv, "raw_data.csv")
    else:
        st.error("รหัสผ่านไม่ถูกต้อง")
else:
    st.info("กรุณาใส่รหัสผ่านที่แถบด้านซ้ายมือเพื่อดูข้อมูล")
