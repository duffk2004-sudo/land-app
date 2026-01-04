import streamlit as st
import pandas as pd
import altair as alt

# -----------------------------------------------------------------------------
# 1. 페이지 및 스타일 설정
# -----------------------------------------------------------------------------
st.set_page_config(page_title="토지개발 수지분석(Expert)", layout="wide")

# 상단 메뉴바와 GitHub 버튼 숨기기 (보안)
st.markdown("""
    <style>
    .stAppDeployButton {display:none;}
    [data-testid="stToolbar"] {visibility: hidden !important;}
    header {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    /* 텍스트 가독성 높이기 */
    .stMetric {font-weight: bold;}
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
    col_input, col_result = st.columns([1, 1.2], gap="large")

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
            
            c1, c2 = st.columns(2)
            with c1:
                acq_tax_rate = st.number_input("토지 취등록세율(%)", value=4.6, step=0.1)
            with c2:
                broker_rate_buy = st.number_input("매입 중개수수료율(%)", value=0.9, step=0.1)
            
            cost_land_pure = land_area_py * land_price_per_py
            cost_acq_tax = cost_land_pure * (acq_tax_rate / 100)
            cost_broker_buy = cost_land_pure * (broker_rate_buy / 100)
            
            st.info(f"💵 토지비 소계: {cost_land_pure + cost_acq_tax + cost_broker_buy:,.0f} 만원")

        # 2. 인허가 및 부담금
        with st.expander("2. 인·허가 및 농지/산지 부담금", expanded=True):
            design_arch = st.number_input("건축설계비 (만원)", value=1500, step=100)
            design_civil = st.number_input("토목설계비 (만원)", value=500, step=100)
            
            st.markdown("---")
            official_price = st.number_input("개별공시지가 (원/㎡)", value=100000, step=1000)
            
            # 농지전용
            is_farmland = st.checkbox("농지 전용 (공시지가 30%)", value=True)
            ag_charge = 0.0
            if is_farmland:
                ag_unit_cost = min(official_price * 0.3, 50000)
                ag_charge = (ag_unit_cost * land_area_m2) / 10000

            # 산지전용
            is_forest = st.checkbox("산지 전용 (별도 단가 적용)", value=False)
            forest_charge = 0.0
            if is_forest:
                forest_type = st.selectbox("산지 구분", ["준보전산지", "보전산지", "산지전용제한지역"])
                base_rates = {"준보전산지": 8090, "보전산지": 10510, "산지전용제한지역": 16180}
                add_rate = min(official_price * 0.001, 8090)
                forest_unit_cost = base_rates[forest_type] + add_rate
                forest_charge = (forest_unit_cost * land_area_m2) / 10000
            
            st.write(f"👉 농지부담금: {ag_charge:,.0f} / 산림부담금: {forest_charge:,.0f} (만원)")

        # 3. 공사비
        with st.expander("3. 건축 및 토목 공사비"):
            bldg_area_py = st.number_input("건축 연면적 (평)", value=200.0, step=1.0)
            
            c1, c2 = st.columns(2)
            with c1:
                cost_per_py_arch = st.number_input("평당 건축비 (만원)", value=600, step=50)
            with c2:
                cost_per_py_civil = st.number_input("평당 토목비 (만원)", value=50, step=10)

            cost_arch_total = bldg_area_py * cost_per_py_arch
            cost_civil_total = land_area_py * cost_per_py_civil
            
            st.info(f"🏗️ 공사비 합계: {cost_arch_total + cost_civil_total:,.0f} 만원")

        # 4. 준공 후 비용 (개발부담금 포함)
        with st.expander("4. 준공 후 세금 및 개발부담금", expanded=True):
            # 보존등기
            const_tax_rate = st.number_input("건물 보존등기 세율(%)", value=3.16, step=0.01)
            cost_const_tax = cost_arch_total * (const_tax_rate / 100)
            
            st.markdown("---")
            # 지목변경 취득세
            st.markdown("**① 지목변경 취득세**")
            land_val_increase = st.number_input("지목변경 후 지가상승분(예상, 만원)", value=10000, step=1000)
            jimok_tax_rate = st.number_input("지목변경 세율(%)", value=2.2, step=0.1)
            cost_change_tax = land_val_increase * (jimok_tax_rate / 100)
            st.caption(f"👉 예상 세액: {cost_change_tax:,.0f} 만원")

            st.markdown("---")
            # 개발부담금 (New)
            st.markdown("**② 개발부담금 (개발이익 환수)**")
            st.caption("공식: (종료시점지가 - 개시지가 - 개발비용) × 25%")
            
            # 개발부담금 계산기
            dev_cost_input = st.number_input("인정 개발비용(공사비 등, 만원)", value=int(cost_arch_total+cost_civil_total), help="보통 공사비와 설계비 등이 포함됩니다.")
            start_land_val = cost_land_pure # 매입가로 가정
            end_land_val = st.number_input("준공 후 예상 토지감정가 (만원)", value=int(cost_land_pure * 1.5), step=1000)
            
            dev_profit = end_land_val - start_land_val - dev_cost_input
            dev_charge_calc = dev_profit * 0.25 if dev_profit > 0 else 0
            
            # 최종 입력란 (자동계산값 보여주되 수정 가능)
            dev_charge = st.number_input("개발부담금 납부액 (만원)", value=int(dev_charge_calc), step=100)
            
            cost_add_const = st.number_input("기타 준공관련 비용 (만원)", value=0, step=100)
            
        # 5. 양도 및 기타
        with st.expander("5. 양도(분양) 및 수익분석"):
            sales_price_per_py = st.number_input("평당 분양가 (만원)", value=1500, step=100)
            total_sales = bldg_area_py * sales_price_per_py
            
            broker_rate_sell = st.number_input("분양 중개수수료(%)", value=0.9, step=0.1)
            cost_broker_sell = total_sales * (broker_rate_sell / 100)
            
            cost_capital_tax = st.number_input("양도세(법인세) 직접입력 (만원)", value=5000, step=100)
            cost_other = st.number_input("기타 예비비 (만원)", value=1000, step=100)

    # =========================================================================
    # [우측] 결과 분석 대시보드
    # =========================================================================
    
    # 총계 계산
    total_land_cost = cost_land_pure + cost_acq_tax + cost_broker_buy
    total_permit_cost = design_arch + design_civil + ag_charge + forest_charge
    total_const_cost = cost_arch_total + cost_civil_total + cost_add_const
    total_tax_dev_cost = cost_const_tax + cost_change_tax + dev_charge  # 개발부담금 포함
    total_sell_cost = cost_broker_sell + cost_other + cost_capital_tax
    
    grand_total_cost = (total_land_cost + total_permit_cost + total_const_cost + 
                        total_tax_dev_cost + total_sell_cost)
    
    net_profit = total_sales - grand_total_cost
    roi = (net_profit / grand_total_cost * 100) if grand_total_cost > 0 else 0

    with col_result:
        st.header("📊 분석 결과 리포트")
        
        # 1. 상단 요약 (Metrics)
        m1, m2, m3 = st.columns(3)
        m1.metric("총 매출액", f"{total_sales:,.0f} 만원")
        m2.metric("총 지출액", f"{grand_total_cost:,.0f} 만원")
        m3.metric("예상 순수익", f"{net_profit:,.0f} 만원", f"{roi:.2f}%")
        
        st.divider()

        # 2. 지출 상세 내역 (표) - 항상 보임
        st.subheader("📋 지출 항목별 상세 내역")
        
        df = pd.DataFrame([
            ["1. 토지매입비(세금포함)", total_land_cost],
            ["2. 인허가/부담금", total_permit_cost],
            ["   (농지/산림 부담금)", ag_charge + forest_charge],
            ["3. 건축/토목 공사비", total_const_cost],
            ["4. 준공후 세금/부담금", total_tax_dev_cost],
            ["   (지목변경 취득세)", cost_change_tax],
            ["   (개발부담금)", dev_charge],
            ["5. 판매비용/양도세", total_sell_cost],
            ["   (양도세/법인세)", cost_capital_tax],
        ], columns=["구분", "금액(만원)"])
        
        # 표 그리기
        st.dataframe(
            df.style.format({"금액(만원)": "{:,.0f}"}), 
            use_container_width=True, 
            hide_index=True,
            height=350
        )

        # 3. 그래프 (클릭해야 열림)
        with st.expander("📊 그래프 확인하기 (클릭하세요)"):
            st.markdown("##### 수입 vs 지출 vs 순수익 구조")
            
            chart_data = pd.DataFrame({
                '항목': ['총 매출', '총 지출', '순수익'],
                '금액': [total_sales, grand_total_cost, net_profit],
                'Color': ['#1f77b4', '#d62728', '#2ca02c'] # 파랑, 빨강, 초록
            })
            
            # 막대 그래프
            base = alt.Chart(chart_data).encode(
                x=alt.X('항목', sort=None, axis=alt.Axis(labelAngle=0)), # 글씨 가로로
                y='금액',
                color=alt.Color('Color', scale=None)
            )
            
            bar = base.mark_bar(size=50)
            
            # 막대 위 글씨 (가로)
            text = base.mark_text(
                align='center',
                baseline='bottom',
                dy=-5,  # 막대 살짝 위
                fontSize=14
            ).encode(
                text=alt.Text('금액', format=',.0f')
            )
            
            st.altair_chart((bar + text).properties(height=350), use_container_width=True)

        if net_profit > 0:
            st.success("✅ 사업성 양호 (흑자 예상)")
        else:
            st.error("⚠️ 사업성 주의 (적자 예상)")
