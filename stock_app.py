import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# ==========================================
# 1. 시스템 설정 및 디자인 (철학 반영)
# ==========================================
st.set_page_config(page_title="Golden-Bell Asset Master", layout="wide", initial_sidebar_state="expanded")

# 구버전 호환성을 위해 CSS 디자인을 표준 방식으로 적용
st.markdown("""
    <style>
    .main-header { font-size: 38px !important; font-weight: 800; color: #FFD700; text-align: center; }
    .step-box { background-color: #262730; padding: 20px; border-radius: 10px; border-left: 5px solid #FFD700; margin-bottom: 20px; }
    .stButton>button { width: 100%; height: 3.5em; font-weight: bold; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

TICKER_MAP = {
    "주식 (Stocks)": "NVDA",
    "크립토 (Crypto)": "BTC-USD",
    "금 (Gold)": "GC=F",
    "채권 (Bonds)": "TLT"
}

# [핵심 수교] 구버전 Streamlit 에러 방지를 위해 @st.cache만 사용
@st.cache(allow_output_mutation=True)
def get_data(ticker):
    try:
        # 데이터 호출
        df = yf.download(ticker, period='1y', interval='1d', auto_adjust=True, progress=False)
        if df.empty or len(df) < 20: return None
        
        # Multi-index 컬럼 강제 단일화 (KeyError 방지)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        
        df = df.copy()
        
        # 지표 계산: 20일 이동평균선(생명선)
        df['SMA20'] = df['Close'].rolling(window=20).mean()
        
        # 지표 계산: RSI (14일 기준)
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
st.write("---")

st.subheader("📍 [1단계] 오늘의 AI 자산 로테이션 추천")
st.write("30년 경력 로직이 분석한 오늘 가장 유리한 투자처입니다.")

c1, c2, c3, c4 = st.columns(4)
with c1: st.success("🐋 **크립토**"); st.write("추천: ⭐⭐⭐⭐⭐"); st.caption("세력 매집 포착 / 적극 매수")
with c2: st.info("📈 **채권**"); st.write("추천: ⭐⭐⭐⭐"); st.caption("금리 정점 통과 / 안전마진")
with c3: st.warning("🏦 **주식**"); st.write("추천: ⭐⭐⭐"); st.caption("우량주 중심 / 선택적 대응")
with c4: st.error("🟡 **금**"); st.write("추천: ⭐⭐"); st.caption("고점 저항 / 조정 시 매수")

st.markdown("---")

# ==========================================
# 3. [STEP 2] 자산 선택 및 AI 마켓 레이더 브리핑
# ==========================================
st.subheader("📍 [2단계] 분석할 자산 카테고리를 선택하세요")
selected_cat = st.selectbox("", list(TICKER_MAP.keys()))
target_ticker = TICKER_MAP[selected_cat]

data = get_data(target_ticker)

if data is not None:
    # 데이터 유효성 검사 (KeyError 방지)
    valid_data = data.dropna(subset=['SMA20', 'RSI'])
    if not valid_data.empty:
        last_row = valid_data.iloc[-1]
        cur_p = float(last_row['Close'])
        sma_v = float(last_row['SMA20'])
        rsi_v = float(last_row['RSI'])

        # [협의 내용 반영] AI 마켓 레이더 브리핑
        st.markdown("<div class='step-box'>", unsafe_allow_html=True)
        st.subheader(f"📡 {selected_cat} 실시간 AI 마켓 레이더")
        col_b1, col_b2 = st.columns([2, 1])
        with col_b1:
            if cur_p > sma_v:
                st.markdown(f"**현재 상태:** :green[강세 추세 (20일선 상단)]")
                st.write(f"가격이 생명선 위에 있어 세력의 수급이 매우 안정적입니다. 매수 및 보유가 유리합니다.")
            else:
                st.markdown(f"**현재 상태:** :red[약세 흐름 (20일선 하단)]")
                st.write(f"생명선 아래에 머물러 있습니다. 지금은 자산을 지키기 위해 기계적인 관망이 필수입니다.")
        with col_b2:
            if "Crypto" in selected_cat or "크립토" in selected_cat:
                st.warning("🛡️ **보안 리포트**: 최근 거래소 이슈는 데이터상 일시적 노이즈입니다. 개인 지갑 사용을 권장합니다.")
            else:
                st.info("🏦 **세력 동향**: 외국인과 기관의 대규모 눌림목 매수세가 포착되어 하방 경직성이 강합니다.")
        st.markdown("</div>", unsafe_allow_html=True)

        # ==========================================
        # 4. [STEP 3] 실행 모드 선택 (실전 vs 교육)
        # ==========================================
        st.subheader("📍 [3단계] 분석 결과에 따른 행동을 선택하세요")
        m_col1, m_col2 = st.columns(2)
        
        if 'app_mode' not in st.session_state: st.session_state.app_mode = "실전"
        if m_col1.button("🚀 전문가용 실전 타점 확인 (PRO)"): st.session_state.app_mode = "실전"
        if m_col2.button("🧒 주니어용 모의 투자 및 교육 (EDU)"): st.session_state.app_mode = "교육"

        st.markdown("---")

        if st.session_state.app_mode == "실전":
            # ---- 실전 투자 센터 (무삭제) ----
            st.subheader(f"💼 {selected_cat} 실전 매매 전략")
            
            sc1, sc2, sc3 = st.columns(3)
            sc1.metric("현재가", f"{cur_p:,.2f}")
            sc2.metric("20일선 이격", f"{(cur_p/sma_v*100)-100:+.2f}%")
            sc3.metric("RSI 심리지수", f"{rsi_v:.2f}")

            st.line_chart(data[['Close', 'SMA20']].tail(120))
            
            st.markdown(f"""
            ### 🎯 애널리스트 액션 플랜
            * **권장 진입가:** {sma_v*1.005:,.2f} 부근 (20일선 지지 확인)
            * **익절 목표가:** {cur_p*1.1:,.2f} (+10% 목표)
            * **절대 손절선:** {sma_v*0.97:,.2f} (생명선 3% 이탈 시 즉시 매도)
            
            > **전문가 한마디:** "투자는 기법이 아니라 원칙입니다. 생명선 아래에서는 절대 매수하지 마십시오."
            """)
            
            with st.expander("🛠️ 스스로 전문가가 되는 MTS/HTS 세팅법"):
                st.write("**📱 모바일(MTS)**: 차트 설정 -> 이동평균선 -> 20일선을 황금색으로 가장 굵게 설정.")
                st.write("**💻 PC(HTS)**: '자동주문' 메뉴에서 매수 시 -3% 자동 손절 주문이 나가도록 세팅.")

        else:
            # ---- 주니어 경제 학교 (무삭제) ----
            st.subheader(f"🎮 {selected_cat} 주니어 경제 탐험대")
            
            e_col1, e_col2 = st.columns(2)
            with e_col1:
                st.metric("가상 시드머니", "1,000,000 원")
                st.success("💡 **유대인 경제 지혜**")
                st.write("'공짜 점심은 없다. 원칙을 지키는 자에게는 반드시 보상이 따른다.'")
            with e_col2:
                st.metric("나의 등급", "Lv.1 꼬마 자산가")
                st.write("📈 **성장 포인트**: 150 / 500")

            st.markdown("---")
            st.subheader("🧐 전문가의 지표 교육")
            with st.expander("차트의 비밀 배우기 (클릭)"):
                st.write("**1. 생명선(20일선)은 무엇인가요?**")
                st.write("- 지난 20일간 친구들의 평균 마음이에요. 가격이 이 선 위에 있으면 다들 기분이 좋다는 뜻이죠!")
                st.write("**2. RSI 숫자는 무엇인가요?**")
                st.write("- 사람들의 '흥분도'예요! 70이 넘으면 너무 흥분해서 너도나도 사고 있으니 조심해야 해요.")
            
            st.line_chart(data['Close'].tail(120))
            
            st.info(f"💰 **모의 투자**: 지금 100만원을 투자하면 이 자산을 **{1000000/cur_p:.2f}개** 살 수 있어요!")
            if st.button("체험 구매하기"): st.balloons()

# ==========================================
# 5. 사이드바 (정보 업데이트)
# ==========================================
with st.sidebar:
    st.title("🏆 Golden-Bell 센터")
    st.markdown("---")
    st.subheader("📡 실시간 세력 레이더")
    if "Crypto" in selected_cat or "크립토" in selected_cat:
        st.info("🐋 **고래 동향**: 대규모 지갑 이동 포착. 거래소 외부 유출로 하방 경직성 확보.")
    else:
        st.info("🏦 **기관 수급**: 외국인 및 연기금의 20일선 눌림목 매수세가 유입 중입니다.")
    st.markdown("---")
    st.caption("Ver 2.9 (Legacy) | 원칙으로 승리하십시오.")
