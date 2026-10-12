import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import MetaTrader5 as mt5
import pandas_ta as ta

# --- CONFIGURACIÓN DE LA INTERFAZ ---
st.set_page_config(page_title="Trading Guardian", layout="wide")
st.title("🛡️ TRADIN_GUARDIAN - Panel de Riesgo Pepperstone")

# Parámetros en la barra lateral
st.sidebar.title("🔑 Configuración")
ema_rapida_val = st.sidebar.number_input("EMA Rápida", value=20)
ema_lenta_val = st.sidebar.number_input("EMA Lenta", value=50)
riesgo_operacion = st.sidebar.number_input("Riesgo por operación (%)", value=0.50) / 100

# Parámetros de cuenta Pepperstone
cuenta_input = st.sidebar.text_input("Número de Cuenta", value="1234567")
pass_input = st.sidebar.text_input("Contraseña", type="password")
servidor_input = st.sidebar.selectbox("Servidor", ["Pepperstone-Demo", "Pepperstone-Live"])

activo = st.sidebar.selectbox("Elegir Activo", ["EURUSD", "GBPUSD", "BTCUSD", "AAPL"])

# --- LÓGICA DE CONEXIÓN Y ANÁLISIS ---
if st.sidebar.button("Enlazar con MT5 🔄"):
    # 1. Inicializar la plataforma
    if not mt5.initialize():
        st.error(f"Error al inicializar MT5. Código: {mt5.last_error()}")
    else:
        # 2. Hacer login en Pepperstone
        conectado = mt5.login(login=int(cuenta_input), password=pass_input, server=servidor_input)
        
        if not conectado:
            st.error(f"Error de login en Pepperstone: {mt5.last_error()}")
            mt5.shutdown()
        else:
            st.success("✅ Conectado exitosamente a Pepperstone")
            
            # 3. Obtener Información de la Cuenta
            info_cuenta = mt5.account_info()
            if info_cuenta is not None:
                datos_cuenta = info_cuenta._asdict()
                col1, col2, col3 = st.columns(3)
                col1.metric("Balance Total", f"${datos_cuenta['balance']:.2f} {datos_cuenta['currency']}")
                col2.metric("Equidad en Vivo", f"${datos_cuenta['equity']:.2f}")
                col3.metric("Margen Libre", f"${datos_cuenta['margin_free']:.2f}")
                
                # Dinero exacto que estás arriesgando según tu 0.50%
                dinero_riesgo = datos_cuenta['balance'] * riesgo_operacion
                st.sidebar.metric("Dinero Máximo en Riesgo", f"${dinero_riesgo:.2f} USD")

            # 4. Traer los datos técnicos (Últimas 200 velas M15)
            velas = mt5.copy_rates_from_pos(activo, mt5.TIMEFRAME_M15, 0, 200)
            
            if velas is not None and len(velas) > 0:
                df = pd.DataFrame(velas)
                df['time'] = pd.to_datetime(df['time'], unit='s')
                
                # Precios máximos y mínimos de la sesión
                precio_alto_actual = df['high'].max()
                precio_bajo_actual = df['low'].min()
                precio_cierre_actual = df['close'].iloc[-1]
                
                # 5. Cálculos Matemáticos de Indicadores
                df['EMA_20'] = ta.ema(df['close'], length=ema_rapida_val)
                df['EMA_50'] = ta.ema(df['close'], length=ema_lenta_val)
                df.ta.rsi(length=14, append=True)
                df.ta.macd(fast=12, slow=26, signal=9, append=True)
                
                # Renombrar columnas de MACD autogeneradas por pandas_ta si es necesario
                # Usualmente crea: MACD_12_26_9 (línea) y MACDs_12_26_9 (señal)
                
                ultima_vela = df.iloc[-2]  # Vela completamente cerrada
                
                # Mostrar estados actuales
                st.write(f"### Monitoreo en Vivo:  {activo}")
                st.info(f"*Precio Actual:* {precio_cierre_actual} | *Máximo:* {precio_alto_actual} | *Mínimo:* {precio_bajo_actual}")
                
# Elegimos el activo financiero dentro del bróker
activo = "EURUSD" 

# Traer las últimas 200 velas (M15 = Gráficos de 15 minutos)
velas = mt5.copy_rates_from_pos(activo, mt5.TIMEFRAME_M15, 0, 200)

if candles is not None:
    df = pd.DataFrame(velas)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    
    # Extraer los precios más altos y más bajos de la sesión actual
    precio_alto_actual = df['high'].max()
    precio_bajo_actual = df['low'].min()
    precio_cierre_actual = df['close'].iloc[-1]
    
    # Cálculos matemáticos de tu estrategia integrada
    df['EMA20'] = ta.ema(df['close'], length=20)
    df['EMA50'] = ta.ema(df['close'], length=50)
    df.ta.rsi(length=14, append=True)
    df.ta.macd(fast=12, slow=26, signal=9, append=True)
    
    # Variables de la última vela cerrada para tu Guardian de Riesgo
    ultima_fila = df.iloc[-2]
    
    # Mostrar resultados interactivos en la web
    st.write(f"### Monitoreo Técnico: {activo}")
    st.info(f"*Precio Actual:* {precio_cierre_actual} | *Máximo de sesión:* {precio_alto_actual} | *Mínimo de sesión:* {precio_bajo_actual}")
    # Convertir a diccionario para extraer variables fácilmente
    datos = info_cuenta._asdict()
    
    # Crear columnas métricas en tu panel de Streamlit
    col1, col2, col3 = st.columns(3)
    col1.metric("Balance Total", f"${datos['balance']:.2f} {datos['currency']}")
    col2.metric("Equidad en Vivo", f"${datos['equity']:.2f}")
    col3.metric("Nivel de Margen (%)", f"{datos['margin_level']:.2f}%")

# Configuración en tu barra lateral
st.sidebar.header("Conexión Pepperstone")
num_cuenta = st.sidebar.number_input("Número de Cuenta", value=12345678)
password = st.sidebar.text_input("Contraseña", type="password")
servidor = st.sidebar.selectbox("Servidor", ["Pepperstone-Demo", "Pepperstone-Live"])

# Inicializar y conectar al bróker
if st.sidebar.button("Conectar Servidor"):
    if not mt5.initialize():
        st.error("No se pudo iniciar MetaTrader 5 en tu computadora.")
    else:
        # Hacer el login con tus datos de Pepperstone
        conectado = mt5.login(login=num_cuenta, password=password, server=servidor)
        
        if conectado:
            st.success(f"Conectado exitosamente a Pepperstone ({servidor})")
        else:
            st.error(f"Fallo en las credenciales. Código de error: {mt5.last_error()}")

# En tu barra lateral de Configuración
st.sidebar.title("Configuración de Conexión")
simbolo = st.sidebar.selectbox("Instrumento", ["EURUSD", "BTCUSD", "AAPL"])

# 1. Inicializar la conexión con el Bróker
if not mt5.initialize():
    st.error(f"No se pudo conectar a MT5. Error: {mt5.last_error()}")
else:
    # 2. Traer las últimas 500 velas del activo seleccionado
    # mt5.TIMEFRAME_M15 representa temporalidad de 15 minutos, cámbialo según tus inputs
    rates = mt5.copy_rates_from_pos(simbolo, mt5.TIMEFRAME_M15, 0, 500)
    
    # Convertir a DataFrame de Pandas para procesar
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    
    # 3. Calcular RSI y MACD usando la librería técnica
    df.ta.rsi(length=14, append=True)  # Crea la columna RSI_14
    df.ta.macd(fast=12, slow=26, signal=9, append=True)  # Crea MACD_12_26_9
    
    # 4. Lógica para revisar "Método Técnico de Alzas y Bajas"
    ultimo_registro = df.iloc[-1]
    rsi_actual = ultimo_registro['RSI_14']
    macd_linea = ultimo_registro['MACD_12_26_9']
    macd_senal = ultimo_registro['MACDs_12_26_9']
    
    # Ejemplo visual en tu panel de Streamlit
    st.metric(label=f"RSI Actual de {simbolo}", value=round(rsi_actual, 2))
    
    if rsi_actual < 30 and macd_linea > macd_senal:
        st.success("🚨 SEÑAL DE ALZA TÉCNICA (Sobreventa + Cruce MACD)")
    elif rsi_actual > 70 and macd_linea < macd_senal:
        st.warning("🚨 SEÑAL DE BAJA TÉCNICA (Sobrecompra + Cruce MACD)")
    else:
        st.info("El mercado se encuentra en rango neutral.")

    # Recuerda cerrar la conexión al finalizar los procesos pesados
    mt5.shutdown()

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
