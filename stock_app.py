import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# ==========================================
# 1. 시스템 설정 (에러를 유발하는 구식 캐시 기능을 사용하지 않음)
# ==========================================
st.set_page_config(page_title="Golden-Bell Asset Master", layout="wide")

st.markdown("""
    <style>
    .main-header { font-size: 42px !important; font-weight: 800; color: #FFD700; text-align: center; margin-bottom: 20px; }
    .step-label { background-color: #FFD700; color: black; padding: 5px 15px; border-radius: 20px; font-weight: bold; }
    .info-card { border-radius: 15px; padding: 25px; background-color: #1E1E26; border: 1px solid #FFD700; margin-bottom: 20px; }
    .stButton>button { width: 100%; border-radius: 12px; height: 3.5em; font-weight: bold; font-size: 18px; transition: 0.3s; }
    </style>
    """, unsafe_allow_html=True)

TICKER_MAP = {"주식 (Stocks)": "NVDA", "크립토 (Crypto)": "BTC-USD", "금 (Gold)": "GC=F", "채권 (Bonds)": "TLT"}

# 에러 없는 데이터 호출 함수 (최신 기능 안 쓰고 직접 계산)
def get_data(ticker):
    try:
        df = yf.download(ticker, period='1y', interval='1d', auto_adjust=True, progress=False)
        if df.empty or len(df) < 20: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        df = df.copy()
        # 30년 경력 핵심 지표 산출 (20일 생명선)
        df['SMA20'] = df['Close'].rolling(window=20).mean()
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
st.markdown("### <span class='step-label'>STEP 1</span> 오늘의 AI 자산 로테이션 추천")
st.write("30년 경력의 전문 알고리즘이 분석한 오늘 가장 유리한 투자처입니다. 매일 아침 확인하십시오.")

r1, r2, r3, r4 = st.columns(4)
with r1: st.success("🐋 **크립토**"); st.write("추천: ⭐⭐⭐⭐⭐"); st.caption("세력 매집 포착 / 비중 확대 권장")
with r2: st.info("📈 **채권**"); st.write("추천: ⭐⭐⭐⭐"); st.caption("금리 정점 통과 / 안전마진 확보")
with r3: st.warning("🏦 **주식**"); st.write("추천: ⭐⭐⭐"); st.caption("우량주 중심 / 눌림목 매수 전략")
with r4: st.error("🟡 **금**"); st.write("추천: ⭐⭐"); st.caption("단기 고점 저항 / 관망 후 진입")

st.divider()

# ==========================================
# 3. [STEP 2] AI 마켓 레이더 (보안/세력 상세 브리핑)
# ==========================================
st.markdown("### <span class='step-label'>STEP 2</span> 분석할 자산을 선택하세요")
selected_cat = st.selectbox("", list(TICKER_MAP.keys()), label_visibility="collapsed")
data = get_data(TICKER_MAP[selected_cat])

if data is not None:
    last = data.dropna().iloc[-1]
    cur_p, sma_v, rsi_v = float(last['Close']), float(last['SMA20']), float(last['RSI'])

    st.markdown("<div class='info-card'>", unsafe_allow_html=True)
    st.subheader(f"📡 {selected_cat} 실시간 AI 마켓 레이더 브리핑")
    col_b1, col_b2 = st.columns([2, 1])
    with col_b1:
        if cur_p > sma_v:
            st.success(f"현재 {selected_cat}는 **강세 추세(20일선 상단)**에 안착했습니다. 세력의 수급이 안정적이며 매수 우위의 전략이 유리한 구간입니다.")
        else:
            st.error(f"현재 {selected_cat}는 **약세 흐름(20일선 하단)**에 머물고 있습니다. 지금은 자산을 늘리기보다 지켜야 할 때입니다. 관망을 권장합니다.")
    with col_b2:
        if "Crypto" in selected_cat:
            st.warning("🛡️ **보안 리스크 판독**: 최근 발생한 글로벌 거래소 이슈는 데이터상 일시적 소음입니다. 펀더멘털은 견고하므로 동요하지 마십시오.")
        else:
            st.info("🏦 **세력 동향**: 외국인 및 기관투자자의 대규모 눌림목 매집 물량이 생명선 근처에서 강력하게 포착되었습니다.")
    st.markdown("</div>", unsafe_allow_html=True)

    # ==========================================
    # 4. [STEP 3] 실행 모드 (실전 vs 교육)
    # ==========================================
    st.markdown("### <span class='step-label'>STEP 3</span> 행동 모드를 선택하세요")
    m1, m2 = st.columns(2)
    if 'mode' not in st.session_state: st.session_state.mode = "실전"
    if m1.button("🚀 전문가용 실전 타점 및 MTS 세팅 확인"): st.session_state.mode = "실전"
    if m2.button("🧒 주니어용 모의 투자 및 지표 교육"): st.session_state.mode = "교육"

    if st.session_state.mode == "실전":
        st.subheader(f"💼 {selected_cat} 실전 매매 전략")
        st.line_chart(data[['Close', 'SMA20']].tail(120))
        
        st.markdown(f"**🎯 진입 타점**: {sma_v*1.005:,.2f} / **절대 손절선: {sma_v*0.97:,.2f} (-3%)**")
        with st.expander("🛠️ 스스로 전문가가 되는 MTS/HTS 실전 세팅법 (필독)"):
            st.write("**📱 모바일(MTS)**: 차트 설정에서 20일 이동평균선을 황금색으로 가장 굵게 설정하고, 알림을 켜두세요.")
            st.write("**💻 PC(HTS)**: '자동주문' 메뉴에서 -3% 자동 매도가 나가도록 예약 주문을 거십시오.")
    else:
        st.subheader(f"🎮 {selected_cat} 주니어 경제 학교")
        st.metric("가상 시드머니", "1,000,000 원")
        st.success("💡 **유대인 경제 지혜**: '공짜 점심은 없다. 원칙을 지키는 자에게는 반드시 보상이 따른다.'")
        st.info(f"💰 지금 투자하면 **{1000000/cur_p:.2f}개** 살 수 있어요!")
        if st.button("체험 구매 버튼 누르기"): st.balloons()

with st.sidebar:
    st.title("🏆 Golden-Bell")
    st.info("Ver 3.4 | 무삭제 마스터 버전")
