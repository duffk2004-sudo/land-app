import streamlit as st

# [중요] 페이지 기본 설정은 무조건 맨 위에 있어야 합니다!
st.set_page_config(page_title="토지개발수지분석", layout="wide")

# --- 상단 메뉴바와 GitHub 아이콘 숨기기 (괄호 수정 완료) ---
st.markdown("""
    <style>
    .stAppDeployButton {display:none;}
    [data-testid="stToolbar"] {visibility: hidden !important;}
    header {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    </style>
    """, unsafe_allow_html=True)

# 1. 비밀번호 확인 함수
def check_password():
    """비밀번호가 맞는지 확인하는 함수입니다."""
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    if not st.session_state["password_correct"]:
        st.markdown("## 🔒 접근 제한 구역")
        st.write("관계자 외 출입을 금합니다. 비밀번호를 입력해주세요.")
        
        password = st.text_input("비밀번호", type="password")
        
        if st.button("로그인"):
            if password == "2580":
                st.session_state["password_correct"] = True
                st.rerun()  # 화면을 새로고침해서 내용을 보여줌
            else:
                st.error("비밀번호가 틀렸습니다. 다시 시도해주세요.")
        return False
    return True

# 2. 메인 앱 실행 (비밀번호 통과 시에만 보임)
if check_password():
    # --- 여기서부터 진짜 앱 내용입니다 ---
    
    st.title("🏢 토지개발 수지분석 시스템")
    st.markdown("---")

    # 안내 메시지 (프린트/공유 관련)
    with st.expander("ℹ️ 사용 팁 (저장 및 인쇄)"):
        st.info("""
        - **인쇄/PDF 저장:** 브라우저 메뉴에서 `인쇄(Ctrl + P)`를 누른 뒤 'PDF로 저장'을 선택하시면 깔끔하게 저장됩니다.
        - **주소 공유:** 상단 주소창의 URL을 복사해서 전달하세요. (비밀번호 2580도 함께 알려주셔야 합니다.)
        """)

    # 화면을 좌우로 나누기 (왼쪽: 입력 / 오른쪽: 결과)
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("1. 기초 데이터 입력")
        land_area = st.number_input("대지면적 (평)", value=100.0, step=1.0)
        land_price = st.number_input("평당 토지비 (만원)", value=2000, step=100)
        floor_area_ratio = st.number_input("용적률 (%)", value=200.0, step=10.0)
        sales_price = st.number_input("평당 분양가 (만원)", value=3500, step=100)
        construction_cost = st.number_input("평당 공사비 (만원)", value=800, step=50)

    # 계산 로직
    total_land_cost = land_area * land_price  # 총 토지비
    total_floor_area = land_area * (floor_area_ratio / 100) # 연면적
    total_construction_cost = total_floor_area * construction_cost # 총 공사비
    total_sales = total_floor_area * sales_price # 총 매출액
    
    # 기타 비용 (대략 매출의 10% 가정)
    other_cost = total_sales * 0.1
    
    # 총 지출 및 수익
    total_cost = total_land_cost + total_construction_cost + other_cost
    profit = total_sales - total_cost
    profit_margin = (profit / total_sales) * 100 if total_sales > 0 else 0

    with col2:
        st.subheader("2. 수지 분석 결과")
        
        # 보기 좋게 카드 형태로 표시
        st.metric(label="예상 총 매출액", value=f"{total_sales:,.0f} 만원")
        st.metric(label="예상 총 지출", value=f"{total_cost:,.0f} 만원")
        
        st.markdown("---")
        st.write(f"**💰 예상 수익:** :red[{profit:,.0f} 만원]")
        st.write(f"**📈 수익률:** {profit_margin:.2f}%")

        if profit > 0:
            st.success("사업성이 있어 보입니다! 👍")
        else:
            st.error("적자가 예상됩니다. 조건을 다시 확인하세요. 📉")
