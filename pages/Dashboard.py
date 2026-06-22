import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

# 1. ตั้งค่า Layout กว้าง
st.set_page_config(layout="wide") 

# 2. ปรับขนาด Font
st.markdown("""
    <style>
    .stApp { font-size: 28px !important; }
    h1, h2, h3 { color: #0068c9; }
    [data-testid="stMetricValue"] { font-size: 40px !important; }
    .stTable { font-size: 24px !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. ฟังก์ชันโหลดข้อมูล (คงเดิม)
@st.cache_data(ttl=60)
def load_data():
    sheet_url = "https://docs.google.com/spreadsheets/d/1U0bVw8G5jyMDwR6ohaqrU6k5KRwEhYIcCENMyoZoyyw/export?format=csv"
    df = pd.read_csv(sheet_url, encoding='utf-8-sig')
    perms_df = pd.read_csv("permissions.csv", encoding='utf-8-sig')
    return df, perms_df

# (ใส่ target_map ของคุณไว้ที่นี่เหมือนเดิมครับ...)
# [ตัดออกเพื่อประหยัดพื้นที่ - โปรดคงไว้ในโค้ดของคุณ]

# ส่วนจัดการ Login และแสดงผล Dashboard
st.title("📊 Dashboard สรุปผลสำหรับผู้บริหาร")

if "password_correct" not in st.session_state:
    st.session_state.password_correct = False

if not st.session_state.password_correct:
    pwd = st.text_input("รหัสผ่านผู้บริหาร:", type="password")
    if st.button("เข้าสู่ระบบ"):
        _, perms_df = load_data()
        user_row = perms_df[perms_df['Password'].astype(str).str.strip() == str(pwd).strip()]
        if not user_row.empty:
            st.session_state.password_correct = True
            st.session_state.user_info = user_row.iloc[0]
            st.rerun()
        else:
            st.error("รหัสผ่านไม่ถูกต้อง")
else:
    try:
        df, _ = load_data()
        if st.button("🔄 อัพเดตข้อมูลล่าสุด"):
            st.cache_data.clear()
            st.rerun()

        # [ส่วนการกรองหน่วยงาน... คงเดิม]
        # ... (โค้ดเตรียม df_display ของคุณ) ...

        # --- ส่วนที่ 1: ร้อยละจำนวนผู้ประเมิน ---
        st.subheader("ส่วนที่ 1: ร้อยละจำนวนผู้ประเมิน")
        # ... (โค้ดกราฟส่วนที่ 1 ของคุณ) ...
        st.divider()
        
        # --- ส่วนที่ 2: สรุปผลการประเมินภาพรวม ---
        st.subheader("ส่วนที่ 2: สรุปผลการประเมินภาพรวม")
        col_graph, col_summary = st.columns([0.7, 0.3])

        with col_graph:
            avg_data = (df_display[score_cols].mean() / 5 * 100).reset_index()
            avg_data.columns = ['หัวข้อ', 'Score']
            chart2 = alt.Chart(avg_data).mark_bar().encode(
                x=alt.X('Score', title='คะแนนเฉลี่ย (%)', scale=alt.Scale(domain=[0, 100])),
                y=alt.Y('หัวข้อ', title=None, axis=alt.Axis(labelLimit=400, labelFontSize=14)),
                color=alt.value('#2980b9') 
            ).properties(height=500)
            st.altair_chart(chart2, use_container_width=True)

        with col_summary:
            df_display['Mean_Score'] = df_display[score_cols].mean(axis=1)
            def classify_score(s):
                if s >= 4.21: return "ดีมาก"
                elif s >= 3.41: return "ดี"
                elif s >= 2.61: return "ปานกลาง"
                elif s >= 1.81: return "น้อย"
                else: return "ควรปรับปรุง"
            df_display['Level'] = df_display['Mean_Score'].apply(classify_score)
            
            # คำนวณสรุปผล
            overall_avg = df_display['Mean_Score'].mean()
            total_people = df_display.shape[0] 
            count_good = df_display[df_display['Level'].isin(["ดีมาก", "ดี"])].shape[0]
            percent_good = (count_good / total_people * 100) if total_people > 0 else 0

            st.metric("คะแนนเฉลี่ยรวม", f"{overall_avg:.2f} / 5.00")
            st.metric(label="ระดับดีขึ้นไป", value=f"{count_good} / {total_people} คน", delta=f"{percent_good:.1f}%")

            st.write("**สถิติระดับความพึงพอใจ:**")
            level_counts = df_display['Level'].value_counts().sort_index().reset_index()
            level_counts.columns = ['Level', 'Count']
            st.table(level_counts[level_counts['Count'] > 0])
        
        st.divider()

        # --- ส่วนที่ 3: สถิติละเอียด ---
        st.subheader("ส่วนที่ 3: คะแนนเฉลี่ย (Mean) และ SD")
        stats = df_display[score_cols].agg(['mean', 'std']).round(2).T
        st.dataframe(stats, use_container_width=True)
    
        # --- ส่วนที่ 4: สรุปจุดแข็งและจุดที่ควรปรับปรุง ---
        st.subheader("ส่วนที่ 4: วิเคราะห์จุดแข็งและจุดที่ต้องปรับปรุง")
        mean_scores = df_display[score_cols].mean()
        best_col, worst_col = mean_scores.idxmax(), mean_scores.idxmin()
        best_score, worst_score = mean_scores.max(), mean_scores.min()
            
        col1, col2 = st.columns(2)
        col1.metric("จุดแข็งที่สุด (คะแนนสูงสุด)", f"{best_score:.2f} / 5.00", best_col)
        col2.metric("จุดที่ควรปรับปรุง (คะแนนต่ำสุด)", f"{worst_score:.2f} / 5.00", worst_col)
        st.divider()

        if st.button("ออกจากระบบ"):
            st.session_state.password_correct = False
            st.rerun()

    except Exception as e:
        st.error(f"เกิดข้อผิดพลาด: {e}")
