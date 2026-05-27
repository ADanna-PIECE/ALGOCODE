"""
Proyecto: Análisis Cuantitativo - Rendimiento de Portafolio
Autor: Augusto Danna
Descripción: Módulo de visualización para evaluar la consistencia histórica 
             de los retornos a través de mapas de calor mensuales y anuales.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict

class PerformanceVisualizer:
    """
    Genera visualizaciones de rendimiento histórico agrupadas por 
    activo, año y mes para identificar estacionalidades y consistencia.
    """
    def __init__(self, trades_dict: Dict[str, pd.DataFrame], output_dir: str = './plots'):
        self.trades = trades_dict
        self.output_dir = output_dir
        self.activos = list(trades_dict.keys())
        
        import os
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Paleta de colores corporativa para los gráficos
        self.colores = {'BTC': '#F7931A', 'ETH': '#627EEA', 'SOL': '#9945FF', 'AVAX': '#E84142'}

    def plot_monthly_heatmaps(self) -> None:
        """Crea un grid de heatmaps con el retorno neto mensual por activo."""
        print("[INFO] Generando Heatmaps de rendimiento mensual...")
        
        fig, axes = plt.subplots(2, 2, figsize=(18, 10))
        fig.suptitle('Análisis de Rendimiento Mensual por Activo (R Neto)', 
                     fontsize=16, fontweight='bold')

        meses_labels = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 
                        'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']

        axes_flat = axes.flatten()

        for i, activo in enumerate(self.activos):
            if i >= 4: 
                break 
                
            ax = axes_flat[i]
            ops_act = self.trades[activo].copy()
            
            ops_act['mes'] = ops_act['fecha'].dt.month
            ops_act['anio'] = ops_act['fecha'].dt.year

            pivot_r = ops_act.pivot_table(
                index='anio', columns='mes',
                values='r_neto', aggfunc='sum'
            ).fillna(0)
            
            pivot_r.columns = [meses_labels[m-1] for m in pivot_r.columns]

            color_titulo = self.colores.get(activo, '#333333')

            sns.heatmap(pivot_r, ax=ax, cmap='RdYlGn', center=0,
                        annot=True, fmt='.1f', linewidths=0.5, linecolor='white',
                        annot_kws={'size': 11, 'fontweight': 'bold'}, cbar=False)
            
            ax.set_title(f'{activo} — Retorno Histórico', fontsize=14, fontweight='bold', color=color_titulo)
            ax.set_xlabel('Mes', fontsize=10)
            ax.set_ylabel('Año', fontsize=10)

        plt.tight_layout()
        fig.subplots_adjust(top=0.92) 
        
        filepath = f'{self.output_dir}/heatmap_rendimiento.png'
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        print(f"[SUCCESS] Heatmaps guardados en: {filepath}")
        plt.close()

# =====================================================================
# EJEMPLO DE USO (MOCK DATA PARA GITHUB)
# =====================================================================
if __name__ == "__main__":
    print("[TEST] Generando Mock Data Histórica...")
    
    fechas_mock = pd.date_range(start="2024-01-01", end="2026-05-27", freq="D")
    n_days = len(fechas_mock)
    
    np.random.seed(10)
    
    r_btc = np.random.normal(0.05, 1.2, n_days)
    r_eth = np.random.normal(0.08, 1.5, n_days)
    r_sol = np.random.normal(0.12, 2.5, n_days)
    r_avax = np.random.normal(0.10, 2.0, n_days)
    
    mock_trades = {
        'BTC': pd.DataFrame({'fecha': fechas_mock, 'r_neto': r_btc}),
        'ETH': pd.DataFrame({'fecha': fechas_mock, 'r_neto': r_eth}),
        'SOL': pd.DataFrame({'fecha': fechas_mock, 'r_neto': r_sol}),
        'AVAX': pd.DataFrame({'fecha': fechas_mock, 'r_neto': r_avax})
    }
    
    visualizer = PerformanceVisualizer(mock_trades, output_dir='./test_plots')
    visualizer.plot_monthly_heatmaps()
