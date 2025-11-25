"""
Detector de Niveles Psicológicos
Identifica niveles en incrementos de 0.5
"""

import numpy as np
import pandas as pd
from typing import List, Tuple, Dict
import config


class LevelDetector:
    """Detecta y gestiona niveles de precio psicológicos"""

    def __init__(self, increment: float = config.LEVEL_INCREMENT):
        self.increment = increment
        self.levels = self._generate_levels()

    def _generate_levels(self) -> List[float]:
        """
        Genera lista de niveles desde LEVEL_RANGE_MIN hasta LEVEL_RANGE_MAX
        en incrementos de self.increment
        """
        levels = []
        current = config.LEVEL_RANGE_MIN

        while current <= config.LEVEL_RANGE_MAX:
            levels.append(round(current, 1))
            current += self.increment

        return levels

    def get_nearest_level(self, price: float) -> float:
        """
        Encuentra el nivel más cercano a un precio dado

        Args:
            price: Precio actual

        Returns:
            Nivel más cercano
        """
        # Redondear al incremento más cercano
        nearest = round(price / self.increment) * self.increment
        return round(nearest, 1)

    def get_levels_in_range(self, price: float, range_points: float = 5.0) -> List[float]:
        """
        Obtiene niveles dentro de un rango del precio actual

        Args:
            price: Precio actual
            range_points: Rango en puntos arriba y abajo del precio

        Returns:
            Lista de niveles dentro del rango
        """
        min_price = price - range_points
        max_price = price + range_points

        return [level for level in self.levels
                if min_price <= level <= max_price]

    def distance_to_level(self, price: float, level: float) -> float:
        """
        Calcula distancia absoluta del precio a un nivel

        Args:
            price: Precio actual
            level: Nivel de referencia

        Returns:
            Distancia absoluta
        """
        return abs(price - level)

    def is_near_level(self, price: float, tolerance: float = config.LEVEL_TOLERANCE) -> Tuple[bool, float]:
        """
        Determina si el precio está cerca de algún nivel

        Args:
            price: Precio actual
            tolerance: Tolerancia en puntos

        Returns:
            (está_cerca, nivel_cercano)
        """
        nearest_level = self.get_nearest_level(price)
        distance = self.distance_to_level(price, nearest_level)

        is_near = distance <= tolerance

        return is_near, nearest_level if is_near else None

    def get_next_levels(self, price: float, direction: str, count: int = 3) -> List[float]:
        """
        Obtiene los próximos niveles en una dirección

        Args:
            price: Precio actual
            direction: "up" o "down"
            count: Número de niveles a devolver

        Returns:
            Lista de niveles
        """
        current_level = self.get_nearest_level(price)
        next_levels = []

        if direction.lower() == "up":
            for i in range(1, count + 1):
                next_level = current_level + (self.increment * i)
                if next_level <= config.LEVEL_RANGE_MAX:
                    next_levels.append(round(next_level, 1))
        else:  # down
            for i in range(1, count + 1):
                next_level = current_level - (self.increment * i)
                if next_level >= config.LEVEL_RANGE_MIN:
                    next_levels.append(round(next_level, 1))

        return next_levels

    def analyze_price_action_at_level(self, df: pd.DataFrame, level: float) -> Dict:
        """
        Analiza cómo reacciona el precio en un nivel específico

        Args:
            df: DataFrame con datos OHLCV
            level: Nivel a analizar

        Returns:
            Diccionario con estadísticas de reacción
        """
        tolerance = config.LEVEL_TOLERANCE

        # Filtrar barras que tocaron el nivel
        touched_level = df[
            ((df['low'] <= level + tolerance) & (df['high'] >= level - tolerance))
        ].copy()

        if len(touched_level) == 0:
            return {
                'touches': 0,
                'bounces': 0,
                'breaks': 0,
                'bounce_rate': 0.0
            }

        bounces = 0
        breaks = 0

        for idx in touched_level.index:
            # Verificar si hay datos suficientes después
            if idx + 3 >= len(df):
                continue

            # Obtener barras siguientes
            next_bars = df.loc[idx+1:idx+3]

            # Determinar si rebotó o rompió
            if len(next_bars) > 0:
                # Si el precio se alejó del nivel en dirección opuesta = rebote
                price_before = df.loc[idx, 'close']
                price_after = next_bars['close'].iloc[-1]

                if price_before < level and price_after < level - tolerance:
                    bounces += 1
                elif price_before > level and price_after > level + tolerance:
                    bounces += 1
                elif abs(price_after - level) > tolerance * 2:
                    breaks += 1

        total_touches = len(touched_level)
        bounce_rate = bounces / total_touches if total_touches > 0 else 0.0

        return {
            'touches': total_touches,
            'bounces': bounces,
            'breaks': breaks,
            'bounce_rate': bounce_rate
        }

    def get_support_resistance_levels(self, df: pd.DataFrame, lookback: int = 100) -> Dict[str, List[float]]:
        """
        Identifica niveles que actuaron como soporte o resistencia

        Args:
            df: DataFrame con datos OHLCV
            lookback: Número de barras a analizar

        Returns:
            {'support': [levels], 'resistance': [levels]}
        """
        recent_data = df.tail(lookback)

        support_levels = []
        resistance_levels = []

        for level in self.levels:
            analysis = self.analyze_price_action_at_level(recent_data, level)

            # Si tuvo varios toques y buena tasa de rebote, es un nivel fuerte
            if analysis['touches'] >= 2 and analysis['bounce_rate'] >= 0.5:
                # Determinar si es soporte o resistencia basado en precio actual
                current_price = df['close'].iloc[-1]

                if level < current_price:
                    support_levels.append(level)
                else:
                    resistance_levels.append(level)

        return {
            'support': sorted(support_levels, reverse=True),  # Más cercano primero
            'resistance': sorted(resistance_levels)  # Más cercano primero
        }


if __name__ == "__main__":
    # Test básico
    detector = LevelDetector()

    print("=== LEVEL DETECTOR TEST ===\n")
    print(f"Niveles generados: {detector.levels}\n")

    test_price = 2575.75
    print(f"Precio de prueba: {test_price}")
    print(f"Nivel más cercano: {detector.get_nearest_level(test_price)}")
    print(f"Niveles en rango (±5): {detector.get_levels_in_range(test_price, 5)}")

    is_near, level = detector.is_near_level(test_price)
    print(f"¿Está cerca de nivel? {is_near}, Nivel: {level}")

    print(f"\nPróximos 3 niveles arriba: {detector.get_next_levels(test_price, 'up', 3)}")
    print(f"Próximos 3 niveles abajo: {detector.get_next_levels(test_price, 'down', 3)}")
