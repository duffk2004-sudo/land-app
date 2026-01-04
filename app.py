import streamlit as st
import pandas as pd
import altair as alt
import streamlit as st
import pandas as pd
import altair as alt

# --- 비밀번호 설정 (여기서 비밀번호를 바꾸세요) ---
SECRET_PASSWORD = "vipmember" 

# 로그인 화면 함수
def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == SECRET_PASSWORD:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # 보안을 위해 입력값 삭제
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # 처음 접속 시
        st.text_input(
            "유료 회원 전용 비밀번호를 입력하세요", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # 비밀번호 틀렸을 때
        st.text_input(
            "비밀번호가 틀렸습니다. 다시 입력하세요", type="password", on_change=password_entered, key="password"
        )
        return False
    else:
        # 비밀번호 맞았을 때
        return True

# --- 메인 코드 시작 ---
if check_password():
    # 여기에 아까 만든 계산기 코드가 쭉 나오면 됩니다.
    # (원래 있던 set_page_config는 check_password 보다 위에 있어야 합니다. 순서 주의!)
    
    # ... (여기서부터 아까 만든 st.sidebar... 코드가 시작됨)
    st.title("🏗️ 부동산 개발 수지분석 (회원전용)")
    # ... (나머지 코드 그대로)
# 페이지 설정
st.set_page_config(page_title="부동산 개발 마스터 (최종)", layout="wide")

st.title("🏗️ 부동산 개발 수지분석 (전문가용 Final)")
st.markdown("좌측에 값을 입력하면 우측에 결과가 나타납니다.")

# ==========================================
# 1. 왼쪽 사이드바 : 데이터 입력
# ==========================================
st.sidebar.header("📝 사업 수지 입력")

# 1단계: 토지 매입
with st.sidebar.expander("1️⃣ 토지 매입 단계", expanded=True):
    land_area = st.number_input("토지 면적 (평)", value=100)
    land_price = st.number_input("토지 평당 매입가 (만원)", value=3000)
    
    st.write("---")
    st.caption("👇 전용부담금 계산용 (필수)")
    public_price_m2 = st.number_input("개별공시지가 (원/㎡)", value=100000, step=1000)
    
    st.caption("👇 매입 부대비용")
    acq_tax_rate = st.number_input("취득세율 (%)", value=4.6, step=0.1)
    broker_fee_rate = st.number_input("매입 중개수수료율 (%)", value=0.9, step=0.1)
    legal_fee = st.number_input("법무사/기타 비용 (만원)", value=200)

# 2단계: 인허가 및 전용 (핵심 수정 부분)
with st.sidebar.expander("2️⃣ 인허가 및 전용부담금 (자동계산)"):
    design_cost = st.number_input("토목/건축 설계비 합계 (만원)", value=2000)
    
    st.write("---")
    st.write("🌍 **토지 유형 선택**")
    land_type = st.radio("지목 선택", ["농지 (전,답,과수원)", "산지 (임야)", "기타 (대지 등)"])

    farmland_charge = 0
    forest_cost = 0

    # 평 -> m2 환산
    land_area_m2 = land_area * 3.3058

    if land_type == "농지 (전,답,과수원)":
        st.caption(f"💡 농지보전부담금 (공시지가 30%, 상한 5만원/㎡)")
        unit_charge = min(public_price_m2 * 0.3, 50000)
        farmland_charge = (land_area_m2 * unit_charge) / 10000 
        st.info(f"농지부담금: {farmland_charge:,.0f} 만원")
        
    elif land_type == "산지 (임야)":
        st.caption("🌲 대체산림조성비 (2024년 기준 + 공시지가 1%)")
        forest_type = st.selectbox("산지 구분", ["준보전산지", "보전산지", "산지전용제한지역"])
        
        base_prices = {"준보전산지": 7260, "보전산지": 9430, "산지전용제한지역": 14520}
        base_price = base_prices[forest_type]
        forest_unit_price = base_price + (public_price_m2 * 0.001)
        
        forest_cost = (land_area_m2 * forest_unit_price) / 10000
        st.info(f"산림조성비: {forest_cost:,.0f} 만원")

# 3단계: 건축 공사
with st.sidebar.expander("3️⃣ 건축 공사 (시공)"):
    build_area = st.number_input("실제 건축할 연면적 (평)", value=60)
    civil_work_cost = st.number_input("토목 공사비 (만원)", value=3000)
    const_cost_per_py = st.number_input("평당 건축비 (만원)", value=800)

# 4단계: 준공 후 정산
with st.sidebar.expander("4️⃣ 준공 후 정산"):
    category_tax_rate = st.number_input("지목변경 취득세율 (%)", value=2.0)
    reg_tax_rate = st.number_input("보존등기 비용율 (%)", value=3.16)
    dev_charge = st.number_input("개발부담금 예상액 (만원)", value=1500)

# 5단계: 분양 및 양도세
with st.sidebar.expander("5️⃣ 분양(매출) 및 세금"):
    st.write("#### 💰 매출 계획")
    sale_type = st.radio("매출 기준", ["건축 평당 가격", "토지 평당 가격", "총 매출액 입력"])
    
    if sale_type == "건축 평당 가격":
        sale_price = st.number_input("분양가 (건축 1평당, 만원)", value=5000)
        total_sales = build_area * sale_price
    elif sale_type == "토지 평당 가격":
        sale_price = st.number_input("분양가 (토지 1평당, 만원)", value=6000)
        total_sales = land_area * sale_price
    else:
        total_sales = st.number_input("총 예상 매출액 (만원)", value=600000)

    st.write("---")
    st.write("#### 💸 매각 비용 및 양도세")
    sell_broker_fee = st.number_input("매각 중개수수료/기타 (만원)", value=1000)
    
    tax_method = st.radio("양도세 입력 방식", ["자동 계산 (세율 %)", "직접 금액 입력"])
    
    yangdo_tax_input = 0
    yangdo_tax_rate = 0
    
    if tax_method == "자동 계산 (세율 %)":
        yangdo_tax_rate = st.number_input("예상 양도세율 (%)", value=33.0)
    else:
        yangdo_tax_input = st.number_input("양도세 납부 예상액 (만원)", value=5000)


# ==========================================
# 2. 계산 로직 (여기가 안 보였던 부분!)
# ==========================================

# 1. 토지비
land_cost_pure = land_area * land_price
acq_tax = land_cost_pure * (acq_tax_rate / 100)
broker_fee = land_cost_pure * (broker_fee_rate / 100)
step1_cost = land_cost_pure + acq_tax + broker_fee + legal_fee

# 2. 인허가
step2_cost = design_cost + farmland_charge + forest_cost

# 3. 공사비
pure_build_cost = build_area * const_cost_per_py
step3_cost = civil_work_cost + pure_build_cost

# 4. 준공비
category_tax = step3_cost * (category_tax_rate / 100)
reg_tax = pure_build_cost * (reg_tax_rate / 100)
step4_cost = category_tax + reg_tax + dev_charge

# 5. 매각비
step5_cost_other = sell_broker_fee

# 총 사업비
total_project_cost = step1_cost + step2_cost + step3_cost + step4_cost + step5_cost_other

# 이익 계산
pre_tax_profit = total_sales - total_project_cost

# 양도세 처리
if tax_method == "직접 금액 입력":
    final_yangdo_tax = yangdo_tax_input
else:
    final_yangdo_tax = pre_tax_profit * (yangdo_tax_rate / 100) if pre_tax_profit > 0 else 0

net_profit = pre_tax_profit - final_yangdo_tax

if total_project_cost > 0:
    roi = (net_profit / total_project_cost) * 100
else:
    roi = 0

# ==========================================
# 3. 결과 대시보드 (우측 화면)
# ==========================================
st.subheader("📊 최종 분석 결과")

col1, col2, col3, col4 = st.columns(4)
col1.metric("1. 총 지출", f"{total_project_cost + final_yangdo_tax:,.0f} 만원")
col2.metric("2. 총 매출", f"{total_sales:,.0f} 만원")
col3.metric("3. 순이익", f"{net_profit:,.0f} 만원")
col4.metric("🔥 수익률", f"{roi:.1f} %")

st.divider()

tab1, tab2 = st.tabs(["📋 상세 내역서", "📊 그래프 분석"])

with tab1:
    st.write("#### 🏗️ 단계별 자금 투입 내역")
    data = {
        "단계": ["1.토지매입", "1.토지매입", "1.토지매입", "1.토지매입", 
                 "2.인허가", "2.인허가(부담금)", "2.인허가(부담금)", 
                 "3.공사", "3.공사", "4.준공", "4.준공", "4.준공", 
                 "5.매각/세금", "5.매각/세금"],
        "항목": ["순수 토지비", "취득세", "중개수수료", "법무비 등", 
                 "설계/감리비", "농지보전부담금", "대체산림조성비", 
                 "토목공사비", "건축공사비", 
                 "지목변경취득세", "보존등기비", "개발부담금", 
                 "매각수수료/기타", "양도소득세"],
        "금액(만원)": [land_cost_pure, acq_tax, broker_fee, legal_fee, 
                     design_cost, farmland_charge, forest_cost, 
                     civil_work_cost, pure_build_cost, 
                     category_tax, reg_tax, dev_charge, 
                     sell_broker_fee, final_yangdo_tax]
    }
    df = pd.DataFrame(data)
    # 0원인 항목은 숨기기
    df = df[df['금액(만원)'] > 0]
    st.dataframe(df.style.format({"금액(만원)": "{:,.0f}"}), use_container_width=True, height=500)

with tab2:
    st.write("#### 1. 지출 vs 이익 구조")
    chart_data = pd.DataFrame({
        '구분': ['총 비용', '양도세', '순이익'],
        '금액': [total_project_cost, final_yangdo_tax, net_profit]
    })
    c = alt.Chart(chart_data).mark_arc(innerRadius=60).encode(
        theta=alt.Theta(field="금액", type="quantitative"),
        color=alt.Color(field="구분", type="nominal"),
        tooltip=["구분", "금액"]
    )
    st.altair_chart(c, use_container_width=True)

    st.write("#### 2. 비용 vs 매출 (가로 보기)")
    bar_data = pd.DataFrame({
        '구분': ['총 지출 합계', '총 매출 합계'],
        '금액': [total_project_cost + final_yangdo_tax, total_sales]
    })
    
    base = alt.Chart(bar_data).encode(
        y=alt.Y('구분', title=None),
        x=alt.X('금액', title='금액 (만원)'),
        color='구분'
    )
    bars = base.mark_bar()
    text = base.mark_text(align='left', dx=5).encode(text=alt.Text('금액', format=',.0f'))
    st.altair_chart((bars + text).properties(height=200), use_container_width=True)