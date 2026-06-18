import streamlit as st
import pandas as pd
import numpy as np
import os
import altair as alt

st.set_page_config(layout="wide")

@st.cache_data(ttl=60)
def load_data():
    base_dir = os.path.dirname(os.path.dirname(__file__))
    df = pd.read_csv(os.path.join(base_dir, "data.csv"), encoding='utf-8-sig')
    perms_df = pd.read_csv(os.path.join(base_dir, "permissions.csv"), encoding='utf-8-sig')
    targets_df = pd.read_csv(os.path.join(base_dir, "targets.csv"), encoding='utf-8-sig')
    return df, perms_df, targets_df

st.title("📊 Dashboard สรุปผลการประเมินพยาบาล")

try:
    df, perms_df, targets_df = load_data()
    pwd = st.sidebar.text_input("รหัสผ่าน:", type="password")

    if pwd:
        user_row = perms_df[perms_df['Password'].astype(str).str.strip() == str(pwd).strip()]
        
        if not user_row.empty:
            access_list = str(user_row.iloc[0]['WardAccess'])
            if access_list != "ALL":
                allowed_wards = [w.strip() for w in access_list.split(',')]
                df = df[df['หน่วยงาน'].astype(str).str.strip().isin(allowed_wards)]

            if df.empty:
                st.warning("ไม่พบข้อมูลการประเมินสำหรับหน่วยงานที่คุณดูแล")
            else:
                st.sidebar.markdown("---")
                all_wards = ["ภาพรวมทั้งหมด"] + sorted(df['หน่วยงาน'].unique().tolist())
                selected_ward = st.sidebar.selectbox("เลือกหน่วยงาน:", all_wards)
                
                df_display = df[df['หน่วยงาน'] == selected_ward] if selected_ward != "ภาพรวมทั้งหมด" else df
                score_cols = df_display.select_dtypes(include=[np.number]).columns.drop('อายุผู้ประเมิน (ปี)', errors='ignore')

                # ส่วนที่ 1: ร้อยละตามเป้าหมาย (ใช้ progress_df)
                st.subheader("ส่วนที่ 1: ร้อยละจำนวนผู้ประเมิน (เทียบตามเป้าหมาย)")
                counts = df_display['หน่วยงาน'].value_counts().reset_index()
                counts.columns = ['หน่วยงาน', 'Count']
                progress_df = pd.merge(counts, targets_df, on='หน่วยงาน', how='left').fillna({'Target': 1})
                progress_df['Percent'] = (progress_df['Count'] / progress_df['Target'] * 100).clip(upper=100)
                
                chart1 = alt.Chart(progress_df).mark_bar().encode(
                    x='หน่วยงาน',
                    y=alt.Y('Percent', scale=alt.Scale(domain=[0, 100]))
                )
                st.altair_chart(chart1, use_container_width=True)

                # ส่วนที่ 2: ร้อยละผลการประเมินภาพรวม
                st.subheader("ส่วนที่ 2: ร้อยละผลการประเมินภาพรวม")
                avg_data = (df_display[score_cols].mean() / 5 * 100).reset_index()
                avg_data.columns = ['หัวข้อ', 'Score']
                chart2 = alt.Chart(avg_data).mark_bar().encode(
                    x=alt.X('Score', scale=alt.Scale(domain=[0, 100])),
                    y='หัวข้อ'
                )
                st.altair_chart(chart2, use_container_width=True)

                # ส่วนที่ 3: Mean & SD
                st.subheader("ส่วนที่ 3: คะแนนเฉลี่ย (Mean) และ SD")
                stats = df_display[score_cols].agg(['mean', 'std']).round(2).T
                stats.columns = ['Mean', 'SD']
                stats['SD'] = stats['SD'].fillna(0)
                st.dataframe(stats, use_container_width=True)
                
                st.download_button("ดาวน์โหลดตารางสรุปผล (CSV)", stats.to_csv().encode('utf-8-sig'), "summary.csv")
        else:
            st.error("รหัสผ่านไม่ถูกต้อง")
except Exception as e:
    st.error(f"เกิดข้อผิดพลาด: {e}")
