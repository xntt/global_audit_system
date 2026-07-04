import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import akshare as ak
from datetime import datetime

st.set_page_config(page_title="全球流动性正交审计系统", layout="wide", page_icon="🌐")

st.markdown("""
<style>
    .stApp { background-color: #0E1117; color: #FAFAFA; }
    .high-risk { background-color: #3D1F1F; color: #FF6B6B; }
    .independent { background-color: #1F3D2A; color: #4ADE80; }
    .safe-haven { background-color: #2A3D1F; color: #4ADE80; }
</style>
""", unsafe_allow_html=True)

st.title("🌐 全球流动性正交审计系统（3x杠杆 + 资金流向版）")
st.caption(f"最后更新：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 集成你提供的3倍多空工具清单")

@st.cache_data(ttl=900)
def get_etf_change(ticker):
    try:
        hist = yf.Ticker(ticker).history(period="5d", interval="15m")
        if not hist.empty:
            return round(float(hist['Close'].pct_change().iloc[-1] * 100), 2)
    except:
        pass
    return None

def analyze_with_3x(sector, long_ticker, short_ticker, anchor_note):
    long_chg = get_etf_change(long_ticker)
    short_chg = get_etf_change(short_ticker)
    
    # 简单资金流向判断
    signal = "正常"
    conclusion = "跟随"
    level = "低"
    action = "观望"
    
    if long_chg and long_chg > 3 and short_chg and short_chg < -2:
        signal = "安全避险轮动"
        conclusion = "独立（避险流入）"
        level = "高"
        action = "关注轮动机会"
    elif long_chg and long_chg > 4:
        signal = "美股先行/资金流入"
        conclusion = "独立（US Leading）"
        level = "高"
        action = "关注A/HK跟进"
    
    return {
        "板块名称": sector,
        "3x Long": long_ticker,
        "3x Long 涨跌": f"{long_chg}%" if long_chg else "N/A",
        "3x Short": short_ticker,
        "3x Short 涨跌": f"{short_chg}%" if short_chg else "N/A",
        "核心锚点/触发": anchor_note,
        "资金流向信号": signal,
        "结论": conclusion,
        "预警级别": level,
        "建议动作": action
    }

# 基于你表格的完整监控列表
sectors_data = [
    ("半导体(芯片)", "SOXL", "SOXS", "NVDA $190 / 海力士 $1412"),
    ("纳斯达克100", "TQQQ", "SQQQ", "25500 缺口 / 特朗普关税"),
    ("生物技术", "LABU", "LABD", "XBI指数 / 并购新闻（美股先行）"),
    ("中概股(中国互联网)", "CWEB", "YANG", "上证4000点 / 存储板块异动"),
    ("金融(银行/证券)", "FAS", "FAZ", "沃尔什利率政策 / 商业地产坏账（避险信号）"),
    ("能源(石油/天然气)", "ERX", "ERY", "俄罗斯制裁执行力度"),
    ("罗素2000(小票)", "TNA", "TZA", "罗素重组生效后的承接力"),
]

results = [analyze_with_3x(*s) for s in sectors_data]
df = pd.DataFrame(results)

def highlight(row):
    if row["预警级别"] == "高":
        if "避险" in str(row["资金流向信号"]):
            return ['background-color: #2A3D1F; color: #4ADE80'] * len(row)
        return ['background-color: #3D1F1F; color: #FF6B6B'] * len(row)
    elif "独立" in str(row["结论"]):
        return ['background-color: #1F3D2A; color: #4ADE80'] * len(row)
    return ['background-color: #1E222A'] * len(row)

st.dataframe(df.style.apply(highlight, axis=1), use_container_width=True, height=520)

with st.sidebar:
    st.header("控制面板")
    if st.button("立即刷新全部数据", type="primary"):
        st.cache_data.clear()
        st.rerun()
    st.caption("已集成你提供的3倍杠杆工具 + 资金流向检测")

st.caption("系统已支持：安全避险轮动（FAS案例）、美股先行（LABU案例）等信号 | 可继续添加更多板块")
