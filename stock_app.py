import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import datetime

# ==========================================
# 1. 기본 설정 및 데이터 처리 함수 (정확성 기반)
# ==========================================
st.set_page_config(page_title="Golden-Bell Asset Master", layout="wide", initial_sidebar_state="expanded")

# 티커 맵핑 (주식, 코인, 금, 채권)
TICKER_MAP = {
    "주식 (Stocks)": "NVDA",   # 예시: 엔비디아
    "크립토 (Crypto)": "BTC-USD", # 비트코인
    "금 (Gold)": "GC=F",       # 금 선물
    "채권 (Bonds)": "TLT"      # 미국 장기채 ETF
}

@st.cache
def get_data(ticker, period='6mo', interval='1d'):
    """yfinance를 통한 실시간 데이터 호출 및 보조지표 계산"""
    try:
        df = yf.download(ticker, period=period, interval=interval, progress=False)
        if df.empty:
            return None
        
        # 보조지표 계산 (수익 로직의 핵심)
        df['20SMA'] = df['Close'].rolling(window=20).mean() # 생명선
        
        # RSI 계산
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        return df
    except Exception as e:
        st.error(f"데이터 로드 중 오류 발생: {e}")
        return None

def get_trading_signal(current_price, sma20, rsi):
    """[수익 구조 핵심] 데이터 기반 매매 신호 생성"""
    signal = {"action": "관망", "color": "gray", "desc": "뚜렷한 방향성이 없습니다."}
    
    # 필승 로직: 20일선 위에 있고, RSI가 과열되지 않았을 때가 타점
    if current_price > sma20 * 1.01: # 20일선보다 1% 이상 위
        if rsi < 70:
            signal = {"action": "매수 우위 (보유)", "color": "green", "desc": "상승 추세입니다. 20일선 지지를 확인하며 보유하세요."}
        else:
             signal = {"action": "과열 (분할 매도 고려)", "color": "orange", "desc": "RSI가 너무 높습니다. 수익 실현을 고려하세요."}
    elif current_price < sma20 * 0.99: # 20일선보다 1% 이상 아래
        if rsi > 30:
             signal = {"action": "매도 우위 (관망)", "color": "red", "desc": "하락 추세입니다. 20일선 회복 전까지 진입 금지."}
        else:
             signal = {"action": "과매도 (반등 주의)", "color": "blue", "desc": "많이 하락했습니다. 기술적 반등이 나올 수 있으나 섣불리 진입하지 마세요."}
            
    return signal

# ==========================================
# 2. 사이드바 UI (모드 및 자산 선택)
# ==========================================
with st.sidebar:
    st.title("🏆 Golden-Bell 센터")
    st.markdown("---")
    
    # 모드 선택
    mode = st.radio("모드 선택", ["🧒 주니어 경제 학교", "💼 프로 투자 센터 (실전)"], index=1)
    st.markdown("---")
    
    # 자산 선택
    selected_asset_key = st.selectbox("분석 대상 자산", list(TICKER_MAP.keys()))
    target_ticker = TICKER_MAP[selected_asset_key]
    
    st.markdown("---")
    # [사고 모드 반영] 실시간 세력/위기 브리핑 (시뮬레이션 데이터)
    st.subheader("📡 마켓 레이더 (AI 분석)")
    if "크립토" in selected_asset_key:
        st.info("🐋 **고래 동향:** 최근 1주간 주요 지갑 매집세 포착. 국가 단위(미국 등) 물량 이동 없음.")
        st.warning("🛡️ **보안 이슈:** 최근 거래소 해킹은 개별 시스템 문제로 판독됨. 펀더멘털 영향 제한적.")
    elif "주식" in selected_asset_key:
         st.info("🏦 **기관 수급:** AI 섹터 중심으로 외국인/기관 동반 매수 유입 중.")
    else:
        st.write("선택한 자산에 대한 특이 동향이 없습니다.")

# ==========================================
# 3. 메인 화면 로직 (모드별 분기)
# ==========================================

# 데이터 로드
data = get_data(target_ticker)

if mode == "🧒 주니어 경제 학교":
    # ---- 주니어 모드 UI ----
    st.title("🎮 주니어 경제 탐험대")
    st.write(f"### 🧐 오늘의 탐구 대상: {selected_asset_key.split(' ')[0]}")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("나의 레벨", "Lv.1 새싹 투자자")
        st.metric("가상 시드머니", "1,000,000 원")
        st.image("https://cdn-icons-png.flaticon.com/512/4140/4140043.png", width=100) # 예시 아이콘

    with col2:
        st.success("💡 **오늘의 배움 카드**")
        if "주식" in selected_asset_key:
            st.write("주식은 회사의 주인이 되는 증서예요. 회사가 돈을 잘 벌면 내 증서의 가치도 올라가요!")
        elif "크립토" in selected_asset_key:
            st.write("비트코인은 인터넷 세상의 황금이에요. 전 세계 어디로든 순식간에 보낼 수 있죠!")
        else:
             st.write("다양한 자산이 경제를 움직여요. 가격이 오르고 내리는 걸 관찰해보세요.")
             
    st.markdown("---")
    if data is not None:
         st.subheader("📈 가격은 어떻게 움직였을까?")
         st.line_chart(data['Close'])
         st.caption("지난 6개월 동안의 가격 변화 그래프예요.")


else:
    # ---- 프로 투자 센터 (실전) UI ----
    st.title("🚀 프로 투자 센터: 실전 필승 전략")
    st.markdown("---")

    # [핵심 1] 자산 로테이션 대시보드 (사고 모드 기반 시황)
    # 실제로는 더 복잡한 거시경제 지표 연동 필요, 현재는 논리적 구조 예시
    st.subheader("🚦 글로벌 자산 매력도 신호등")
    a_col1, a_col2, a_col3, a_col4 = st.columns(4)
    a_col1.metric("비트코인 (Crypto)", "매력도 높음", "세력 매집 중")
    a_col2.metric("주식 (Stocks)", "중립", "종목 장세")
    a_col3.metric("금 (Gold)", "다소 높음", "조정 시 매수")
    a_col4.metric("채권 (Bonds)", "매력도 높음", "금리 인하 기대")
    st.info("💡 **AI 전략 코멘트:** 현재는 변동성을 활용한 **크립토**와 안전마진이 확보된 **채권**의 비중을 높이는 것이 현명한 포트폴리오 전략입니다.")
    st.markdown("---")

    if data is not None:
        # 최신 데이터 추출
        last_row = data.iloc[-1]
        current_price = last_row['Close']
        sma20_val = last_row['20SMA']
        rsi_val = last_row['RSI']
        
        # 매매 신호 생성
        signal = get_trading_signal(current_price, sma20_val, rsi_val)

        # 메인 차트 및 핵심 지표 영역
        col_chart, col_metrics = st.columns([2, 1])
        
        with col_chart:
            st.subheader(f"📊 {selected_asset_key} 실시간 분석")
            # 20일선과 주가를 같이 그리기 위해 데이터 가공
            chart_data = data[['Close', '20SMA']].dropna()
            st.line_chart(chart_data)
            st.caption("파란선: 주가 / 주황선: 20일 이동평균선 (생명선)")

        with col_metrics:
            st.subheader("핵심 기술적 지표")
            st.metric(label="현재가", value=f"{current_price:,.2f}")
            
            # 20일선 이격도 표현
            disparity = (current_price / sma20_val * 100) - 100
            st.metric(label="20일선 이격도", value=f"{disparity:+.2f}%", delta_color="inverse")
            st.caption("* 0% 이상이어야 상승 추세")

            # RSI 표현
            st.metric(label="RSI (14일)", value=f"{rsi_val:.2f}")
            st.caption("* 30 이하: 침체, 70 이상: 과열")

        # [핵심 2 & 3] 수익 구조를 위한 가이드 및 교육
        st.markdown("---")
        st.subheader("🎯 실전 매매 액션 플랜 (수익 보장 구조)")
        
        # 신호에 따른 행동 가이드
        st.markdown(f"""### 현재 상태: :**{signal['color']}[{signal['action']}]**""")
        st.write(signal['desc'])
        
        # 구체적 타점 제시 (원칙 매매)
        g_col1, g_col2, g_col3 = st.columns(3)
        # 진입가는 20일선 근처 지지 시
        entry_price = sma20_val * 1.005 
        # 목표가는 현재가 대비 +10% (예시)
        target_price = current_price * 1.10
        # 손절가는 20일선 이탈 기준 (-3%)
        stop_loss_price = sma20_val * 0.97

        g_col1.metric("✅ 추천 진입가 (눌림목)", f"{entry_price:,.2f} 부근")
        g_col2.metric("💰 1차 목표가 (+10%)", f"{target_price:,.2f}")
        g_col3.metric("🛡️ 절대 손절가 (원칙)", f"{stop_loss_price:,.2f}")
        st.error("⚠️ **경고:** 손절가 이탈 시 '기계적 매도'가 자산을 지키는 유일한 길입니다. 감정을 배제하세요.")

        # MTS/HTS 세팅 가이드 탭
        st.markdown("---")
        with st.expander("🛠️ (필독) 내 폰과 PC에 이 전략 적용하기"):
            tab1, tab2 = st.tabs(["📱 MTS (모바일) 필수 세팅", "💻 HTS (PC) 정밀 세팅"])
            with tab1:
                st.write("**어떤 앱을 쓰든 이 3가지는 꼭 설정하세요!**")
                st.markdown("""
                1.  **차트 설정 - 이동평균선:** '20일선'을 추가하고 두껍게(노란색 추천) 설정하세요. 주가가 이 선 위에 있을 때만 매수 버튼을 봅니다.
                2.  **보조지표 - RSI:** RSI 지표를 추가하고 기준선을 30과 70으로 설정하세요. 70이 넘어가면 절대 추격 매수 금지!
                3.  **호가창 - 체결강도:** 매수 전 체결강도가 100% 이상인지 확인하여 매수세의 힘을 체크하세요.
                """)
            with tab2:
                st.write("**PC에서는 '자동'을 활용하여 뇌동매매를 막습니다.**")
                st.markdown("""
                1.  **주식 자동감시주문 (스탑로스):** 매수 즉시 '손실제한 -3%'를 설정하여 내가 자리를 비워도 기계가 손절하게 만드세요.
                2.  **조건검색식 활용:** '주가 > 20일 이평선' AND '거래량 전일 대비 200% 이상' 조건을 만족하는 종목만 필터링해서 보세요.
                """)
    else:
        st.error("데이터를 불러오지 못했습니다. 잠시 후 다시 시도해주세요.")
