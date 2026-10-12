import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf

st.set_page_config(page_title="TRADING GUARDIAN", page_icon="📈", layout="wide")
st.title("📈 TRADING GUARDIAN")
st.caption("Analizador educativo de Forex. No ejecuta operaciones ni garantiza ganancias.")

with st.sidebar:
    st.header("Configuración")
    pair = st.selectbox("Instrumento", ["EUR/USD", "GBP/USD", "USD/JPY"])
    ticker = {"EUR/USD":"EURUSD=X", "GBP/USD":"GBPUSD=X", "USD/JPY":"JPY=X"}[pair]
    period = st.selectbox("Historial", ["1mo","3mo","6mo","1y","2y"], index=2)
    interval = st.selectbox("Temporalidad", ["1d","1h","30m"], index=0)
    fast = st.number_input("EMA rápida", 3, 50, 20)
    slow = st.number_input("EMA lenta", 10, 200, 50)
    risk = st.slider("Riesgo hipotético por operación (%)", 0.1, 1.0, 0.5, 0.1)
    balance = st.number_input("Saldo de referencia (USD)", min_value=0.0, value=100.0, step=10.0)
    stop = st.number_input("Stop-loss hipotético (%)", min_value=0.1, max_value=5.0, value=1.0, step=0.1)

@st.cache_data(ttl=300)
def load_data(ticker, period, interval):
    d = yf.download(ticker, period=period, interval=interval, auto_adjust=False, progress=False)
    if d is None or d.empty: return pd.DataFrame()
    if isinstance(d.columns, pd.MultiIndex): d.columns = d.columns.get_level_values(0)
    d.columns = [str(c).title() for c in d.columns]
    if not all(c in d.columns for c in ["Open","High","Low","Close"]): return pd.DataFrame()
    return d.dropna(subset=["Open","High","Low","Close"])

def calc_rsi(s, n=14):
    delta=s.diff()
    gain=delta.clip(lower=0).ewm(alpha=1/n,min_periods=n,adjust=False).mean()
    loss=(-delta.clip(upper=0)).ewm(alpha=1/n,min_periods=n,adjust=False).mean()
    rs=gain/loss.replace(0,np.nan)
    return 100-(100/(1+rs))

df=load_data(ticker,period,interval)
if df.empty:
    st.error("No se pudieron cargar datos. Prueba otro historial o temporalidad.")
    st.info("Los datos pueden estar retrasados o diferir de los precios de tu bróker.")
    st.stop()

df["EMA_fast"]=df["Close"].ewm(span=int(fast),adjust=False).mean()
df["EMA_slow"]=df["Close"].ewm(span=int(slow),adjust=False).mean()
df["RSI"]=calc_rsi(df["Close"])
e12=df["Close"].ewm(span=12,adjust=False).mean()
e26=df["Close"].ewm(span=26,adjust=False).mean()
df["MACD"]=e12-e26
df["MACD_signal"]=df["MACD"].ewm(span=9,adjust=False).mean()
df["MACD_hist"]=df["MACD"]-df["MACD_signal"]
last=df.iloc[-1]
up=last["EMA_fast"]>last["EMA_slow"]
macd_up=last["MACD"]>last["MACD_signal"]
rsi=float(last["RSI"]) if pd.notna(last["RSI"]) else np.nan
if up and macd_up and pd.notna(rsi) and 50 <= rsi <= 70:
    signal="POSIBLE SESGO ALCISTA"
    note="EMA, MACD y RSI coinciden en un posible sesgo alcista; no es garantía."
elif not up and not macd_up and pd.notna(rsi) and 30 <= rsi <= 50:
    signal="POSIBLE SESGO BAJISTA"
    note="EMA, MACD y RSI coinciden en un posible sesgo bajista; no es garantía."
else:
    signal="SIN CONFIRMACIÓN"
    note="Los indicadores no coinciden. Esperar también es una decisión."

a,b,c,d=st.columns(4)
a.metric("Último cierre",f"{last['Close']:.5f}")
b.metric("RSI", "—" if pd.isna(rsi) else f"{rsi:.1f}")
c.metric("Tendencia EMA","Alcista" if up else "Bajista")
d.metric("Lectura técnica",signal)
st.info(note)
st.warning("La aplicación no envía órdenes. No existe una estrategia que elimine el riesgo de pérdida.")

fig=make_subplots(rows=3,cols=1,shared_xaxes=True,vertical_spacing=0.04,
                  row_heights=[0.62,0.19,0.19],subplot_titles=("Velas y EMA","RSI","MACD"))
fig.add_trace(go.Candlestick(x=df.index,open=df["Open"],high=df["High"],low=df["Low"],close=df["Close"],name="Precio"),row=1,col=1)
fig.add_trace(go.Scatter(x=df.index,y=df["EMA_fast"],name=f"EMA {fast}"),row=1,col=1)
fig.add_trace(go.Scatter(x=df.index,y=df["EMA_slow"],name=f"EMA {slow}"),row=1,col=1)
fig.add_trace(go.Scatter(x=df.index,y=df["RSI"],name="RSI"),row=2,col=1)
fig.add_hline(y=70,line_dash="dash",row=2,col=1); fig.add_hline(y=30,line_dash="dash",row=2,col=1)
fig.add_trace(go.Bar(x=df.index,y=df["MACD_hist"],name="MACD histograma"),row=3,col=1)
fig.add_trace(go.Scatter(x=df.index,y=df["MACD"],name="MACD"),row=3,col=1)
fig.add_trace(go.Scatter(x=df.index,y=df["MACD_signal"],name="Señal MACD"),row=3,col=1)
fig.update_layout(height=760,xaxis_rangeslider_visible=False,legend_orientation="h",margin=dict(l=10,r=10,t=55,b=10))
st.plotly_chart(fig,use_container_width=True)

st.subheader("Calculadora de riesgo")
risk_usd=balance*risk/100
exposure=risk_usd/(stop/100)
st.write(f"Riesgo teórico: **US${risk_usd:.2f}** ({risk:.1f}% del saldo de referencia).")
st.write(f"Exposición nocional ilustrativa para ese stop: **US${exposure:.2f}**. No equivale al margen ni a un lote recomendado.")
st.caption("El cálculo real depende del pip, el tamaño de lote, la moneda de la cuenta, spread, comisiones, apalancamiento y deslizamiento.")

with st.expander("Reglas prudentes"):
    st.markdown("- Practica primero en demo.\n- No aumentes el riesgo para recuperar pérdidas.\n- Define stop-loss y salida antes de entrar.\n- Considera spread, comisiones y deslizamiento.\n- Prueba la estrategia con datos históricos antes de confiar en ella.")
st.caption("Herramienta educativa; no es asesoría financiera, recomendación de compra/venta ni promesa de rentabilidad.")
