import streamlit as st
import yfinance as yf
import pandas as pd
import datetime

# 2. 앱 레이아웃 설정
st.set_page_config(page_title="Emergent Stock Analyzer", layout="wide")

st.title("🚀 Emergent 실시간 주식 분석 대시보드")
st.markdown("데이터를 통해 시장의 흐름을 분석합니다.")

# 3. 사이드바 - 설정 창
with st.sidebar:
    st.header("🔍 설정")
    ticker = st.text_input("종목 코드 입력", "AAPL")
    start_date = st.date_input("시작 날짜", datetime.date(2023, 1, 1))
    end_date = st.date_input("종료 날짜", datetime.date.today())

# 4. 데이터 불러오기 및 그래프 출력
if ticker:
    data = yf.download(ticker, start=start_date, end=end_date)
    
    if not data.empty:
        # 지표 계산
        col1, col2, col3 = st.columns(3)
        current_price = data['Close'].iloc[-1]
        change = current_price - data['Close'].iloc[-2]
        
        
        col1.metric("현재가", f"${current_price.item():,.2f}", f"{change.item():+.2f}")
        col2.metric("최고가 (기간 내)", f"${data['High'].max().item():,.2f}")
        col3.metric("거래량", f"{data['Volume'].iloc[-1].item():,}")

        # 메인 그래프
        st.subheader(f"{ticker} 주가 흐름 (Line Chart)")
        st.line_chart(data['Close'])
        
        # 데이터 표
        with st.expander("상세 데이터 보기"):
            st.write(data.tail(10))
    else:
        st.error("데이터를 찾을 수 없습니다. 종목 코드를 다시 확인해 주세요.")