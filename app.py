사장님, 정확한 지적입니다. 분양(매각) 금액을 산정할 때 '건물 평수'로 팔 수도 있고, '토지 평수'로 팔 수도 있어야 진정한 전문가용이죠.

말씀하신 대로 두 가지 기능을 완벽하게 수정했습니다.

분양가 기준 선택 기능 추가:

"건물 평수 기준" vs **"토지 평수 기준"**을 선택할 수 있게 만들었습니다.

선택에 따라 총 매출액이 정확하게 바뀝니다.

그래프 디자인 개선:

막대그래프의 폭을 좁혀서(Slim) 훨씬 세련되게 만들었습니다.

금액 숫자가 막대 끝에 정확하게 정렬되도록 위치를 조정했습니다.

아래 코드를 복사해서 덮어씌우시면 됩니다.

🔥 [최종] 분양기준 선택 + 그래프 디자인 수정 코드
Python

import streamlit as st
import pandas as pd
import altair as alt

# -----------------------------------------------------------------------------
# 1. 페이지 및 스타일 설정
# -----------------------------------------------------------------------------
st.set_page_config(page_title="토지개발 수지분석(Final)", layout="wide")

# 스타일 설정
st.markdown("""
    <style>
    .stAppDeployButton {display:none;}
    [data-testid="stToolbar"] {visibility: hidden !important;}
    header {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    
    /* 탭 글씨 시인성 높이기 */
    button[data-baseweb="tab"] {
        font-size: 16px !important;
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
    st.title("🏗️ 토지개발 수지분석 시스템 (전문가용)")
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
            
            # 계산 변수 정의
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

        # 4. 준공 및 개발부담금
        with st.expander("4. 준공 및 개발부담금", expanded=True):
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
            
            cost_add_const = st.number_input("기타 추가건축비 (만원)", value=0, step=100)
            
        # 5. 양도 및 수익분석 (기준 선택 기능 추가)
        with st.expander("5. 양도/이자 및 수익분석", expanded=True):
            # [수정] 분양가 산정 기준 선택
            st.markdown("##### 📌 분양(매각) 기준 선택")
            sales_criteria = st.radio(
                "어떤 면적을 기준으로 파시겠습니까?",
                ["건물 평수 기준 (연면적)", "토지 평수 기준 (대지면적)"],
                horizontal=True
            )
            
            sales_price_per_py = st.number_input("평당 분양가 (만원)", value=1500, step=100)
            
            # [수정] 선택한 기준에 따라 총 매출 계산
            if sales_criteria == "건물 평수 기준 (연면적)":
                total_sales = bldg_area_py * sales_price_per_py
                st.caption(f"👉 계산식: 연면적({bldg_area_py}평) × {sales_price_per_py}만원")
            else:
                total_sales = land_area_py * sales_price_per_py
                st.caption(f"👉 계산식: 대지면적({land_area_py}평) × {sales_price_per_py}만원")
            
            st.divider()
            
            broker_rate_sell = st.number_input("분양 수수료(%)", value=0.9, step=0.1)
            cost_broker_sell = total_sales * (broker_rate_sell / 100)
            
            cost_interest = st.number_input("사업이자비용 (PF이자 등, 만원)", value=0, step=100)
            cost_capital_tax = st.number_input("양도세(법인세) 입력 (만원)", value=5000, step=100)
            cost_other = st.number_input("기타 예비비 (만원)", value=1000, step=100)

    # =========================================================================
    # [우측] 결과 분석 대시보드
    # =========================================================================
    
    # 총계 계산
    grand_total_cost = (cost_land_pure + cost_acq_tax + cost_broker_buy + 
                        design_arch + design_civil + ag_charge + forest_charge +
                        cost_arch_total + cost_civil_total + cost_const_tax +
                        cost_change_tax + dev_charge + cost_add_const +
                        cost_broker_sell + cost_interest + cost_capital_tax + cost_other)
    
    net_profit = total_sales - grand_total_cost
    roi = (net_profit / grand_total_cost * 100) if grand_total_cost > 0 else 0

    with col_result:
        st.header("📊 수지분석 리포트")
        
        # 상단 요약 배너
        m1, m2, m3 = st.columns(3)
        m1.metric("총 매출 (수입)", f"{total_sales:,.0f} 만원")
        m2.metric("총 지출 (비용)", f"{grand_total_cost:,.0f} 만원")
        m3.metric("예상 순수익", f"{net_profit:,.0f} 만원", f"{roi:.2f}%", delta_color="normal")
        
        st.write("") # 간격 띄우기

        # 탭(Tab) 만들기
        tab_table, tab_graph = st.tabs(["📋 상세 지출 내역표", "📊 시각화 그래프"])

        # [탭 1] 상세 지출 내역표
        with tab_table:
            st.markdown("##### 📌 지출 항목별 상세 내역 (단위: 만원)")
            
            data_list = [
                ["1. 토지매입비", "순수 토지비", cost_land_pure],
                ["1. 토지매입비", "토지 취등록세", cost_acq_tax],
                ["1. 토지매입비", "매입 중개수수료", cost_broker_buy],
                
                ["2. 인허가/부담금", "건축 설계비", design_arch],
                ["2. 인허가/부담금", "토목 설계비", design_civil],
                ["2. 인허가/부담금", "농지전용부담금", ag_charge],
                ["2. 인허가/부담금", "대체산림조성비", forest_charge],
                
                ["3. 공사비", "건축 공사비", cost_arch_total],
                ["3. 공사비", "토목 공사비", cost_civil_total],
                
                ["4. 준공 및 부담금", "보존등기 취득세", cost_const_tax],
                ["4. 준공 및 부담금", "지목변경 취득세", cost_change_tax],
                ["4. 준공 및 부담금", "개발부담금", dev_charge],
                ["4. 준공 및 부담금", "기타 추가건축비", cost_add_const],
                
                ["5. 판매/이자/세금", "분양 중개수수료", cost_broker_sell],
                ["5. 판매/이자/세금", "사업이자비용", cost_interest],
                ["5. 판매/이자/세금", "양도세(법인세)", cost_capital_tax],
                ["5. 판매/이자/세금", "기타 예비비", cost_other],
            ]
            
            df_detail = pd.DataFrame(data_list, columns=["대항목", "세부항목", "금액"])
            
            # 요약행 추가
            summary_rows = [
                ["[ 소 계 ]", "----------------", 0],
                ["[ 결 과 ]", "① 총 매각금액", total_sales],
                ["[ 결 과 ]", "② 총 지출금액", grand_total_cost],
                ["[ 결 과 ]", "③ 예 상 수 익", net_profit],
            ]
            
            df_summary = pd.DataFrame(summary_rows, columns=["대항목", "세부항목", "금액"])
            df_final = pd.concat([df_detail, df_summary], ignore_index=True)

            # 포맷팅 함수
            def format_currency(row):
                if row['세부항목'] == "----------------":
                    return "-"
                val = row['금액']
                return f"{val:,.0f}"

            df_final['금액(만원)'] = df_final.apply(format_currency, axis=1)

            # 수익률 행
            roi_row = pd.DataFrame([["[ 결 과 ]", "④ 수 익 율", f"{roi:.2f}%"]], columns=["대항목", "세부항목", "금액(만원)"])
            df_display = pd.concat([df_final, roi_row], ignore_index=True)
            
            st.dataframe(
                df_display[["대항목", "세부항목", "금액(만원)"]],
                use_container_width=True,
                height=700,
                hide_index=True
            )

        # [탭 2] 그래프 (디자인 수정 반영)
        with tab_graph:
            st.markdown("##### 📈 수입 vs 지출 구조 분석")
            
            chart_data = pd.DataFrame({
                '항목': ['총 매출', '총 지출', '순수익'],
                '금액': [total_sales, grand_total_cost, net_profit],
                '색상': ['#1f77b4', '#d62728', '#2ca02c']
            })
            
            base = alt.Chart(chart_data).encode(
                x=alt.X('금액', axis=None), 
                y=alt.Y('항목', sort=None, title=""),
                color=alt.Color('색상', scale=None, legend=None),
                tooltip=['항목', alt.Tooltip('금액', format=',.0f')]
            )
            
            # [수정] 막대 굵기를 30으로 줄여서 얇고 세련되게 표현
            bar = base.mark_bar(size=30)
            
            # [수정] 텍스트를 막대 끝(Right)에 정렬
            text = base.mark_text(
                align='left',   # 왼쪽 정렬 (막대 끝 기준)
                dx=5,           # 막대에서 5픽셀 떨어뜨림
                fontSize=14,
                fontWeight='bold'
            ).encode(
                text=alt.Text('금액', format=',.0f')
            )
            
            st.altair_chart(bar + text, use_container_width=True)
            
            st.divider()
            
            st.markdown("##### 🍩 지출 비중 분석")
            cost_data = pd.DataFrame({
                'category': ['토지비', '인허가/부담금', '공사비', '준공/부담금', '판매/이자/세금'],
                'value': [
                    cost_land_pure + cost_acq_tax + cost_broker_buy,
                    design_arch + design_civil + ag_charge + forest_charge,
                    cost_arch_total + cost_civil_total,
                    cost_const_tax + cost_change_tax + dev_charge + cost_add_const,
                    cost_broker_sell + cost_interest + cost_capital_tax + cost_other
                ]
            })
            
            pie = alt.Chart(cost_data).mark_arc(innerRadius=60).encode(
                theta=alt.Theta(field="value", type="quantitative"),
                color=alt.Color(field="category", type="nominal", title="지출 항목"),
                tooltip=['category', alt.Tooltip('value', format=',.0f')]
            )
            st.altair_chart(pie, use_container_width=True)

        st.write("")
        if net_profit > 0:
            st.success(f"✅ **사업성 성공!** 예상 수익금은 **{net_profit:,.0f} 만원** 입니다.")
        else:
            st.error(f"⚠️ **사업성 주의!** **{abs(net_profit):,.0f} 만원**의 적자가 예상됩니다
