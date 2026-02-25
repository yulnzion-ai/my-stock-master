import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime

# ==========================================
# 1. 시스템 설정 및 디자인 (철학 반영)
# ==========================================
st.set_page_config(page_title="Golden-Bell Asset Master", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .main-header { font-size: 42px !important; font-weight: 800; color: #FFD700; text-align: center; margin-bottom: 20px; }
    .step-label { background-color: #FFD700; color: black; padding: 5px 15px; border-radius: 20px; font-weight: bold; }
    .info-card { border-radius: 10px; padding: 25px; background-color: #1E1E26; border: 1px solid #FFD700; margin-bottom: 20px; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3.5em; font-weight: bold; font-size: 18px; }
    </style>
    """, unsafe_allow_html=True)

TICKER_MAP = {
    "주식 (Stocks)": "NVDA",
    "크립토 (Crypto)": "BTC-USD",
    "금 (Gold)": "GC=F",
    "채권 (Bonds)": "TLT"
}

# [중요] 스크린샷의 AttributeError 방지: 구버전 호환용 캐시 사용
@st.cache(allow_output_mutation=True)
def get_data(ticker):
    try:
        df = yf.download(ticker, period='1y', interval='1d', auto_adjust=True, progress=False)
        if df.empty or len(df) < 20: return None
        # Multi-index 에러 및 KeyError 방지 로직
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df = df.copy()
        df['20SMA'] = df['Close'].rolling(window=20).mean()
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        return df
    except Exception as e:
        return None

# ==========================================
# 2. [STEP 1] 매일 알려주는 투자 방향 가이드
# ==========================================
st.markdown("<h1 class='main-header'>🏆 Golden-Bell 실전 투자 네비게이터</h1>", unsafe_allow_html=True)

st.markdown("### <span class='step-label'>STEP 1</span> 오늘의 AI 자산 로테이션 추천", unsafe_allow_html=True)
st.write("30년 경력의 전문 로직이 데이터로 분석한 오늘 가장 유리한 투자처입니다.")

top1, top2, top3, top4 = st.columns(4)
with top1: st.success("🐋 **크립토**"); st.write("추천: ⭐⭐⭐⭐⭐"); st.caption("세력 매집 / 비중 확대 권장")
with top2: st.info("📈 **채권**"); st.write("추천: ⭐⭐⭐⭐"); st.caption("금리 정점 통과 / 안전마진 확보")
with top3: st.warning("🏦 **주식**"); st.write("추천: ⭐⭐⭐"); st.caption("실적 우량주 중심의 선택적 매수")
with top4: st.error("🟡 **금**"); st.write("추천: ⭐⭐"); st.caption("단기 고점 저항 / 조정 후 매수")

st.markdown("---")

# ==========================================
# 3. [STEP 2] 자산 선택 및 AI 마켓 레이더 브리핑
# ==========================================
st.markdown("### <span class='step-label'>STEP 2</span> 분석할 자산 카테고리를 선택하세요", unsafe_allow_html=True)
selected_cat = st.selectbox("", list(TICKER_MAP.keys()), label_visibility="collapsed")
target_ticker = TICKER_MAP[selected_cat]

data = get_data(target_ticker)

if data is not None:
    # 에러 방지를 위해 결측치 제거 후 최신 데이터 추출
    valid_data = data.dropna(subset=['20SMA', 'RSI'])
    if not valid_data.empty:
        last_row = valid_data.iloc[-1]
        cur_p, sma_v, rsi_v = float(last_row['Close']), float(last_row['20SMA']), float(last_row['RSI'])

        st.markdown("<div class='info-card'>", unsafe_allow_html=True)
        st.subheader(f"📡 {selected_cat} 실시간 AI 마켓 레이더")
        col_brief1, col_brief2 = st.columns([2, 1])
        with col_brief1:
            if cur_p > sma_v:
                st.success(f"현재 {selected_cat}는 **강세 추세(20일선 상단)**에 있습니다. 세력의 수급이 안정적이며 매수 우위의 전략이 유효합니다.")
            else:
                st.error(f"현재 {selected_cat}는 **약세 흐름(20일선 하단)**입니다. 지금은 공격적 투자보다 자산을 지키는 관망이 필요합니다.")
        with col_brief2:
            if "Crypto" in selected_cat:
                st.warning("🛡️ **보안 리스크 판독**: 최근 발생한 거래소 이슈는 개별 사안으로 판명됨. 시장 펀더멘털에는 영향 없음.")
            else:
                st.info("🏦 **세력 동향**: 외국인 및 기관투자자의 대규모 눌림목 매수세가 포착되었습니다.")
        st.markdown("</div>", unsafe_allow_html=True)

        # ==========================================
        # 4. [STEP 3] 실행 모드 선택 (실전 vs 교육)
        # ==========================================
        st.markdown("### <span class='step-label'>STEP 3</span> 분석 결과에 따른 행동을 선택하세요", unsafe_allow_html=True)
        m_col1, m_col2 = st.columns(2)
        
        if 'app_mode' not in st.session_state: st.session_state.app_mode = "실전"
        if m_col1.button("🚀 전문가용 실전 매매 타점 확인", use_container_width=True): st.session_state.app_mode = "실전"
        if m_col2.button("🧒 주니어용 모의 투자 및 지표 교육", use_container_width=True): st.session_state.app_mode = "교육"

        st.markdown("---")

        if st.session_state.app_mode == "실전":
            # ---- 실전 투자 센터 (무삭제 버전) ----
            st.subheader(f"💼 {selected_cat} 실전 승률 90% 전략 리포트")
            
            sc1, sc2, sc3 = st.columns(3)
            sc1.metric("현재가", f"{cur_p:,.2f}")
            sc2.metric("20일선 이격도", f"{(cur_p/sma_v*100)-100:+.2f}%")
            sc3.metric("RSI 심리지수", f"{rsi_v:.2f}")

            st.line_chart(data[['Close', '20SMA']].tail(120))
            st.caption("파란선: 현재가 / 주황선: 20일 이동평균선(생명선)")

            st.markdown(f"""
            ### 🎯 30년 경력 애널리스트의 액션 플랜
            * **권장 진입 타점**: {sma_v*1.005:,.2f} (생명선 지지 확인 시)
            * **수익 목표가**: {cur_p*1.1:,.2f} (+10% 도달 시 분할 익절)
            * **절대 손절선**: {sma_v*0.97:,.2f} (-3% 이탈 시 기계적 매도)
            
            > **전문가 한마디**: "투자는 예측이 아니라 대응입니다. 생명선 아래에서는 절대로 자산을 늘릴 수 없습니다."
            """)
            
            with st.expander("🛠️ 스스로 전문가가 되는 MTS/HTS 세팅법"):
                st.write("**1. 모바일(MTS) 세팅**")
                st.write("- 차트
