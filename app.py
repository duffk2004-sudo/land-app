import streamlit as st
import pandas as pd
import altair as alt

# -----------------------------------------------------------------------------
# 1. 페이지 및 스타일 설정
# -----------------------------------------------------------------------------
st.set_page_config(page_title="토지개발 수지분석(Final)", layout="wide")

# 스타일: 메뉴 숨김 + 탭 글씨 크기 조정 + 표 헤더 강조
st.markdown("""
    <style>
    .stAppDeployButton {display:none;}
    [data-testid="stToolbar"] {visibility: hidden !important;}
    header {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    
    /* 탭 글씨 크게 */
    button[data-baseweb="tab"] {
        font-size: 18px !important;
        font-weight: bold !important;
    }
    </style>
    """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. 비밀번호 확인 함수
# -----------------------------------------------------------------------------
def check_password():
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

# -----------------------------------------------------------------------------
# 3. 메인 앱 실행
# -----------------------------------------------------------------------------
if check_password():
    st.title("🏗️ 토지개발 수지분석 시스템 (최종 완성판)")
    st.markdown("---")

    # 전체 레이아웃: 좌측(입력) / 우측(결과)
    col_input, col_result = st.columns([1, 1.3], gap="large")

    # =========================================================================
    # [좌측] 데이터 입력란
    # =========================================================================
    with col_input:
        st.header("📝 데이터 입력")

        # 1. 토지매입비용
        with st.expander("1. 토지매입비용", expanded=True):
            land_area_py = st.number_input("대지면적 (평)", value=100.0, step=1.0)
            land_area_m2 = land_area_py * 3.3058  # m2 자동변환
            
            land_price_per_py = st.number_input("평당 토지매입비 (만원)", value=2000, step=100)
            
            c1, c2 = st.columns(2)
            with c1:
                acq_tax_rate = st.number_input("취등록세율(%)", value=4.6, step=0.1)
            with c2:
                broker_rate_buy = st.number_input("매입 중개수수료(%)", value=0.9, step=0.1)
            
            # 계산
            cost_land_pure = land_area_py * land_price_per_py
            cost_acq_tax = cost_land_pure * (acq_tax_rate / 100)
            cost_broker_buy = cost_land_pure * (broker_rate_buy / 100)

        # 2. 인허가 및 부담금
        with st.expander("2. 인·허가 및 농지/산지 부담금", expanded=True):
            design_arch = st.number_input("건축설계비 (만원)", value=1500, step=100)
            design_civil = st.number_input("토목설계비 (만원)", value=500, step=100)
            
            st.markdown("---")
            official_price = st.number_input("개별공시지가 (원/㎡)", value=100000, step=1000)
            
            # 농지전용
            is_farmland = st.checkbox("농지 전용 여부", value=True)
            ag_charge = 0.0
            if is_farmland:
                ag_unit_cost = min(official_price * 0.3, 50000)
                ag_charge = (ag_unit_cost * land_area_m2) / 10000

            # 산지전용
            is_forest = st.checkbox("산지 전용 여부", value=False)
            forest_charge = 0.0
            if is_forest:
                forest_type = st.selectbox("산지 구분", ["준보전산지", "보전산지", "산지전용제한지역"])
                base_rates = {"준보전산지": 8090, "보전산지": 10510, "산지전용제한지역": 16180}
                add_rate = min(official_price * 0.001, 8090)
                forest_unit_cost = base_rates[forest_type] + add_rate
                forest_charge = (forest_unit_cost * land_area_m2) / 10000

        # 3. 공사비
        with st.expander("3. 건축 및 토목 공사비", expanded=True):
            bldg_area_py = st.number_input("건축 연면적 (평)", value=200.0, step=1.0)
            
            c1, c2 = st.columns(2)
            with c1:
                cost_per_py_arch = st.number_input("평당 건축비 (만원)", value=600, step=50)
            with c2:
                cost_per_py_civil = st.number_input("평당 토목비 (만원)", value=50, step=10)

            cost_arch_total = bldg_area_py * cost_per_py_arch
            cost_civil_total = land_area_py * cost_per_py_civil

        # 4. 준공 후 비용 (개발부담금 포함)
        with st.expander("4. 준공 후 세금 및 개발부담금", expanded=True):
            const_tax_rate = st.number_input("보존등기 세율(%)", value=3.16, step=0.01)
            cost_const_tax = cost_arch_total * (const_tax_rate / 100)
            
            st.markdown("---")
            st.markdown("**① 지목변경 취득세**")
            land_val_increase = st.number_input("지가상승분(예상, 만원)", value=10000, step=1000)
            jimok_tax_rate = st.number_input("지목변경 세율(%)", value=2.2, step=0.1)
            cost_change_tax = land_val_increase * (jimok_tax_rate / 100)

            st.markdown("---")
            st.markdown("**② 개발부담금 (자동계산)**")
            dev_cost_input = st.number_input("인정 개발비용(공사비 등)", value=int(cost_arch_total+cost_civil_total))
            start_land_val = cost_land_pure 
            end_land_val = st.number_input("준공 후 토지감정가 (만원)", value=int(cost_land_pure * 1.5), step=1000)
            
            dev_profit = end_land_val - start_land_val - dev_cost_input
            dev_charge_calc = dev_profit * 0.25 if dev_profit > 0 else 0
            dev_charge = st.number_input("개발부담금 납부액", value=int(dev_charge_calc), step=100)
            
            cost_add
