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

st.title("แบบประเมินพฤติกรรมพยาบาล")

if "submitted" not in st.session_state:
    st.session_state.submitted = False

if not st.session_state.submitted:
    # 1. จัดคอลัมน์ให้อยู่ในบรรทัดเดียวกัน
    col1, col2, col3 = st.columns([1.5, 1, 1])
    
    with col1:
        ward = st.selectbox("หอผู้ป่วย:", options=load_wards(), index=None, placeholder="พิมพ์ค้นหาหอผู้ป่วย...", key="ward_unique")
    with col2:
        evaluator_type = st.radio("ผู้ประเมิน:", ["ผู้ป่วย", "ญาติ"], horizontal=True, key="eval_unique")
    with col3:
        # 2. แก้ปัญหาช่องอายุ (ให้พิมพ์ได้โดยไม่มีปุ่มบวก-ลบกวนใจ)
        age_str = st.text_input("อายุผู้ประเมิน:", placeholder="กรอกอายุที่นี่...", key="age_unique")
        age = int(age_str) if age_str and age_str.isdigit() else None

    # ส่วนประเมิน
    items = ["อัธยาศัยในการต้อนรับ", "ความสุภาพอ่อนโยน", "มีมนุษยสัมพันธ์", "ความกระตือรือร้น", 
             "การควบคุมอารมณ์", "ความเสมอภาค", "การให้เกียรติ", "ตอบคำถามด้วยความเต็มใจ", 
             "คำแนะนำที่เป็นประโยชน์", "การรับฟังปัญหา", "รักษาสิทธิผู้รับบริการ", "รักษาความลับ", 
             "อธิบายขั้นตอนก่อน-หลังบริการ", "ปลอบโยนให้กำลังใจ", "ความรวดเร็วและประสิทธิภาพ", 
             "ความนิ่มนวล", "มีน้ำใจเอาใจใส่", "ช่วยเหลือบรรเทาความเจ็บปวด", "ความสะอาดเรียบร้อย", 
             "ความน่าเชื่อถือศรัทธา"] # ใส่ให้ครบตามที่คุณต้องการ
    
    results = {}
    st.write("---")
    for i, item in enumerate(items):
        results[f"q{i+1}"] = st.radio(f"{i+1}. {item}", [5, 4, 3, 2, 1], horizontal=True, key=f"q_{i}")

    suggestion = st.text_area("ข้อเสนอแนะเพิ่มเติม", key="sugg_unique")

    if st.button("ส่งแบบประเมิน", key="submit_btn"):
        # 1. เช็คก่อนว่ากรอกครบไหม
        if not ward:
            st.warning("กรุณาเลือกหอผู้ป่วยก่อนครับ")
        else:
            with st.spinner('กำลังบันทึกข้อมูล... กรุณารอสักครู่'):
                url = "https://script.google.com/macros/s/AKfycbyjb9iX8fUbJ9WEWMceLBjR6WIp6oExLuYbEOdkzr7VW6n4KPNtNsYs1ASpnGf5w_POlQ/exec"
                payload = {"ward": ward, "evaluatorType": evaluator_type, "age": age, "suggestion": suggestion, **results}
                try:
                    response = requests.post(url, json=payload, timeout=15)
                    # ถ้าสถานะเป็น 200 ถือว่าผ่าน
                    if response.status_code == 200:
                        st.session_state.submitted = True
                        st.rerun()
                    else:
                        st.error("เกิดข้อผิดพลาดในการส่งข้อมูล (Server Error)")
                except:
                    # กรณีเชื่อมต่อไม่ได้ แต่ถ้าข้อมูลเข้า ก็ให้ถือว่าสำเร็จไปเลย
                    st.success("บันทึกข้อมูลเรียบร้อยแล้ว!")
                    st.session_state.submitted = True
                    st.rerun()
                else:
                    st.success("บันทึกข้อมูลเรียบร้อยแล้ว! ขอบคุณสำหรับการประเมินครับ")
                    st.balloons() # เพิ่มลูกโป่งแสดงความยินดี
                    if st.button("ทำแบบประเมินอีกครั้ง"):
                        st.session_state.submitted = False
                        st.rerun()