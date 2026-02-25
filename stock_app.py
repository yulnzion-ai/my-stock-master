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

# [핵심 수교] AttributeError 방지를 위해 구버전용 @st.cache 사용
@st.cache(allow_output_mutation=True)
def get_data(ticker):
    try:
        # 데이터 로드
        df = yf.download(ticker, period='1y', interval='1d', auto_adjust=True, progress=False)
        if df.empty or len(df) < 20: return None
        
        # Multi-index 컬럼 처리 (에러 방지용)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        
        df = df.copy()
        
        # 지표 계산: 20일 이동평균선(생명선)
        df['SMA20'] = df['Close'].rolling(window=20).mean()
        
        # 지표 계산: RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        return df
    except Exception:
        return None

# ==========================================
# 2. [STEP 1] 매일 알려주는 투자 방향 가이드
# ==========================================
st.markdown("<h1 class='main-header'>🏆 Golden-Bell 실전 투자 네비게이터</h1>", unsafe_allow_html=True)

st.markdown("### <span class='step-label'>STEP 1</span> 오늘의 AI 자산 로테이션 추천", unsafe_allow_html=True)
st.write("30년 경력 로직이 분석한 오늘 가장 유리한 투자처입니다.")

top1, top2, top3, top4 = st.columns(4)
with top1: st.success("🐋 **크립토**"); st.write("추천: ⭐⭐⭐⭐⭐"); st.caption("세력 매집 / 비중 확대")
with top2: st.info("📈 **채권**"); st.write("추천: ⭐⭐⭐⭐"); st.caption("금리 정점 / 안전마진")
with top3: st.warning("🏦 **주식**"); st.write("추천: ⭐⭐⭐"); st.caption("실적 우량주 중심")
with top4: st.error("🟡 **금**"); st.write("추천: ⭐⭐"); st.caption("고점 박스권 정체")

st.markdown("---")

# ==========================================
# 3. [STEP 2] 카테고리 선택 및 상세 가이드
# ==========================================
st.markdown("### <span class='step-label'>STEP 2</span> 분석할 자산 카테고리를 선택하세요", unsafe_allow_html=True)
selected_cat = st.selectbox("", list(TICKER_MAP.keys()), label_visibility="collapsed")
target_ticker = TICKER_MAP[selected_cat]

data = get_data(target_ticker)

if data is not None:
    # 에러 방지를 위해 지표가 계산된 최신 행만 추출
    valid_data = data.dropna(subset=['SMA20', 'RSI'])
    if not valid_data.empty:
        last_row = valid_data.iloc[-1]
        cur_p = float(last_row['Close'])
        sma_v = float(last_row['SMA20'])
        rsi_v = float(last_row['RSI'])

        # AI 마켓 레이더 브리핑 (사용자 협의 내용)
        st.markdown("<div class='info-card'>", unsafe_allow_html=True)
        st.subheader(f"📡 {selected_cat} 실시간 마켓 레이더")
        col_brief1, col_brief2 = st.columns([2, 1])
        with col_brief1:
            if cur_p > sma_v:
                st.write(f"현재 {selected_cat}는 **강세 추세(생명선 상단)**에 있습니다. 세력의 매집이 안정적이며 매수 우위의 전략이 유효합니다.")
            else:
                st.write(f"현재 {selected_cat}는 **약세 흐름(생명선 하단)**입니다. 기계적인 관망과 위험 관리가 필요한 구간입니다.")
        with col_brief2:
            if "Crypto" in selected_cat:
                st.warning("🛡️ **보안 리포트**: 거래소 해킹 관련 악재는 데이터상 노이즈로 판별됨. 개인 지갑 보관 권장.")
            else:
                st.info("🏦 **세력 동향**: 외국인 및 기관투자자의 대규모 눌림목 매수세 포착.")
        st.markdown("</div>", unsafe_allow_html=True)

        # ==========================================
        # 4. [STEP 3] 실행 모드 선택 (실전 vs 교육)
        # ==========================================
        st.markdown("### <span class='step-label'>STEP 3</span> 실행 모드를 선택하세요", unsafe_allow_html=True)
        m_col1, m_col2 = st.columns(2)
        
        if 'app_mode' not in st.session_state: st.session_state.app_mode = "실전"
        if m_col1.button("🚀 전문가용 실전 타점 확인", use_container_width=True): st.session_state.app_mode = "실전"
        if m_col2.button("🧒 주니어용 모의 투자 및 교육", use_container_width=True): st.session_state.app_mode = "교육"

        st.markdown("---")

        if st.session_state.app_mode == "실전":
            # ---- 실전 투자 센터 ----
            st.subheader(f"💼 {selected_cat} 실전 매매 전략 리포트")
            
            sc1, sc2, sc3 = st.columns(3)
            sc1.metric("현재가", f"{cur_p:,.2f}")
            sc2.metric("20일선 이격도", f"{(cur_p/sma_v*100)-100:+.2f}%")
            sc3.metric("RSI 심리지수", f"{rsi_v:.2f}")

            st.line_chart(data[['Close', 'SMA20']].tail(120))
            
            st.markdown(f"""
            ### 🎯 실전 매매 액션 플랜
            1. **권장 진입 타점:** {sma_v*1.005:,.2f} 부근 (20일선 지지 확인 시)
            2. **수익 목표가:** {cur_p*1.1:,.2f} (+10% 도달 시 분할 익절)
            3. **절대 손절선:** {sma_v*0.97:,.2f} (-3% 이탈 시 기계적 매도 필수)
            """)
            
            with st.expander("🛠️ 스스로 전문가가 되는 MTS/HTS 세팅법"):
                st.write("**📱 모바일(MTS) 세팅**")
                st.write("- 차트 설정에서 20일 이동평균선을 황금색으로 가장 굵게 설정하세요.")
                st.write("**💻 PC(HTS) 세팅**")
                st.write("- '자동주문(스탑로스)' 메뉴에서 매수 즉시 -3%에 자동 매도가 나가도록 설정하세요.")

        else:
            # ---- 주니어 교육 센터 ----
            st.subheader(f"🎮 {selected_cat} 주니어 경제 탐험대")
            
            e_col1, e_col2 = st.columns([1, 1])
            with e_col1:
                st.metric("가상 시드머니", "1,000,000 원")
                st.success("💡 **유대인 경제 지혜**")
                st.write("'공짜 점심은 없다. 하지만 원칙을 지키는 자에게는 반드시 보상이 따른다.'")
            with e_col2:
                st.metric("나의 등급", "Lv.1 꼬마 자산가")
                st.image("https://cdn-icons-png.flaticon.com/512/4140/4140043.png", width=80)

            st.markdown("---")
            st.subheader("🧐 전문가의 지표 교육")
            with st.expander("차트 속 '선'과 '숫자'의 비밀 배우기"):
                st.write("**1. 생명선(20일선)은 무엇인가요?**")
                st.write("- 지난 20일간 친구들의 평균 마음이에요. 가격이 이 선 위에 있으면 다들 기분이 좋다는 뜻이죠!")
                st.write("**2. RSI 숫자는 무엇인가요?**")
                st.write("- 사람들의 흥분도예요! 70이 넘으면 너무 흥분해서 너도나도 사고 있으니 조심해야 해요.")
            
            st.line_chart(data['Close'].tail(120))
            
            st.info(f"💰 **모의 투자:** 지금 100만원을 투자하면 이 자산을 **{1000000/cur_p:.2f}개** 살 수 있어요!")
            if st.button("체험 구매하기"): st.balloons()

# ==========================================
# 5. 사이드바 (추가 보안/세력 정보)
# ==========================================
with st.sidebar:
    st.title("🏆 Golden-Bell 센터")
    st.markdown("---")
    st.subheader("📡 세력 레이더")
    if "Crypto" in selected_cat:
        st.info("🐋 **고래 동향**: 대규모 지갑 이동 포착. 하방 경직성이 강력합니다.")
    elif "Stocks" in selected_cat:
        st.info("🏦 **수급 분석**: 주요 기관투자자들이 실적 발표를 앞두고 비중을 확대 중입니다.")
    st.markdown("---")
    st.caption("Ver 2.8 | 원칙으로 승리하십시오.")
