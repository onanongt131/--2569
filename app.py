import streamlit as st
import requests

# ตั้งค่าหน้ากระดาษ
st.set_page_config(page_title="แบบประเมินพฤติกรรมพยาบาล", layout="wide")

# ฟังก์ชันดึงรายชื่อหอจากไฟล์
def load_wards():
    try:
        with open("wards.txt", "r", encoding="utf-8") as f:
            return [line.strip() for line in f.readlines()]
    except:
        return ["หอผู้ป่วย 1", "หอผู้ป่วย 2"]

# จัดการสถานะหน้าจอ
if "submitted" not in st.session_state:
    st.session_state.submitted = False

st.title("แบบประเมินพฤติกรรมพยาบาล")

# แสดงหน้าฟอร์มประเมินถ้ายังไม่ได้ส่ง
if not st.session_state.submitted:
    col1, col2, col3 = st.columns([1.5, 1, 1])
    
    with col1:
        ward = st.selectbox("หอผู้ป่วย:", options=load_wards(), index=None, placeholder="พิมพ์ค้นหาหอผู้ป่วย...", key="ward_unique")
    with col2:
        evaluator_type = st.radio("ผู้ประเมิน:", ["ผู้ป่วย", "ญาติ"], horizontal=True, key="eval_unique")
    with col3:
        age_str = st.text_input("อายุผู้ประเมิน:", placeholder="กรอกอายุที่นี่...", key="age_unique")
        age = int(age_str) if age_str and age_str.isdigit() else None

    items = ["อัธยาศัยในการต้อนรับ", "ความสุภาพอ่อนโยน", "มีมนุษยสัมพันธ์", "ความกระตือรือร้น", 
             "การควบคุมอารมณ์", "ความเสมอภาค", "การให้เกียรติ", "ตอบคำถามด้วยความเต็มใจ", 
             "คำแนะนำที่เป็นประโยชน์", "การรับฟังปัญหา", "รักษาสิทธิผู้รับบริการ", "รักษาความลับ", 
             "อธิบายขั้นตอนก่อน-หลังบริการ", "ปลอบโยนให้กำลังใจ", "ความรวดเร็วและประสิทธิภาพ", 
             "ความนิ่มนวล", "มีน้ำใจเอาใจใส่", "ช่วยเหลือบรรเทาความเจ็บปวด", "ความสะอาดเรียบร้อย", 
             "ความน่าเชื่อถือศรัทธา"]
    
    results = {}
    st.write("---")
    for i, item in enumerate(items):
        results[f"q{i+1}"] = st.radio(f"{i+1}. {item}", [5, 4, 3, 2, 1], horizontal=True, key=f"q_{i}")

    suggestion = st.text_area("ข้อเสนอแนะเพิ่มเติม", key="sugg_unique")

    if st.button("ส่งแบบประเมิน", key="submit_btn"):
        if not ward:
            st.warning("กรุณาเลือกหอผู้ป่วยก่อนครับ")
        else:
            with st.spinner('กำลังส่งข้อมูล...'):
                url = "https://script.google.com/macros/s/AKfycbyjb9iX8fUbJ9WEWMceLBjR6WIp6oExLuYbEOdkzr7VW6n4KPNtNsYs1ASpnGf5w_POlQ/exec"
                payload = {"ward": ward, "evaluatorType": evaluator_type, "age": age, "suggestion": suggestion, **results}
                try:
                    response = requests.post(url, json=payload, timeout=20)
                    if response.status_code == 200:
                        st.session_state.submitted = True
                        st.rerun()
                    else:
                        st.error(f"เกิดข้อผิดพลาดในการส่งข้อมูล (Status: {response.status_code})")
                except Exception as e:
                    st.error(f"ไม่สามารถเชื่อมต่อฐานข้อมูลได้: {e}")

# แสดงหน้า Success เมื่อส่งเสร็จแล้ว
else:
    st.success("บันทึกข้อมูลเรียบร้อยแล้ว! ขอบคุณสำหรับการประเมินครับ")
    st.balloons()
    if st.button("ทำแบบประเมินอีกครั้ง"):
        st.session_state.submitted = False
        st.rerun()ion_state.submitted = False
                        st.rerun()
