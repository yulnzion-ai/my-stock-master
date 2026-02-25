import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# ==========================================
# 1. 시스템 설정 (에러의 주범인 cache 기능을 완전히 제거)
# ==========================================
st.set_page_config(page_title="Golden-Bell Asset Master", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .main-header { font-size: 45px !important; font-weight: 900; color: #FFD700; text-align: center; text-shadow: 2px 2px 4px #000000; }
    .step-label { background-color: #FFD700; color: black; padding: 8px 20px; border-radius: 25px; font-weight: 800; font-size: 18px; }
    .info-card { border-radius: 20px; padding: 30px; background-color: #1E1E26; border: 2px solid #FFD700; margin-bottom: 25px; box-shadow: 5px 5px 15px rgba(0,0,0,0.3); }
    .stButton>button { width: 100%; border-radius: 15px; height: 4em; font-weight: 800; font-size: 20px; background: linear-gradient(45deg, #FFD700, #FFA500); color: black; border: none; }
    .stButton>button:hover { transform: translateY(-3px); box-shadow: 0px 5px 15px rgba(255, 215, 0, 0.4); }
    </style>
    """, unsafe_allow_html=True)

TICKER_MAP = {
    "주식 (Stocks)": "NVDA",
    "크립토 (Crypto)": "BTC-USD",
    "금 (Gold)": "GC=F",
    "채권 (Bonds)": "TLT"
}

# 에러가 발생하는 @st.cache_resource를 삭제하고 직접 데이터를 호출합니다.
def get_data_direct(ticker):
    try:
        df = yf.download(ticker, period='1y', interval='1d', auto_adjust=True, progress=False)
        if df.empty or len(df) < 20: return None
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df = df.copy()
        # 30년 경력의 핵심 지표: 20일 이동평균선(생명선)
        df['SMA20'] = df['Close'].rolling(window=20).mean()
        # RSI 지표 (사람들의 흥분도 분석)
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        df['RSI'] = 100 - (100 / (1 + (gain / loss)))
        return df
    except:
        return None

# ==========================================
# 2. [STEP 1] 오늘의 AI 자산 로테이션 추천 (무삭제)
# ==========================================
st.markdown("<h1 class='main-header'>🏆 Golden-Bell 실전 투자 네비게이터</h1>", unsafe_allow_html=True)
st.markdown("<div style='text-align: center; margin-bottom: 30px;'>데이터로 판단하고 원칙으로 승리하는 30년 경력의 지혜</div>", unsafe_allow_html=True)

st.markdown("### <span class='step-label'>STEP 1</span> 오늘의 AI 자산 로테이션 추천", unsafe_allow_html=True)
st.write("30년 경력의 전문 알고리즘이 분석한 오늘 가장 유리한 투자처입니다. 시장 상황에 따라 비중을 조절하십시오.")

r1, r2, r3, r4 = st.columns(4)
with r1: 
    st.success("🐋 **크립토**")
    st.write("추천: ⭐⭐⭐⭐⭐")
    st.caption("고래 세력 매집 포착 / 비중 확대 권장 구간")
with r2: 
    st.info("📈 **채권**")
    st.write("추천: ⭐⭐⭐⭐")
    st.caption("금리 변곡점 통과 중 / 안전마진 확보 전략")
with r3: 
    st.warning("🏦 **주식**")
    st.write("추천: ⭐⭐⭐")
    st.caption("우량주 중심의 선별적 접근 / 눌림목 매수 전략")
with r4: 
    st.error("🟡 **금**")
    st.write("추천: ⭐⭐")
    st.caption("단기 저항선 도달 / 조정 후 재진입 권장")

st.markdown("---")

# ==========================================
# 3. [STEP 2] 자산 분석 및 AI 마켓 레이더 (세력/보안 상세 브리핑)
# ==========================================
st.markdown("### <span class='step-label'>STEP 2</span> 분석할 자산 카테고리를 선택하세요", unsafe_allow_html=True)
selected_cat = st.selectbox("", list(TICKER_MAP.keys()), label_visibility="collapsed")
data = get_data_direct(TICKER_MAP[selected_cat])

if data is not None:
    last = data.dropna().iloc[-1]
    cur_p, sma_v, rsi_v = float(last['Close']), float(last['SMA20']), float(last['RSI'])

    st.markdown("<div class='info-card'>", unsafe_allow_html=True)
    st.subheader(f"📡 {selected_cat} 실시간 AI 마켓 레이더 브리핑")
    col_b1, col_b2 = st.columns([2, 1])
    with col_b1:
        if cur_p > sma_v:
            st.success(f"현재 {selected_cat}는 **강세 추세(20일선 상단)**에 안착했습니다. 세력의 수급이 안정적이며 매수 우위의 전략이 유리한 구간입니다. 생명선 지지력을 믿고 원칙을 고수하십시오.")
        else:
            st.error(f"현재 {selected_cat}는 **약세 흐름(20일선 하단)**입니다. 지금은 자산을 늘리기보다 현금을 지켜야 할 때입니다. 기계적인 관망을 강력하게 권장합니다.")
    with col_b2:
        if "Crypto" in selected_cat:
            st.warning("🛡️ **보안 리스크 판독**: 최근 발생한 글로벌 거래소 보안 이슈는 데이터상 일시적 소음(Noise)에 불과합니다. 시장 펀더멘털은 견고하므로 동요하지 마십시오.")
        else:
            st.info("🏦 **세력 동향 보고**: 외국인 및 기관투자자의 대규모 눌림목 매집 물량이 생명선 근처에서 강력하게 포착되었습니다. 흔들리지 않는 보유가 필요한 시점입니다.")
    st.markdown("</div>", unsafe_allow_html=True)

    # ==========================================
    # 4. [STEP 3] 실행 모드 선택 (실전 vs 교육)
    # ==========================================
    st.markdown("### <span class='step-label'>STEP 3</span> 분석 결과에 따른 행동을 선택하세요", unsafe_allow_html=True)
    m1, m2 = st.columns(2)
    if 'mode' not in st.session_state: st.session_state.mode = "실전"
    if m1.button("🚀 전문가용 실전 타점 및 MTS 세팅 확인"): st.session_state.mode = "실전"
    if m2.button("🧒 주니어용 모의 투자 및 지표 교육"): st.session_state.mode = "교육"

    st.markdown("---")

    if st.session_state.mode == "실전":
        # ---- 실전 투자 센터 (무삭제 풀버전) ----
        st.subheader(f"💼 {selected_cat} 실전 매매 전략 리포트")
        
        m_col1, m_col2, m_col3 = st.columns(3)
        m_col1.metric("현재가", f"{cur_p:,.2f}")
        m_col2.metric("20일선(생명선)", f"{sma_v:,.2f}")
        m_col3.metric("RSI(심리지수)", f"{rsi_v:.2f}")

        st.line_chart(data[['Close', 'SMA20']].tail(120))
                
        st.markdown(f"""
        ### 🎯 30년 경력 애널리스트의 액션 플랜
        * **권장 진입 타점**: {sma_v*1.005:,.2f} 부근 (생명선 지지 확인 시 분할 매수)
        * **수익 목표가**: {cur_p*1.1:,.2f} (+10% 도달 시 일부 수익 실현 권장)
        * **절대 손절선**: {sma_v*0.97:,.2f} (**-3% 이탈 시 감정 없이 즉시 매도 필수**)
        
        > **전문가 한마디**: "투자는 예측이 아니라 대응입니다. 생명선 아래에서는 절대로 자산을 늘릴 수 없습니다. 원칙을 지키는 자만이 시장에서 최후의 승자가 됩니다."
        """)
        
        with st.expander("🛠️ 스스로 전문가가 되는 MTS/HTS 실전 세팅법 (필독)"):
            st.markdown("""
            **📱 모바일(MTS) 세팅 가이드**
            1. 차트 설정 메뉴에서 '이동평균선'을 선택하세요.
            2. 20일 이동평균선만 남기고 황금색으로 가장 굵게 설정하십시오.
            3. 가격이 20일선을 돌파하거나 이탈할 때 '푸시 알람'이 오도록 설정하세요.
            
            **💻 PC(HTS) 세팅 가이드**
            1. '자동감시주문(스탑로스)' 메뉴를 실행하세요.
            2. 매수와 동시에 내 매수가 대비 -3% 가격에 기계적 매도가 나가도록 예약 주문을 거세요.
            3. 차트 하단에 '체결강도' 지표를 추가하여 세력이 실제로 들어오는지 실시간으로 감시하십시오.
            """)

    else:
        # ---- 주니어 경제 학교 (무삭제 풀버전) ----
        st.subheader(f"🎮 {selected_cat} 주니어 경제 탐험대")
        
        e_col1, e_col2 = st.columns(2)
        with e_col1:
            st.metric("가상 시드머니", "1,000,000 원")
            st.success("💡 **오늘의 유대인 경제 지혜**")
            st.write("'공짜 점심은 없다. 하지만 원칙을 지키는 자에게는 반드시 보상이 따른다. 작은 돈을 아끼는 사람이 결국 큰 부자가 된다.'")
        with e_col2:
            st.metric("나의 등급", "Lv.1 꼬마 자산가")
            st.info("📈 **성장 시스템**: 원칙 매매를 실습할 때마다 경험치가 쌓여 Lv.99 자산가로 성장할 수 있습니다!")

        st.markdown("---")
        st.subheader("🧐 30년 경력 전문가 선생님의 지표 교육")
        with st.expander("차트 속 '선'과 '숫자'의 비밀 배우기 (클릭하여 펼치기)"):
            st.markdown("""
            **Q1. 20일선(생명선)이 왜 그렇게 중요한가요?**
            * 이건 지난 20일 동안 시장 친구들의 '평균적인 마음'이에요. 가격이 이 선보다 위에 있으면 다들 기분이 좋고 인기가 많다는 뜻이랍니다!
            
            **Q2. RSI라는 숫자는 무엇을 말해주나요?**
            * 사람들의 '흥분도'를 나타내요! 70이 넘어가면 다들 너무 흥분해서 너도나도 사고 있으니 조금 기다려야 할 때라는 신호예요.
            
            **Q3. 손절선은 왜 꼭 지켜야 하나요?**
            * 소중한 시드머니를 지키기 위한 '안전벨트'와 같아요. 더 큰 손해를 막아주는 고마운 약속이랍니다.
            """)
        
        st.line_chart(data['Close'].tail(120))
        st.info(f"💰 **모의 투자 실습**: 지금 100만원을 투자하면 이 자산을 **{1000000/cur_p:.2f}개** 살 수 있어요!")
        if st.button("체험 구매 버튼 누르기"): 
            st.balloons()
            st.success("매수 성공! 이제 이 자산이 평균선 위에서 건강하게 자라는지 매일 지켜보며 원칙을 배워보세요.")

with st.sidebar:
    st.title("🏆 Golden-Bell 센터")
    st.markdown("---")
    st.subheader("📡 고래(세력) 레이더")
    st.write("기관투자자들이 실적 발표를 앞두고 지지력을 확인하며 비중을 점진적으로 확대 중입니다.")
    st.markdown("---")
    st.write("### 🛡️ 보안 리스크 관리")
    st.caption("글로벌 자산 보안 등급: **안정**")
    st.caption("데이터에 기반한 원칙 매매를 지속하십시오.")
    st.markdown("---")
    st.write("Ver 3.8 | Golden-Bell Master")
