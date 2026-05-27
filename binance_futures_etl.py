"""
Proyecto: Ingesta y Procesamiento de Datos OHLCV (Binance Futures)
Autor: Augusto Danna
Descripción: Sistema automatizado para la descarga, normalización y 
             estructuración de datos de alta frecuencia (5m) de futuros USDT-M.
"""

# =====================================================================
# CELDA 1 — CONFIGURACIÓN DEL ENTORNO
# =====================================================================
"""
Script de inicialización para Google Colab.
Se encarga de montar el almacenamiento persistente de Drive y verificar/instalar 
las dependencias de terceros necesarias para el análisis.
"""
from google.colab import drive
drive.mount('/content/drive')

import subprocess, sys

# NOTE: Si la librería no está instalada, subprocess la instala silenciosamente (-q)
for pkg in ['pandas_ta', 'seaborn']:
    try:
        __import__(pkg)
    except ImportError:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', pkg, '-q'])

print('✅ Drive montado y dependencias OK')

# =====================================================================
# CELDA 2 — IMPORTS
# =====================================================================
"""
Importación de dependencias núcleo y utilerías.
Carga los módulos estándar de Python para peticiones HTTP y manejo de archivos,
junto con librerías especializadas en manipulación de series temporales (Pandas),
cálculo vectorial (NumPy) y análisis técnico (Pandas TA).
"""
import os, zipfile, requests, warnings
import pandas as pd
import numpy as np
import pandas_ta as ta
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
from datetime import datetime, timedelta
warnings.filterwarnings('ignore')

def pearsonr(x, y):
    r = np.corrcoef(np.array(x), np.array(y))[0, 1]
    return r, None

print('✅ Imports OK')

# =====================================================================
# CELDA 3 — CONFIG GLOBAL MULTI-SESIÓN
# =====================================================================
"""
Configuración de parámetros globales y constantes del sistema.
Define la arquitectura de rutas, zona horaria objetivo (EST/EDT), 
ventana temporal de análisis y los diccionarios de metadatos de los activos.
"""
CARPETA      = '/content/drive/MyDrive/crypto_futuros_data'
TZ           = 'America/New_York'

# Clave: Empezamos en Enero para tener historial base
FECHA_INICIO = '2026-01-01'
CAPITAL_INI  = 1_000.0

ACTIVOS = {
    'BTC':  {'simbolo': 'BTCUSDT',  'color': '#F7931A'},
    'ETH':  {'simbolo': 'ETHUSDT',  'color': '#627EEA'},
    'SOL':  {'simbolo': 'SOLUSDT',  'color': '#9945FF'},
    'AVAX': {'simbolo': 'AVAXUSDT', 'color': '#E84142'},
}

# NOTE: Parámetros de sesión temporal ajustados mediante heurística propia y análisis histórico del activo.
CONFIG_MULTI = {
    'BTC': {
        'asialondres': {'inicio': '21:00', 'fin': '08:00'}
    },
    'ETH': {
        'ny':          {'inicio': '09:00', 'fin': '14:00'},
        'asia':        {'inicio': '21:00', 'fin': '00:00'},
        'asialondres': {'inicio': '21:00', 'fin': '08:00'}
    },
    'SOL': {
        'ny':          {'inicio': '09:00', 'fin': '14:00'},
        'asia':        {'inicio': '21:00', 'fin': '00:00'},
        'asialondres': {'inicio': '21:00', 'fin': '08:00'}
    },
    'AVAX': {
        'asialondres': {'inicio': '21:00', 'fin': '08:00'}
    }
}

print('✅ Configuración de Sesiones cargada.')

# =====================================================================
# CELDA 4 — DESCARGA HÍBRIDA (FUTUROS USDT-M)
# =====================================================================
"""
Servicio de Ingesta de Datos (Data Ingestion) para Futuros USDT-M.
Descarga y almacena datos OHLCV de alta frecuencia (5m) desde Binance Vision.
Implementa una lógica híbrida para optimizar el almacenamiento.
"""
import os, zipfile, requests
from datetime import datetime

os.makedirs(CARPETA, exist_ok=True)
anio_actual = datetime.now().year
mes_actual  = datetime.now().month
dia_actual  = datetime.now().day

def descargar_simbolo(simbolo: str, anio_inicio: int) -> None:
    # Base de datos de FUTUROS (um = USDT-Margined)
    base_mensual = 'https://data.binance.vision/data/futures/um/monthly/klines'
    base_diaria  = 'https://data.binance.vision/data/futures/um/daily/klines'

    for anio in range(anio_inicio, anio_actual + 1):
        for mes in range(1, 13):
            if anio == anio_actual and mes > mes_actual: break

            ms = str(mes).zfill(2)

            # --- LÓGICA MES ACTUAL: DESCARGA DIARIA ---
            if anio == anio_actual and mes == mes_actual:
                print(f"  📥 Buscando días sueltos de {ms}/{anio}...")
                for dia in range(1, dia_actual):
                    d_str = str(dia).zfill(2)
                    nombre_diario = f'{simbolo}-5m-{anio}-{ms}-{d_str}'
                    ruta_csv = os.path.join(CARPETA, f'{nombre_diario}.csv')

                    if os.path.exists(ruta_csv): continue

                    url_diaria = f'{base_diaria}/{simbolo}/5m/{nombre_diario}.zip'
                    ruta_zip   = os.path.join(CARPETA, f'{nombre_diario}.zip')

                    try:
                        r = requests.get(url_diaria, timeout=15)
                        if r.status_code == 200:
                            with open(ruta_zip, 'wb') as f: f.write(r.content)
                            with zipfile.ZipFile(ruta_zip, 'r') as z: z.extractall(CARPETA)
                            os.remove(ruta_zip)
                            print(f'    ✅ {nombre_diario}.csv')
                    except Exception:
                        pass
                break

            # --- LÓGICA MESES CERRADOS: DESCARGA MENSUAL ---
            else:
                nombre_mensual = f'{simbolo}-5m-{anio}-{ms}'
                ruta_csv = os.path.join(CARPETA, f'{nombre_mensual}.csv')

                if os.path.exists(ruta_csv): continue

                url_mensual = f'{base_mensual}/{simbolo}/5m/{nombre_mensual}.zip'
                ruta_zip    = os.path.join(CARPETA, f'{nombre_mensual}.zip')

                try:
                    r = requests.get(url_mensual, timeout=30)
                    if r.status_code == 200:
                        with open(ruta_zip, 'wb') as f: f.write(r.content)
                        with zipfile.ZipFile(ruta_zip, 'r') as z: z.extractall(CARPETA)
                        os.remove(ruta_zip)
                        print(f'  ✅ {nombre_mensual}.csv')
                except Exception:
                    pass

print("Verificando descargas mensuales y bajando días recientes (FUTUROS)...")
for nombre, cfg in ACTIVOS.items():
    print(f'\n=== {nombre} ===')
    descargar_simbolo(cfg['simbolo'], 2026)

total = len([f for f in os.listdir(CARPETA) if f.endswith('.csv')])
print(f'\n✅ Total archivos en Drive: {total}')

# =====================================================================
# CELDA 5 — CARGA DE DATOS AL DATAFRAME
# =====================================================================
"""
Pipeline de Procesamiento y Estructuración de Datos (ETL).
Lee los archivos CSV descargados, concatena los registros y normaliza la 
serie temporal para su posterior análisis en memoria RAM.
"""
def cargar_datos(simbolo: str) -> pd.DataFrame:
    archivos = sorted([f for f in os.listdir(CARPETA) if f.startswith(f'{simbolo}-5m') and f.endswith('.csv')])
    if not archivos: return pd.DataFrame()

    dfs = []
    for arch in archivos:
        dfs.append(pd.read_csv(os.path.join(CARPETA, arch), header=None, dtype=str))

    df = pd.concat(dfs, ignore_index=True)
    df.columns = ['open_time','open','high','low','close','volume','close_time','quote_vol','trades','tb_base','tb_quote','ignore']

    df['open_time'] = pd.to_numeric(df['open_time'], errors='coerce')
    mask = df['open_time'] > 1e15
    df.loc[mask, 'open_time'] = df.loc[mask, 'open_time'] // 1000
    df['open_time'] = pd.to_datetime(df['open_time'], unit='ms', errors='coerce')
    df = df.dropna(subset=['open_time'])

    for col in ['open','high','low','close','volume']:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    df = df[['open_time','open','high','low','close','volume']].copy()
    df['open_time'] = df['open_time'].dt.tz_localize('UTC').dt.tz_convert(TZ)
    df = df.sort_values('open_time').drop_duplicates('open_time').reset_index(drop=True).dropna()
    df = df[df['open_time'] >= pd.Timestamp(FECHA_INICIO, tz=TZ)].reset_index(drop=True)
    df = df.set_index('open_time')
    return df

print('Cargando datos a la memoria RAM...')
DFS = {}
for nombre, cfg in ACTIVOS.items():
    DFS[nombre] = cargar_datos(cfg['simbolo'])
    if not DFS[nombre].empty:
        print(f'  {nombre}: {len(DFS[nombre]):,} velas | {DFS[nombre].index[0].date()} → {DFS[nombre].index[-1].date()}')
print('\n✅ Base de datos lista para operar.')
