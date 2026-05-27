"""
Proyecto: Motor de Backtesting Institucional - Baseline Momentum
Autor: Augusto Danna
Descripción: Motor de ejecución estructurada para validación de estrategias de 
             Momentum (HMA + RSI Bollinger). Incluye gestión dinámica de riesgo 
             (Stop Loss adaptativo) y auditoría financiera de costos de fricción.
"""

import pandas as pd
import numpy as np
from typing import Dict, List
import warnings
warnings.filterwarnings('ignore')

class MomentumBacktestEngine:
    """
    Motor de simulación de trading que evalúa entradas por momentum,
    calculando el impacto real de las comisiones (spread/slippage) en el PnL.
    """
    def __init__(self, data_dict: Dict[str, pd.DataFrame], 
                 session_start: str = "09:30", session_end: str = "11:30", 
                 friccion_r: float = 0.12):
        self.data = data_dict
        self.session_start = session_start
        self.session_end = session_end
        self.friccion_r = friccion_r
        self.resultados = []

    def _calcular_indicadores(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calcula HMA (100) para sesgo direccional y RSI (14) con 
        Bandas de Bollinger (24, 1) para gatillos de momentum.
        """
        import pandas_ta as ta
        
        df = df.copy()
        df['HMA_100'] = ta.hma(df['close'], length=100)
        df['RSI'] = ta.rsi(df['close'], length=14)
        
        bb_rsi = ta.bbands(df['RSI'], length=24, std=1)
        if bb_rsi is not None:
            col_bbu = [col for col in bb_rsi.columns if col.startswith('BBU')][0]
            col_bbl = [col for col in bb_rsi.columns if col.startswith('BBL')][0]
            df['BBU_RSI'] = bb_rsi[col_bbu]
            df['BBL_RSI'] = bb_rsi[col_bbl]
            
        df.dropna(subset=['HMA_100', 'BBU_RSI'], inplace=True)
        return df

    def ejecutar_simulacion(self, target_rr: float = 2.0) -> pd.DataFrame:
        """Itera sobre la serie temporal simulando la ejecución en vivo."""
        print(f"[INFO] Ejecutando simulación institucional (RR Objetivo: 1:{target_rr})")
        
        for activo, df_crudo in self.data.items():
            df = self._calcular_indicadores(df_crudo)
            in_trade, trade_dir, sl, tp = False, None, 0, 0
            
            for i in range(1, len(df)):
                row = df.iloc[i]
                prev_row = df.iloc[i-1]
                current_time = row.name.strftime('%H:%M')

                # Gestión de la posición abierta
                if in_trade:
                    if trade_dir == 'BUY':
                        if row['high'] >= tp:
                            self.resultados.append({'fecha': row.name, 'activo': activo, 'pnl': target_rr - self.friccion_r, 'res': 1})
                            in_trade = False
                        elif row['low'] <= sl:
                            self.resultados.append({'fecha': row.name, 'activo': activo, 'pnl': -1 - self.friccion_r, 'res': 0})
                            in_trade = False
                    else: # SELL
                        if row['low'] <= tp:
                            self.resultados.append({'fecha': row.name, 'activo': activo, 'pnl': target_rr - self.friccion_r, 'res': 1})
                            in_trade = False
                        elif row['high'] >= sl:
                            self.resultados.append({'fecha': row.name, 'activo': activo, 'pnl': -1 - self.friccion_r, 'res': 0})
                            in_trade = False
                    continue

                # Filtro de Sesión Operativa
                if not (self.session_start <= current_time <= self.session_end): 
                    continue

                # Lógica de Entrada (Momentum Breakout)
                if row['close'] > row['HMA_100'] and prev_row['RSI'] <= prev_row['BBU_RSI'] and row['RSI'] > row['BBU_RSI']:
                    trade_dir, in_trade = 'BUY', True
                    sl = df['low'].iloc[max(0, i-7):i].min()
                    riesgo = row['close'] - sl
                    if riesgo > 0: tp = row['close'] + (riesgo * target_rr)
                    else: in_trade = False

                elif row['close'] < row['HMA_100'] and prev_row['RSI'] >= prev_row['BBL_RSI'] and row['RSI'] < row['BBL_RSI']:
                    trade_dir, in_trade = 'SELL', True
                    sl = df['high'].iloc[max(0, i-7):i].max()
                    riesgo = sl - row['close']
                    if riesgo > 0: tp = row['close'] - (riesgo * target_rr)
                    else: in_trade = False

        return pd.DataFrame(self.resultados)

    def auditar_rendimiento(self, df_trades: pd.DataFrame) -> None:
        """Genera el reporte de auditoría deduciendo costos de broker."""
        if df_trades.empty:
            print("[WARN] No se generaron operaciones en la simulación.")
            return
            
        print("\n" + "═"*70)
        print("📅 AUDITORÍA INSTITUCIONAL: DESGLOSE Y COSTOS DE FRICCIÓN")
        print("═"*70)
        
        df_trades['año'] = df_trades['fecha'].dt.year
        reporte_anual = []

        for año in sorted(df_trades['año'].unique()):
            df_año = df_trades[df_trades['año'] == año].copy()
            trades = len(df_año)
            win_rate = df_año['res'].mean() * 100

            pnl_neto = df_año['pnl'].sum()
            costos_broker = trades * self.friccion_r
            pnl_bruto = pnl_neto + costos_broker 

            ganancias = df_año[df_año['pnl'] > 0]['pnl'].sum()
            perdidas = abs(df_año[df_año['pnl'] < 0]['pnl'].sum())
            pf = ganancias / perdidas if perdidas > 0 else 0

            df_año['Cum_PnL'] = df_año['pnl'].cumsum()
            df_año['DD'] = df_año['Cum_PnL'] - df_año['Cum_PnL'].cummax()
            max_dd_anual = df_año['DD'].min()

            reporte_anual.append({
                'Año': año, 'Trades': trades, 'Win Rate %': f"{win_rate:.2f}%",
                'PF': f"{pf:.2f}", 'PnL Bruto (R)': f"{pnl_bruto:.2f}R",
                'Pago Broker (R)': f"-{costos_broker:.2f}R",
                'PnL Neto (R)': f"{pnl_neto:.2f}R", 'Max DD (R)': f"{max_dd_anual:.2f}R"
            })

        df_reporte = pd.DataFrame(reporte_anual)
        print(df_reporte.to_string(index=False))
        print("═"*70)
        
        total_bruto = sum([float(x['PnL Bruto (R)'][:-1]) for x in reporte_anual])
        total_broker = sum([float(x['Pago Broker (R)'][1:-1]) for x in reporte_anual])
        total_neto = sum([float(x['PnL Neto (R)'][:-1]) for x in reporte_anual])

        pct_broker = (total_broker / total_bruto * 100) if total_bruto > 0 else 0

        print(f"💰 PnL BRUTO GENERADO:   {total_bruto:.2f}R")
        print(f"🏦 COSTOS DE BROKER:    -{total_broker:.2f}R ({pct_broker:.1f}% del bruto)")
        print(f"✅ PnL NETO FINAL:       {total_neto:.2f}R")

# =====================================================================
# EJEMPLO DE USO (MOCK DATA PARA GITHUB)
# =====================================================================
if __name__ == "__main__":
    print("[TEST] Inicializando entorno de pruebas...")
    
    # Simulamos una serie de precios OHLCV básica para que el motor pueda procesar
    fechas = pd.date_range(start="2024-01-01 09:00", end="2025-12-31 12:00", freq="5min")
    n = len(fechas)
    np.random.seed(42)
    
    # Generamos movimiento de precios con tendencia alcista leve
    close = np.cumsum(np.random.normal(0, 0.05, n)) + 100
    high = close + np.random.uniform(0, 0.1, n)
    low = close - np.random.uniform(0, 0.1, n)
    
    mock_df = pd.DataFrame({'close': close, 'high': high, 'low': low}, index=fechas)
    
    # Instanciamos y ejecutamos el motor
    engine = MomentumBacktestEngine(data_dict={'MOCK_ASSET': mock_df}, session_start="09:00", session_end="12:00")
    
    # Simulamos la ejecución intentando cazar ratios 1:2
    trades = engine.ejecutar_simulacion(target_rr=2.0)
    engine.auditar_rendimiento(trades)
