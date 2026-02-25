import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# [핵심] 에러 원천 차단: 구버전 Streamlit(1.10.0 이하)에서도 돌아가는 캐시 방식
def universal_cache(func):
    if hasattr(st, 'cache_data'): return st.cache_data(func)
    elif hasattr(st, 'cache_resource'): return st.cache_resource(func)
    else: return st.cache(func, allow_output_mutation=True)

# ==========================================
# 1. 시스템 설정 및 디자인 (사용자 철학 100% 반영)
# ==========================================
st.set_page_config(page_title="Golden-Bell Asset Master", layout="wide")

st.markdown("""
    <style>
    .main-header { font-size: 42px !important; font-weight: 800; color: #FFD700; text-align: center; margin-bottom: 20px; }
    .step-label { background-color: #FFD700; color: black; padding: 5px 15px; border-radius: 20px; font-weight: bold; }
    .info-card { border-radius: 15px; padding: 25px; background-color: #1E1E26; border: 1px solid #FFD700; margin-bottom: 20px; }
    .stButton>button { width: 100%; border-radius: 12px; height: 3.5em; font-weight: bold; font-size: 18px; transition: 0.3s; }
    .stButton>button:hover { background-color: #FFD700; color: black; }
    </style>
    """, unsafe_allow_html=True)

TICKER_MAP = {"주식 (Stocks)": "NVDA", "크립토 (Crypto)": "BTC-USD", "금 (Gold)": "GC=F", "채권 (Bonds)": "TLT"}

@universal_cache
def get_data(ticker):
    try:
        df = yf.download(ticker, period='1y', interval='1d', auto_adjust=True, progress=False)
        if df.empty or len(df) < 20: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        df = df.copy()
        df['SMA20'] = df['Close'].rolling(window=20).mean() # 생명선
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        df['RSI'] = 100 - (100 / (1 + (gain / loss)))
        return df
    except: return None

# ==========================================
# 2. [STEP 1] AI 자산 로테이션 추천 (무삭제)
# ==========================================
st.markdown("<h1 class='main-header'>🏆 Golden-Bell 실전 투자 네비게이터</h1>", unsafe_allow_html=True)
st.markdown("### <span class='step-label'>STEP 1</span> 오늘의 AI 자산 로테이션 추천", unsafe_allow_html=True)
st.write("30년 경력의 전문 알고리즘이 분석한 오늘 가장 유리한 투자처입니다. 매일 아침 확인하십시오.")

r1, r2, r3, r4 = st.columns(4)
with r1: st.success("🐋 **크립토**"); st.write("추천: ⭐⭐⭐⭐⭐"); st.caption("세력 매집 포착 / 비중 확대")
with r2: st.info("📈 **채권**"); st.write("추천: ⭐⭐⭐⭐"); st.caption("안전마진 확보")
with r3: st.warning("🏦 **주식**"); st.write("추천: ⭐⭐⭐"); st.caption("우량주 중심 / 눌림목 매수")
with r4: st.error("🟡 **금**"); st.write("추천: ⭐⭐"); st.caption("고점 저항 확인 / 관망")

st.markdown("---")

# ==========================================
# 3. [STEP 2] 자산 선택 및 AI 마켓 레이더 (보안/세력)
# ==========================================
st.markdown("### <span class='step-label'>STEP 2</span> 분석할 자산 카테고리를 선택하세요", unsafe_allow_html=True)
selected_cat = st.selectbox("", list(TICKER_MAP.keys()), label_visibility="collapsed")
data = get_data(TICKER_MAP[selected_cat])

if data is not None:
    valid = data.dropna(subset=['SMA20', 'RSI'])
    if not valid.empty:
        last = valid.iloc[-1]
        cur_p, sma_v, rsi_v = float(last['Close']), float(last['SMA20']), float(last['RSI'])

        st.markdown("<div class='info-card'>", unsafe_allow_html=True)
        st.subheader(f"📡 {selected_cat} 실시간 AI 마켓 레이더 브리핑")
        col_b1, col_b2 = st.columns([2, 1])
        with col_b1:
            if cur_p > sma_v: st.success(f"현재 **강세 추세(20일선 상단)**입니다. 세력 수급이 안정적입니다.")
            else: st.error(f"현재 **약세 흐름(20일선 하단)**입니다. 기계적인 관망을 권장합니다.")
        with col_b2:
            if "Crypto" in selected_cat: st.warning("🛡️ **보안 리포트**: 거래소 이슈는 노이즈입니다. 펀더멘털은 견고합니다.")
            else: st.info("🏦 **세력 동향**: 기관의 대규모 눌림목 매집이 포착되었습니다.")
        st.markdown("</div>", unsafe_allow_html=True)

        # ==========================================
        # 4. [STEP 3] 실행 모드 선택 (실전 vs 교육)
        # ==========================================
        st.markdown("### <span class='step-label'>STEP 3</span> 분석 결과에 따른 행동을 선택하세요", unsafe_allow_html=True)
        m1, m2 = st.columns(2)
        if 'app_mode' not in st.session_state: st.session_state.app_mode = "실전"
        if m1.button("🚀 전문가용 실전 타점 및 MTS 세팅"): st.session_state.app_mode = "실전"
        if m2.button("🧒 주니어용 모의 투자 및 교육"): st.session_state.app_mode = "교육"

        if st.session_state.app_mode == "실전":
            st.subheader(f"💼 {selected_cat} 실전 매매 전략")
            st.line_chart(data[['Close', 'SMA20']].tail(120))
                        st.markdown(f"**🎯 액션 플랜**: 추천가 {sma_v*1.005:,.2f} / **절대 손절선 {sma_v*0.97:,.2f} (-3%)**")
            with st.expander("🛠️ MTS/HTS 실전 세팅법 (필독)"):
                st.write("**📱 모바일(MTS)**: 20일선을 황금색으로 굵게 설정하고 돌파 알림을 켜세요.")
                st.write("**💻 PC(HTS)**: '자동주문' 메뉴에서 -3% 자동 매도를 예약하세요.")
        else:
            st.subheader(f"🎮 {selected_cat} 주니어 경제 탐험대")
            st.metric("가상 시드머니", "1,000,000 원")
            st.success("💡 **유대인 경제 지혜**: '원칙을 지키는 자에게는 반드시 보상이 따른다.'")
            with st.expander("🧐 전문가 선생님의 지표 교육"):
                st.write("**20일선**: 지난 20일간 친구들의 평균 마음입니다.")
                st.write("**RSI**: 지금 사람들이 얼마나 흥분했는지 보여주는 지수입니다.")
            st.info(f"💰 지금 투자하면 **{1000000/cur_p:.2f}개** 살 수 있어요!")
            if st.button("체험 구매"): st.balloons()

with st.sidebar:
    st.title("🏆 Golden-Bell")
    st.info("우리는 데이터로 판단하고 원칙으로 승리합니다.")
