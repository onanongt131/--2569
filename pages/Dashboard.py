import streamlit as st
import pandas as pd
import numpy as np
import os

st.set_page_config(layout="wide")

@st.cache_data(ttl=60)
def load_data():
    base_dir = os.path.dirname(os.path.dirname(__file__))
    data_path = os.path.join(base_dir, "data.csv")
    perm_path = os.path.join(base_dir, "permissions.csv")
    df = pd.read_csv(data_path, encoding='utf-8-sig')
    perms_df = pd.read_csv(perm_path, encoding='utf-8-sig')
    return df, perms_df

st.title("📊 Dashboard สรุปผลการประเมินพยาบาล")

try:
    df, perms_df = load_data()
    pwd = st.sidebar.text_input("รหัสผ่านผู้บริหาร:", type="password")

    if pwd:
        if 'Password' in perms_df.columns:
            user_row = perms_df[perms_df['Password'].astype(str).str.strip() == str(pwd).strip()]

            if not user_row.empty:
                access_list = str(user_row.iloc[0]['WardAccess'])
                
                # ถ้าไม่ใช้สิทธิ์ ALL ให้กรองข้อมูล
                if access_list != "ALL":
                    allowed_wards = [w.strip() for w in access_list.split(',')]
                    df = df[df['หน่วยงาน'].astype(str).str.strip().isin(allowed_wards)]

                # เช็คว่ามีข้อมูลเหลือไหมหลังกรอง
                if df.empty:
                    st.warning("ไม่พบข้อมูลการประเมินสำหรับหน่วยงานที่คุณดูแล")
                else:
                    # ส่วนการแสดงผล
                    st.subheader("ส่วนที่ 1: ร้อยละจำนวนผู้ประเมิน")
                    progress = df['หน่วยงาน'].value_counts() / 50 * 100
                    st.bar_chart(progress)

                    # 2. ร้อยละผลการประเมินภาพรวม (กราฟแนวนอน)
                    st.subheader("ส่วนที่ 2: ร้อยละผลการประเมินภาพรวม")
                    avg_scores = df_filtered[score_cols].mean()
                    # สลับแกนให้แสดงเป็นกราฟแท่งแนวนอน
                    st.bar_chart(avg_scores / 5 * 100, horizontal=True)

                    # 3. Mean & SD รายข้อ (ปรับให้หัวข้ออยู่คอลัมน์)
                    st.subheader("ส่วนที่ 3: คะแนนเฉลี่ย (Mean) และ SD")
                    # ใช้ .T (Transpose) เพื่อเปลี่ยนแถวเป็นคอลัมน์
                    stats = df_filtered[score_cols].agg(['mean', 'std']).round(2).T
                    stats.columns = ['Mean', 'SD']
                    st.dataframe(stats, use_container_width=True)

                    # ดาวน์โหลด
                    csv = stats.to_csv().encode('utf-8-sig')
                    st.download_button("ดาวน์โหลดตารางสรุปผล (CSV)", csv, "summary.csv")

                    with st.expander("ดูข้อมูลดิบ"):
                        st.dataframe(df)
            else:
                st.error("รหัสผ่านไม่ถูกต้อง")
        else:
            st.error("ไม่พบหัวคอลัมน์ Password ในไฟล์ permissions.csv")
except Exception as e:
    st.error(f"เกิดข้อผิดพลาด: {e}")
