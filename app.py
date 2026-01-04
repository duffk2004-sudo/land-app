import streamlit as st
import pandas as pd
import altair as alt

# -----------------------------------------------------------------------------
# 1. 페이지 및 스타일 설정 (보안 기능 포함)
# -----------------------------------------------------------------------------
st.set_page_config(page_title="토지개발 수지분석(Expert)", layout="wide")

# 상단 메뉴바와 GitHub 버튼 숨기기 (보안)
st.markdown("""
    <style>
    .stAppDeployButton {display:none;}
    [data-testid="stToolbar"] {visibility: hidden !important;}
    header {visibility: hidden !important;}
    footer {visibility: hidden !important;}
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
    st.title("🏗️ 토지개발 수지분석 시스템 (전문가용)")
    st.markdown("---")

    # 전체 레이아웃: 좌측(입력) / 우측(결과)
    col_input, col_result = st.columns([1, 1.5], gap="large")

    # =========================================================================
    # [좌측] 데이터 입력란
    # =========================================================================
    with col_input:
        st.header("📝 항목별 데이터 입력")

        # 1. 토지매입비용
        with st.expander("1. 토지매입비용", expanded=True):
            land_area_py = st.number_input("대지면적 (평)", value=100.0, step=1.0)
            land_area_m2 = land_area_py * 3.3058  # 자동계산용 m2
            
            land_price_per_py = st.number_input("평당 토지매입비 (만원)", value=2000, step=100)
            
            # 취득세 및 중개수수료율
            c1, c2 = st.columns(2)
            with c1:
                acq_tax_rate = st.number_input("토지 취등록세율(%)", value=4.6, step=0.1, help="기본 4.6% (농지 3.4% 등 상황에 맞게 조정)")
            with c2:
                broker_rate_buy = st.number_input("매입 중개수수료율(%)", value=0.9, step=0.1, help="상가/토지 최대 0.9%")
            
            # 계산: 토지매입비
            cost_land_pure = land_area_py * land_price_per_py
            cost_acq_tax = cost_land_pure * (acq_tax_rate / 100)
            cost_broker_buy = cost_land_pure * (broker_rate_buy / 100)
            
            st.info(f"💡 토지대금: {cost_land_pure:,.0f}만원 / 세금+수수료: {cost_acq_tax + cost_broker_buy:,.0f}만원")

        # 2. 인허가 및 부담금 (자동계산 적용)
        with st.expander("2. 인·허가 관련 비용 (부담금 자동계산)", expanded=True):
            design_arch = st.number_input("건축설계비 (만원)", value=1500, step=100)
            design_civil = st.number_input("토목설계비 (만원)", value=500, step=100)
            
            st.markdown("---")
            st.markdown("**🔍 부담금 산출 (공시지가 기준)**")
            official_price = st.number_input("개별공시지가 (원/㎡)", value=100000, step=1000)
            
            # 농지전용부담금
            st.caption("✅ 농지전용부담금 (공시지가의 30%, 상한 5만원)")
            is_farmland = st.checkbox("농지 전용 여부", value=True)
            ag_charge = 0.0
            if is_farmland:
                # ㎡당 상한액 50,000원 적용
                ag_unit_cost = min(official_price * 0.3, 50000)
                ag_charge = (ag_unit_cost * land_area_m2) / 10000  # 만원 단위 변환

            # 대체산림조성비
            st.caption("✅ 대체산림조성비 (2024년 7월 단가 적용)")
            is_forest = st.checkbox("산지 전용 여부", value=False)
            forest_charge = 0.0
            if is_forest:
                forest_type = st.selectbox("산지 구분", ["준보전산지", "보전산지", "산지전용제한지역"])
                
                # 2024년 고시 단가 + 공시지가의 0.1%(최대 8,090원)
                base_rates = {"준보전산지": 8090, "보전산지": 10510, "산지전용제한지역": 16180}
                add_rate = min(official_price * 0.001, 8090)
                
                forest_unit_cost = base_rates[forest_type] + add_rate
                forest_charge = (forest_unit_cost * land_area_m2) / 10000 # 만원 단위
            
            st.write(f"👉 농지부담금: {ag_charge:,.0f} 만원 / 산림부담금: {forest_charge:,.0f} 만원")

        # 3. 건축 및 토목 공사비 (평수 기준)
        with st.expander("3. 건축 및 토목 공사비", expanded=True):
            st.markdown("**(건물 평수 기준 계산)**")
            
            # 건물 연면적 입력 (용적률 대신 직접 입력도 가능하게)
            bldg_area_py = st.number_input("건축 연면적 (평)", value=200.0, step=1.0, help="실제 지어질 건물 총 평수")
            
            col_c1, col_c2 = st.columns(2)
            with col_c1:
                cost_per_py_arch = st.number_input("평당 건축비 (만원)", value=600, step=50)
            with col_c2:
                cost_per_py_civil = st.number_input("평당 토목비 (만원)", value=50, step=10, help="대지면적 기준이 아닌 필요한 경우 입력")

            # 계산
            cost_arch_total = bldg_area_py * cost_per_py_arch
            cost_civil_total = land_area_py * cost_per_py_civil # 토목은 보통 대지면적 기준이나 사용자가 항목을 원함
            
            st.info(f"🏗️ 순수 공사비 합계: {cost_arch_total + cost_civil_total:,.0f} 만원")

        # 4. 준공 후 제세금 및 추가비용
        with st.expander("4. 준공 후 세금 및 추가비용"):
            # 보존등기 취득세
            const_tax_rate = st.number_input("건물 보존등기 세율(%)", value=3.16, step=0.01, help="표준 2.8% + 농특세/교육세 = 약 3.16%")
            cost_const_tax = cost_arch_total * (const_tax_rate / 100)
            
            # 지목변경 취득세
            st.markdown("**지목변경 취득세** (지가상승분의 2.2%)")
            land_value_increase = st.number_input("지목변경 후 지가상승분(예상액, 만원)", value=10000, step=1000)
            cost_change_tax = land_value_increase * 0.022
            
            cost_add_const = st.number_input("준공 후 추가 공사비 (만원)", value=0, step=100)
            
        # 5. 분양(양도) 및 수지분석
        with st.expander("5. 양도(분양) 계획 및 세금", expanded=True):
            sales_price_per_py = st.number_input("평당 분양가 (만원)", value=1500, step=100)
            
            # 총 매출액
            total_sales = bldg_area_py * sales_price_per_py
            
            # 판매 수수료
            broker_rate_sell = st.number_input("분양 중개수수료율(%)", value=0.9, step=0.1)
            cost_broker_sell = total_sales * (broker_rate_sell / 100)
            
            st.markdown("---")
            st.markdown("### 💰 양도소득세 / 법인세")
            tax_method = st.radio("계산 방식 선택", ["직접 입력", "수익의 % 적용"])
            
            cost_capital_tax = 0.0
            if tax_method == "직접 입력":
                cost_capital_tax = st.number_input("양도세(법인세) 예상액 (만원)", value=0, step=100)
            else:
                tax_rate_input = st.number_input("예상 세율 (%)", value=22.0, step=1.0)
                # (매출 - 현재까지의 모든 비용) * 세율
                # 임시 계산을 위해 여기서 비용 합산
                temp_total_cost = (cost_land_pure + cost_acq_tax + cost_broker_buy + 
                                   design_arch + design_civil + ag_charge + forest_charge +
                                   cost_arch_total + cost_civil_total + 
                                   cost_const_tax + cost_change_tax + cost_add_const + cost_broker_sell)
                temp_profit = total_sales - temp_total_cost
                if temp_profit > 0:
                    cost_capital_tax = temp_profit * (tax_rate_input / 100)
            
            cost_other = st.number_input("기타 예비비 (만원)", value=1000, step=100)

    # =========================================================================
    # [우측] 결과 분석 대시보드
    # =========================================================================
    
    # 1. 최종 합계 계산
    total_land_cost = cost_land_pure + cost_acq_tax + cost_broker_buy
    total_permit_cost = design_arch + design_civil + ag_charge + forest_charge
    total_const_cost = cost_arch_total + cost_civil_total + cost_add_const
    total_tax_cost = cost_const_tax + cost_change_tax + cost_capital_tax
    total_sell_cost = cost_broker_sell + cost_other
    
    grand_total_cost = (total_land_cost + total_permit_cost + total_const_cost + 
                        total_tax_cost + total_sell_cost)
    
    net_profit = total_sales - grand_total_cost
    roi = (net_profit / grand_total_cost * 100) if grand_total_cost > 0 else 0

    with col_result:
        st.header("📊 수지분석 결과 리포트")
        
        # 1. 상단 요약 카드 (Metrics)
        m1, m2, m3 = st.columns(3)
        m1.metric("총 매출액 (수입)", f"{total_sales:,.0f} 만원")
        m2.metric("총 지출액 (비용)", f"{grand_total_cost:,.0f} 만원", f"-{grand_total_cost/total_sales*100:.1f}%")
        m3.metric("예상 순수익", f"{net_profit:,.0f} 만원", f"수익률 {roi:.2f}%", delta_color="normal")
        
        st.divider()

        # 2. 그래프 (Chart) - Altair 사용
        st.subheader("📈 수입 vs 지출 구조")
        
        chart_data = pd.DataFrame({
            '항목': ['총 매출', '총 비용', '순수익'],
            '금액': [total_sales, grand_total_cost, net_profit],
            '색상': ['#4c78a8', '#e45756', '#76b7b2'] # 파랑, 빨강, 청록
        })
        
        chart = alt.Chart(chart_data).mark_bar().encode(
            x=alt.X('항목', sort=None),
            y='금액',
            color=alt.Color('항목', legend=None, scale=alt.Scale(domain=['총 매출', '총 비용', '순수익'], range=['#4c78a8', '#e45756', '#76b7b2'])),
            tooltip=['항목', alt.Tooltip('금액', format=',.0f')]
        ).properties(height=300)
        
        st.altair_chart(chart, use_container_width=True)

        # 3. 상세 항목 표 (DataFrame)
        st.subheader("📋 지출 항목별 상세 내역")
        
        df = pd.DataFrame([
            ["1. 토지매입비", cost_land_pure],
            ["   ㄴ 취득세/중개수수료", cost_acq_tax + cost_broker_buy],
            ["2. 인허가비용 (설계비)", design_arch + design_civil],
            ["   ㄴ 농지/산림 부담금", ag_charge + forest_charge],
            ["3. 건축/토목 공사비", cost_arch_total + cost_civil_total],
            ["4. 준공후 세금(보존/지목)", cost_const_tax + cost_change_tax],
            ["   ㄴ 추가공사비", cost_add_const],
            ["5. 판매비용(수수료/기타)", cost_broker_sell + cost_other],
            ["6. 양도세(법인세)", cost_capital_tax],
        ], columns=["항목", "금액(만원)"])
        
        # 표 스타일링 (금액 포맷)
        st.dataframe(
            df.style.format({"금액(만원)": "{:,.0f}"}), 
            use_container_width=True, 
            hide_index=True,
            height=350
        )
        
        if net_profit > 0:
            st.success("✅ 사업성이 충분해 보입니다! (흑자 예상)")
        else:
            st.error("⚠️ 적자가 예상됩니다. 비용을 줄이거나 분양가를 조정하세요.")
