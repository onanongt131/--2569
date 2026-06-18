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
            access_list = str(user_row.iloc[0]['WardAccess'])
            
            # กรองข้อมูล
            if access_list != "ALL":
                allowed_wards = [w.strip() for w in access_list.split(',')]
                df = df[df['หน่วยงาน'].astype(str).str.strip().isin(allowed_wards)]
            
            # เช็คว่ามีข้อมูลเหลือไหมหลังกรอง
            if df.empty:
                st.warning(f"ไม่พบข้อมูลการประเมินสำหรับหน่วยงานที่คุณดูแล")
                st.write("ชื่อหน่วยงานในระบบคือ:", df['หน่วยงาน'].unique())
            else:
                # --- แสดงข้อมูล (ทุกอย่างต้องเยื้องเข้ามาอยู่ภายใต้ else นี้) ---
                
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
            st.error("รหัสผ่านไม่ถูกต้อง"))
