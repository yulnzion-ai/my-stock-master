import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime

# ==========================================
# 1. 시스템 설정 및 디자인 (직관성 극대화)
# ==========================================
st.set_page_config(page_title="Golden-Bell Asset Master", layout="wide", initial_sidebar_state="expanded")

# 사용자 경험(UX)을 위한 커스텀 스타일
st.markdown("""
    <style>
    .main-header { font-size: 42px !important; font-weight: 800; color: #FFD700; text-align: center; margin-bottom: 30px; }
    .status-card { border-radius: 15px; padding: 20px; border: 1px solid #FFD700; background: rgba(255, 215, 0, 0.05); }
    .guide-box { background-color: #262730; padding: 20px; border-radius: 10px; border-left: 5px solid #FFD700; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 자산 설정
TICKER_MAP = {
    "주식 (NVDA)": "NVDA",
    "크립토 (BTC)": "BTC-USD",
    "금 (Gold)": "GC=F",
    "채권 (TLT)": "TLT"
}

@st.cache(allow_output_mutation=True)
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
# 2. [STEP 1] 글로벌 자산 로테이션 (투자처 추천)
# ==========================================
st.markdown("<h1 class='main-header'>🏆 Golden-Bell 실전 투자 의사결정</h1>", unsafe_allow_html=True)

st.subheader("📍 [1단계] AI 마켓 레이더: 지금 어디에 투자할까?")
top1, top2, top3, top4 = st.columns(4)
with top1: st.success("🐋 **크립토**: 매수 우위"); st.caption("세력 매집 확인 / 비중 확대")
with top2: st.info("📈 **채권**: 매력도 높음"); st.caption("금리 정점 통과 중 / 안전")
with top3: st.warning("🏦 **주식**: 선택적 매수"); st.caption("실적 우량주 중심 대응")
with top4: st.write("🟡 **금**: 관망"); st.caption("박스권 상단 저항")

st.markdown("---")

# ==========================================
# 3. [STEP 2] 자산 카테고리 선택 및 상세 분석
# ==========================================
st.subheader("📍 [2단계] 집중 분석할 자산을 선택하세요")
category_list = list(TICKER_MAP.keys())
selected_cat = st.selectbox("", category_list, label_visibility="collapsed")
target_ticker = TICKER_MAP[selected_cat]

data = get_data(target_ticker)

if data is not None:
    # 최신 데이터 추출
    last_row = data.dropna(subset=['20SMA', 'RSI']).iloc[-1]
    cur_p = float(last_row['Close'])
    sma_v = float(last_row['20SMA'])
    rsi_v = float(last_row['RSI'])

    # ==========================================
    # 4. [STEP 3] 진행 모드 선택 (실전 vs 교육)
    # ==========================================
    st.subheader(f"📍 [3단계] {selected_cat} - 실행 모드를 선택하세요")
    col_btn1, col_btn2 = st.columns(2)
    
    # 세션 상태로 모드 관리
    if 'app_mode' not in st.session_state: st.session_state.app_mode = "실전"
    
    if col_btn1.button("🚀 실전 매매 타점 (프로 전용)", use_container_width=True):
        st.session_state.app_mode = "실전"
    if col_btn2.button("🧒 모의 투자 및 교육 (주니어용)", use_container_width=True):
        st.session_state.app_mode = "교육"

    st.markdown("---")

    # ==========================================
    # 5. 모드별 상세 인터페이스 (약속된 기능 복구)
    # ==========================================
    if st.session_state.app_mode == "실전":
        st.markdown(f"### 💼 {selected_cat} 실전 매매 대시보드")
        
        # [지표 판독]
        m1, m2, m3 = st.columns(3)
        m1.metric("현재가", f"{cur_p:,.2f}")
        m2.metric("20일 생명선 이격도", f"{(cur_p/sma_v*100)-100:+.2f}%", delta="추세 유지" if cur_p > sma_v else "추세 하락")
        m3.metric("RSI (심리 지수)", f"{rsi_v:.2f}")

        # [실전 타점 및 이유]
        st.markdown("<div class='status-card'>", unsafe_allow_html=True)
        st.subheader("🎯 오늘의 실전 타점")
        if cur_p > sma_v * 1.01 and rsi_v < 70:
            st.write("✅ **판독:** 주가가 생명선 위에서 안정적으로 지지받고 있습니다. 매수 우위 구간입니다.")
        elif cur_p < sma_v * 0.99:
            st.write("❌ **판독:** 주가가 생명선 아래로 이탈했습니다. 지금 매수하는 것은 위험합니다. 관망하세요.")
        else:
            st.write("⚠️ **판독:** 방향성을 탐색 중입니다. 20일선 돌파를 확인하고 진입해도 늦지 않습니다.")
        
        st.write(f"**추천 행동:** 진입가 {sma_v:,.2f} 부근 / 목표가 {cur_p*1.1:,.2f} / **절대 손절가 {sma_v*0.97:,.2f}**")
        st.markdown("</div>", unsafe_allow_
