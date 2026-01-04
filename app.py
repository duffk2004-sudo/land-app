import streamlit as st

# --- [보안] 상단 메뉴바와 GitHub 버튼 숨기기 (남들이 코드 못 보게 함) ---
st.markdown("""
    <style>
    .stAppDeployButton {display:none;}
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# 페이지 기본 설정
st.set_page_config(page_title="토지개발수지분석", layout="wide")

# 1. 비밀번호 확인 함수
def check_password():
    """비밀번호가 맞는지 확인하는 함수"""
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    if not st.session_state["password_correct"]:
        st.markdown("## 🔒 접근 제한 구역")
        st.write("관계자 외 출입을 금합니다.")
        
        password = st.text_input("비밀번호를 입력하세요", type="password")
        
        if st.button("로그인"):
            if password == "2580":
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.error("비밀번호가 틀렸습니다.")
        return False
    return True

# 2. 메인 앱 실행
if check_password():
    st.title("🏢 토지개발 수지분석 시스템")
    st.markdown("---")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("1. 기초 데이터 입력")
        land_area = st.number_input("대지면적 (평)", value=100.0)
        land_price = st.number_input("평당 토지비 (만원)", value=2000)
        floor_area_ratio = st.number_input("용적률 (%)", value=200.0)
        sales_price = st.number_input("평당 분양가 (만원)", value=3500)
        construction_cost = st.number_input("평당 공사비 (만원)", value=800)

    # 계산 로직
    total_sales = land_area * (floor_area_ratio / 100) * sales_price
    total_cost = (land_area * land_price) + (land_area * (floor_area_ratio / 100) * construction_cost) + (total_sales * 0.1)
    profit = total_sales - total_cost

    with col2:
        st.subheader("2. 결과 확인")
        st.metric(label="예상 수익", value=f"{profit:,.0f} 만원")
        
        if profit > 0:
            st.success("수익 발생 예상! 👍")
        else:
            st.error("적자 예상 📉")
