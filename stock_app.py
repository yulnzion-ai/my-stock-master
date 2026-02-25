import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# 1. 기본 설정 (버전 호환성 확보)
st.set_page_config(page_title="Golden-Bell Asset Master", layout="wide")

TICKER_MAP = {
    "주식 (Stocks)": "NVDA",
    "크립토 (Crypto)": "BTC-USD",
    "금 (Gold)": "GC=F",
    "채권 (Bonds)": "TLT"
}

@st.cache(allow_output_mutation=True) # 구버전 streamlit 호환용
def get_data(ticker):
    try:
        # 최근 yfinance 업데이트 대응: auto_adjust=True 추가
        df = yf.download(ticker, period='1y', interval='1d', auto_adjust=True, progress=False)
        if df.empty or len(df) < 20:
            return None
        
        # 데이터 형식 강제 단순화 (에러 방지)
        df = df.copy()
        
        # 보조지표 계산
        df['20SMA'] = df['Close'].rolling(window=20).mean()
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        return df
    except Exception as e:
        return None

def get_trading_signal(current_price, sma20, rsi):
    # 모든 값을 순수 숫자로 변환하여 비교 에러 방지
    cur = float(current_price)
    sma = float(sma20)
    r = float(rsi)
    
    signal = {"action": "관망", "color": "gray", "desc": "신호 대기 중입니다."}
    
    if cur > sma * 1.01:
        if r < 70:
            signal = {"action": "매수 우위", "color": "green", "desc": "상승 추세입니다."}
        else:
            signal = {"action": "과열", "color": "orange", "desc": "분할 매도를 고려하세요."}
    elif cur < sma * 0.99:
        signal = {"action": "매도 우위", "color": "red", "desc": "하락 추세입니다."}
            
    return signal

# 2. UI 구성
with st.sidebar:
    st.title("🏆 Golden-Bell 센터")
    mode = st.radio("모드 선택", ["🧒 주니어 경제 학교", "💼 프로 투자 센터 (실전)"], index=1)
    selected_asset = st.selectbox("분석 대상 자산", list(TICKER_MAP.keys()))
    target_ticker = TICKER_MAP[selected_asset]

data = get_data(target_ticker)

if data is None:
    st.error("📉 데이터를 불러오지 못했거나 분석을 위한 최소 기간(20일)이 부족합니다. 잠시 후 다시 시도해주세요.")
else:
    # 에러 방지를 위해 마지막 행의 유효 데이터 추출
    valid_data = data.dropna(subset=['20SMA', 'RSI'])
    
    if valid_data.empty:
        st.warning("분석 지표 생성 중입니다. 데이터 양이 충분하지 않습니다.")
    else:
        last_row = valid_data.iloc[-1]
        cur_p = float(last_row['Close'])
        sma_v = float(last_row['20SMA'])
        rsi_v = float(last_row['RSI'])
        
        if mode == "🧒 주니어 경제 학교":
            st.title("🎮 주니어 경제 탐험대")
            st.metric("가상 시드머니", "1,000,000 원")
            st.line_chart(data['Close'])
        else:
            st.title("🚀 프로 투자 센터")
            
            # 상단 대시보드
            col1, col2, col3 = st.columns(3)
            col1.metric("현재가", f"{cur_p:,.2f}")
            col2.metric("20일선 이격도", f"{(cur_p/sma_v*100)-100:+.2f}%")
            col3.metric("RSI 지수", f"{rsi_v:.2f}")
            
            # 매매 신호
            sig = get_trading_signal(cur_p, sma_v, rsi_v)
            st.subheader(f"🎯 전략 신호: :{sig['color']}[{sig['action']}]")
            st.info(sig['desc'])
            
            # 차트
            st.subheader("📊 기술적 분석 차트")
            st.line_chart(data[['Close', '20SMA']].tail(100))

            # 교육 가이드
            with st.expander("🛠️ 실전 매매 가이드"):
                st.write("1. 주가가 **주황색 선(20일선)** 위에 있을 때만 매수하세요.")
                st.write("2. RSI가 70을 넘으면 욕심을 버리고 수익을 챙기세요.")
