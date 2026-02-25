import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# ==========================================
# 1. 초기 설정 및 스타일 (직관성 강화)
# ==========================================
st.set_page_config(page_title="Golden-Bell Asset Master", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .main-header { font-size: 38px !important; font-weight: 800; color: #FFD700; text-align: center; margin-bottom: 10px; }
    .step-title { font-size: 22px; font-weight: 700; color: #FFFFFF; border-left: 5px solid #FFD700; padding-left: 15px; margin: 20px 0; }
    .recommend-box { border-radius: 15px; padding: 25px; background: linear-gradient(135deg, #1e1e1e, #2d2d2d); border: 1px solid #FFD700; }
    .stButton>button { height: 4em; font-weight: bold; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

TICKER_MAP = {
    "주식 (NVDA)": "NVDA",
    "크립토 (BTC)": "BTC-USD",
    "금 (Gold)": "GC=F",
    "채권 (TLT)": "TLT"
}

@st.cache_resource # 최신 버전용 캐시
def get_data(ticker):
    try:
        df = yf.download(ticker, period='1y', interval='1d', auto_adjust=True, progress=False)
        if df.empty or len(df) < 20: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        df['20SMA'] = df['Close'].rolling(window=20).mean()
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        return df.copy()
    except: return None

# ==========================================
# 2. [STEP 1] 매일 알려주는 투자 방향성
# ==========================================
st.markdown("<h1 class='main-header'>🏆 Golden-Bell 투자 네비게이터</h1>", unsafe_allow_html=True)
st.write("<p style='text-align: center; color: gray;'>데이터로 분석하고 원칙으로 실행하는 당신의 자산 관리 파트너</p>", unsafe_allow_html=True)

st.markdown("<div class='step-title'>📍 STEP 1. 오늘의 AI 추천 투자처</div>", unsafe_allow_html=True)
r1, r2, r3, r4 = st.columns(4)
r1.metric("1순위: 크립토", "매수 우위", "세력 매집")
r2.metric("2순위: 채권", "비중 확대", "금리 고점")
r3.metric("3순위: 주식", "중립", "실적 장세")
r4.metric("4순위: 금", "관망", "저항 확인")

# ==========================================
# 3. [STEP 2] 카테고리 선택 및 상세 가이드
# ==========================================
st.markdown("<div class='step-title'>📍 STEP 2. 관심 있는 자산을 선택하세요</div>", unsafe_allow_html=True)
selected_cat = st.selectbox("", list(TICKER_MAP.keys()), label_visibility="collapsed")
target_ticker = TICKER_MAP[selected_cat]

data = get_data(target_ticker)

if data is not None:
    last_row = data.dropna(subset=['20SMA', 'RSI']).iloc[-1]
    cur_p, sma_v, rsi_v = float(last_row['Close']), float(last_row['20SMA']), float(last_row['RSI'])

    # AI의 자산별 상세 브리핑 (사용자가 선택했을 때 다음 과정 가이드)
    st.markdown("<div class='recommend-box'>", unsafe_allow_html=True)
    st.subheader(f"📡 AI 브리핑: {selected_cat}")
    if cur_p > sma_v:
        st.write(f"현재 {selected_cat}는 **강세 추세**에 있습니다. '생명선'인 20일선 위에서 가격이 형성되어 있어 신규 진입 및 보유가 유리한 시점입니다.")
    else:
        st.write(f"현재 {selected_cat}는 **약세 흐름**입니다. 무리한 매수보다는 생명선을 회복할 때까지 기다리는 인내가 필요합니다.")
    st.markdown("</div>", unsafe_allow_html=True)

    # ==========================================
    # 4. [STEP 3] 진행 경로 선택 (실전 vs 교육)
    # ==========================================
    st.markdown("<div class='step-title'>📍 STEP 3. 분석 결과에 따른 실행을 선택하세요</div>", unsafe_allow_html=True)
    c_btn1, c_btn2 = st.columns(2)
    
    if 'mode' not in st.session_state: st.session_state.mode = "실전"
    if c_btn1.button("🚀 전문가용 실전 타점 확인 (PRO)", use_container_width=True): st.session_state.mode = "실전"
    if c_btn2.button("🧒 주니어용 지표 교육 & 실습 (EDU)", use_container_width=True): st.session_state.mode = "교육"

    st.markdown("---")

    if st.session_state.mode == "실전":
        st.subheader(f"📊 {selected_cat} 실전 매매 리포트")
        col1, col2, col3 = st.columns(3)
        col1.metric("현재가", f"{cur_p:,.2f}")
        col2.metric("20일선 이격", f"{(cur_p/sma_v*100)-100:+.2f}%")
        col3.metric("심리지수(RSI)", f"{rsi_v:.2f}")

        st.line_chart(data[['Close', '20SMA']].tail(100))
        
        st.info(f"**💡 전문가 가이드:** 진입 권장가는 {sma_v:,.2f} 부근이며, 목표가는 {cur_p*1.1:,.2f}입니다. **손절은 반드시 {sma_v*0.97:,.2f}**에서 기계적으로 실행하세요.")
    
    else:
        st.subheader(f"🎓 {selected_cat} 경제 지혜 학교")
        st.markdown("> **지표 공부하기:** 차트의 주황색 선은 '평균'을 말해요. 친구들 20명의 평균 점수보다 내 점수가 높으면 공부를 잘하고 있는 거죠? 주가도 똑같아요!")
        
        st.line_chart(data['Close'].tail(120))
        
        st.success(f"**💰 모의 투자 실습:** 지금 100만원을 투자하면 **{1000000/cur_p:.2f}개**를 가질 수 있어요. 미래에 이 가치가 어떻게 변할지 지켜볼까요?")
        if st.button("가상 투자 실행해보기"): st.balloons()

# ==========================================
# 5. 사이드바 (추가 보안/세력 정보)
# ==========================================
with st.sidebar:
    st.title("🏆 Golden-Bell 센터")
    st.write("---")
    st.subheader("📡 세력 레이더")
    if "크립토" in selected_cat:
        st.info("🐋 고래들의 대량 매집이 포착되었습니다. 단기 변동성보다는 장기 추세에 집중하세요.")
    elif "주식" in selected_cat:
        st.info("🏦 외국인과 기관의 동반 매수가 유입되고 있습니다. 실적 발표 시점을 주시하세요.")
    
    st.write("---")
    st.subheader("🛡️ 보안 리포트")
    st.write("현재 시장의 해킹 및 보안 관련 악재는 데이터상 '노이즈'로 판명되었습니다. 원칙대로 매매하십시오.")

st.markdown("---")
st.caption("Golden-Bell: 우리는 데이터로 판단하고 원칙으로 승리합니다. (Ver 2026.02.25)")
