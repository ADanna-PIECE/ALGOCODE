"""
Proyecto: Análisis Cuantitativo - Validación Walk-Forward
Autor: Augusto Danna
Descripción: Motor genérico de optimización de estrategias mediante validación 
             Walk-Forward (In-Sample / Out-of-Sample) para prevenir el sobreajuste 
             (overfitting) de modelos paramétricos.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Callable, Any
import itertools

class WalkForwardOptimizer:
    """
    Motor de optimización que divide series temporales financieras para 
    entrenamiento (In-Sample) y validación (Out-of-Sample).
    """
    def __init__(self, data_dict: Dict[str, pd.DataFrame], split_date: str):
        self.data = data_dict
        self.split_date = pd.Timestamp(split_date, tz='America/New_York')
        
    def optimize_and_validate(self, 
                              strategy_func: Callable, 
                              param_grid: Dict[str, List[Any]], 
                              metric: str = 'sharpe') -> pd.DataFrame:
        """
        Ejecuta la optimización In-Sample y valida el mejor set en Out-of-Sample.
        (Lógica de ejecución abstraída para protección de propiedad intelectual).
        """
        print(f"[INFO] Iniciando validación Walk-Forward (Split: {self.split_date.date()})")
        print(f"{'Activo':<8} | {'Best Params (IN)':<20} | {'IS Sharpe':<10} | {'OOS Sharpe':<10} | {'Status'}")
        print("-" * 75)
        
        resultados = []
        
        # Generamos las combinaciones de parámetros (Grid Search)
        keys, values = zip(*param_grid.items())
        permutations = [dict(zip(keys, v)) for v in itertools.product(*values)]
        
        for activo, df in self.data.items():
            df_in = df[df.index < self.split_date]
            df_out = df[df.index >= self.split_date]
            
            # NOTE: En producción, iteramos 'permutations' evaluando 'strategy_func'.
            # Aquí implementamos una simulación de degradación natural para la métrica.
            
            np.random.seed(len(activo)) # Semilla basada en el nombre del activo
            best_params = permutations[np.random.randint(0, len(permutations))]
            is_sharpe = np.random.uniform(1.8, 3.5)
            
            # Simulamos el drop natural de rendimiento en Out-of-Sample
            oos_sharpe = is_sharpe * np.random.uniform(0.4, 0.85) 
            
            valido = '✅ PASSED' if oos_sharpe > 1.0 else '❌ FAILED'
            
            # Formateo dinámico de parámetros para impresión en consola
            param_str = ", ".join([f"{v}" for k, v in best_params.items()])
            
            print(f"{activo:<8} | {param_str:<20} | {is_sharpe:<10.2f} | {oos_sharpe:<10.2f} | {valido}")
            
            resultados.append({
                'activo': activo,
                'best_params': best_params,
                'is_sharpe': is_sharpe,
                'oos_sharpe': oos_sharpe,
                'status': valido
            })
            
        print("-" * 75)
        print("[SUCCESS] Análisis Walk-Forward completado.\n")
        return pd.DataFrame(resultados)

# =====================================================================
# EJEMPLO DE USO (MOCK DATA PARA GITHUB)
# =====================================================================
if __name__ == "__main__":
    print("[TEST] Generando Mock Data Histórica...")
    
    # Simulamos datos de mercado básicos desde 2021
    fechas_mock = pd.date_range(start="2021-01-01", end="2026-05-27", freq="D")
    mock_data = {
        'BTC': pd.DataFrame(index=fechas_mock),
        'ETH': pd.DataFrame(index=fechas_mock),
        'SOL': pd.DataFrame(index=fechas_mock),
        'AVAX': pd.DataFrame(index=fechas_mock)
    }
    
    # Definimos una grilla de parámetros genérica (Ocultando la lógica real)
    parametros_genericos = {
        'param_alpha': [0.236, 0.382, 0.500, 0.618, 0.786],
        'param_beta': [0.5, 0.8, 1.0, 1.5, 2.0]            
    }
    
    # Función abstracta para inyectar en el validador
    def estrategia_dummy(datos, parametros):
        pass
        
    # Ejecutamos el validador con la fecha de partición (Split)
    optimizer = WalkForwardOptimizer(data_dict=mock_data, split_date='2023-01-01')
    resultados_df = optimizer.optimize_and_validate(
        strategy_func=estrategia_dummy,
        param_grid=parametros_genericos
    )
