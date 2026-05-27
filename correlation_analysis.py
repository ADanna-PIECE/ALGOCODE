"""
Proyecto: Análisis Cuantitativo - Correlación de Activos
Autor: Augusto Danna
Descripción: Módulo estadístico para evaluar la diversificación del portafolio 
             mediante matrices de correlación de Pearson sobre retornos diarios.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict

class CorrelationAnalyzer:
    """
    Evalúa la correlación cruzada de los retornos de múltiples activos 
    para optimizar la exposición al riesgo del portafolio.
    """
    def __init__(self, trades_dict: Dict[str, pd.DataFrame], output_dir: str = './plots'):
        self.trades = trades_dict
        self.output_dir = output_dir
        self.activos = list(trades_dict.keys())
        
        import os
        os.makedirs(self.output_dir, exist_ok=True)

    def _preparar_retornos(self) -> pd.DataFrame:
        """Agrupa las operaciones por fecha y suma el retorno neto diario."""
        retornos_diarios = {}
        for activo, df_ops in self.trades.items():
            ops_dia = df_ops.copy()
            ops_dia['fecha_solo_dia'] = ops_dia['fecha'].dt.date
            ret_dia = ops_dia.groupby('fecha_solo_dia')['r_neto'].sum()
            retornos_diarios[activo] = ret_dia
            
        return pd.DataFrame(retornos_diarios).fillna(0)

    def plot_matriz_correlacion(self) -> None:
        """Genera y guarda el Heatmap de correlación de Pearson."""
        print("[INFO] Calculando matriz de correlación...")
        df_retornos = self._preparar_retornos()
        matriz_corr = df_retornos.corr(method='pearson')

        print("\nMatriz de Correlación de Retornos:")
        print(matriz_corr.round(3))
        
        fig, ax = plt.subplots(figsize=(8, 7))
        sns.heatmap(matriz_corr, ax=ax, annot=True, fmt='.3f',
                    cmap='RdYlGn_r', center=0, vmin=-1, vmax=1,
                    linewidths=0.5, square=True,
                    annot_kws={'size': 14, 'fontweight': 'bold'})
        
        ax.set_title('Correlación Cruzada de Retornos Diarios',
                     fontsize=13, fontweight='bold')
        
        plt.tight_layout()
        filepath = f'{self.output_dir}/matriz_correlacion.png'
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        print(f"[SUCCESS] Matriz guardada en: {filepath}")
        plt.close()

# =====================================================================
# EJEMPLO DE USO 
# =====================================================================
# =====================================================================
# EJEMPLO DE USO (MOCK DATA PARA PRUEBAS Y GITHUB)
# =====================================================================
if __name__ == "__main__":
    # Generamos datos simulados para probar que la clase funciona
    print("[TEST] Generando Mock Data...")
    
    # Creamos 100 días de fechas falsas
    fechas_mock = pd.date_range(start="2026-01-01", periods=100, freq="D")
    
    # Simulamos retornos (R Neto)
    np.random.seed(42) 
    r_btc = np.random.normal(0, 1, 100)
    r_eth = r_btc * 0.8 + np.random.normal(0, 0.5, 100) 
    r_sol = np.random.normal(0, 1.5, 100)
    
    # Armamos los DataFrames simulando la salida de una estrategia
    mock_trades = {
        'BTC': pd.DataFrame({'fecha': fechas_mock, 'r_neto': r_btc}),
        'ETH': pd.DataFrame({'fecha': fechas_mock, 'r_neto': r_eth}),
        'SOL': pd.DataFrame({'fecha': fechas_mock, 'r_neto': r_sol})
    }
    
    # Instanciamos la clase y corremos el método
    analyzer = CorrelationAnalyzer(mock_trades, output_dir='./test_plots')
    analyzer.plot_matriz_correlacion()
