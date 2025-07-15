# -*- coding: utf-8 -*-
"""
Розрахунок технічних індикаторів для торгового бота (ВИПРАВЛЕНА ВЕРСІЯ)
"""

import numpy as np
import pandas as pd
import talib
import logging
from typing import Dict, Tuple, Optional
from config.settings import INDICATORS_CONFIG

logger = logging.getLogger(__name__)

class TechnicalIndicators:
    """Клас для розрахунку технічних індикаторів"""
    
    def __init__(self):
        self.config = INDICATORS_CONFIG
        
    def _safe_convert_to_int_array(self, values: np.ndarray) -> np.ndarray:
        """Безпечна конвертація в цілочисельний масив 0/1"""
        try:
            # Конвертуємо в булевий масив, потім в int
            bool_array = np.array(values, dtype=bool)
            int_array = bool_array.astype(int)
            return int_array
        except Exception as e:
            logger.warning(f"Помилка конвертації в int array: {e}")
            return np.zeros_like(values, dtype=int)
        
    def calculate_rsi(self, close_prices: np.ndarray) -> Dict[str, np.ndarray]:
        """Розрахунок RSI та його похідних"""
        try:
            rsi = talib.RSI(close_prices, timeperiod=self.config['rsi_length'])
            
            # RSI Rising/Falling - виправлено
            rsi_rising_1 = np.zeros(len(rsi), dtype=int)
            rsi_rising_2 = np.zeros(len(rsi), dtype=int)
            rsi_falling_1 = np.zeros(len(rsi), dtype=int)
            rsi_falling_2 = np.zeros(len(rsi), dtype=int)
            
            for i in range(1, len(rsi)):
                if not np.isnan(rsi[i]) and not np.isnan(rsi[i-1]):
                    rsi_rising_1[i] = 1 if rsi[i] > rsi[i-1] else 0
                    rsi_falling_1[i] = 1 if rsi[i] < rsi[i-1] else 0
            
            for i in range(2, len(rsi)):
                if not np.isnan(rsi[i]) and not np.isnan(rsi[i-2]):
                    rsi_rising_2[i] = 1 if rsi[i] > rsi[i-2] else 0
                    rsi_falling_2[i] = 1 if rsi[i] < rsi[i-2] else 0
            
            return {
                'rsi': rsi,
                'rsi_rising_1': rsi_rising_1,
                'rsi_rising_2': rsi_rising_2,
                'rsi_falling_1': rsi_falling_1,
                'rsi_falling_2': rsi_falling_2
            }
        except Exception as e:
            logger.error(f"Помилка розрахунку RSI: {e}")
            return {}
    
    def calculate_ema(self, close_prices: np.ndarray) -> Dict[str, np.ndarray]:
        """Розрахунок EMA та сигналів"""
        try:
            ema_fast = talib.EMA(close_prices, timeperiod=self.config['fast_ma'])
            ema_slow = talib.EMA(close_prices, timeperiod=self.config['slow_ma'])
            ema_trend = talib.EMA(close_prices, timeperiod=self.config['slow_ma'])
            
            # EMA Crossover сигнали - виправлено
            ema_bullish = np.zeros(len(ema_fast), dtype=int)
            ema_bearish = np.zeros(len(ema_fast), dtype=int)
            
            for i in range(1, len(ema_fast)):
                if (not np.isnan(ema_fast[i]) and not np.isnan(ema_slow[i]) and 
                    not np.isnan(ema_fast[i-1]) and not np.isnan(ema_slow[i-1])):
                    
                    # Crossover up (bullish)
                    if ema_fast[i] > ema_slow[i] and ema_fast[i-1] <= ema_slow[i-1]:
                        ema_bullish[i] = 1
                    
                    # Crossunder down (bearish)
                    if ema_fast[i] < ema_slow[i] and ema_fast[i-1] >= ema_slow[i-1]:
                        ema_bearish[i] = 1
            
            return {
                'ema_fast': ema_fast,
                'ema_slow': ema_slow,
                'ema_trend': ema_trend,
                'ema_bullish': ema_bullish,
                'ema_bearish': ema_bearish
            }
        except Exception as e:
            logger.error(f"Помилка розрахунку EMA: {e}")
            return {}
    
    def calculate_macd(self, close_prices: np.ndarray) -> Dict[str, np.ndarray]:
        """Розрахунок MACD та сигналів"""
        try:
            macd_line, macd_signal, macd_histogram = talib.MACD(
                close_prices,
                fastperiod=self.config['macd_fast'],
                slowperiod=self.config['macd_slow'],
                signalperiod=self.config['macd_signal']
            )
            
            # MACD сигнали - виправлено
            macd_bullish = np.zeros(len(macd_line), dtype=int)
            macd_bearish = np.zeros(len(macd_line), dtype=int)
            
            for i in range(1, len(macd_line)):
                if (not np.isnan(macd_line[i]) and not np.isnan(macd_signal[i]) and 
                    not np.isnan(macd_line[i-1]) and not np.isnan(macd_signal[i-1])):
                    
                    # Crossover signals
                    if macd_line[i] > macd_signal[i] and macd_line[i-1] <= macd_signal[i-1]:
                        macd_bullish[i] = 1
                    elif macd_line[i] < macd_signal[i] and macd_line[i-1] >= macd_signal[i-1]:
                        macd_bearish[i] = 1
                    
                    # Additional bullish condition
                    elif (macd_line[i] > macd_signal[i] and 
                          not np.isnan(macd_histogram[i]) and not np.isnan(macd_histogram[i-1]) and
                          macd_histogram[i] > macd_histogram[i-1]):
                        macd_bullish[i] = 1
                    
                    # Additional bearish condition  
                    elif (macd_line[i] < macd_signal[i] and
                          not np.isnan(macd_histogram[i]) and not np.isnan(macd_histogram[i-1]) and
                          macd_histogram[i] < macd_histogram[i-1]):
                        macd_bearish[i] = 1
            
            return {
                'macd_line': macd_line,
                'macd_signal': macd_signal,
                'macd_histogram': macd_histogram,
                'macd_bullish': macd_bullish,
                'macd_bearish': macd_bearish
            }
        except Exception as e:
            logger.error(f"Помилка розрахунку MACD: {e}")
            return {}
    
    def calculate_adx(self, high_prices: np.ndarray, low_prices: np.ndarray, 
                     close_prices: np.ndarray) -> Dict[str, np.ndarray]:
        """Розрахунок ADX (Виправлена версія з обробкою ділення на нуль)"""
        try:
            length = self.config['adx_period']
            
            # Розрахунок True Range та Directional Movement
            up_move = np.diff(high_prices)
            down_move = -np.diff(low_prices)
            
            plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0.0)
            minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0.0)
            
            # True Range
            tr1 = high_prices[1:] - low_prices[1:]
            tr2 = np.abs(high_prices[1:] - close_prices[:-1])
            tr3 = np.abs(low_prices[1:] - close_prices[:-1])
            tr = np.maximum(np.maximum(tr1, tr2), tr3)
            
            # Додавання початкових значень для збереження довжини масивів
            plus_dm = np.concatenate([[0], plus_dm])
            minus_dm = np.concatenate([[0], minus_dm])
            tr = np.concatenate([[0], tr])
            
            # Розрахунок RMA (аналог ta.rma в PineScript)
            def rma(values, period):
                result = np.full_like(values, np.nan)
                alpha = 1.0 / period
                for i in range(len(values)):
                    if i == 0:
                        result[i] = values[i] if not np.isnan(values[i]) else 0
                    else:
                        if not np.isnan(values[i]):
                            result[i] = alpha * values[i] + (1 - alpha) * result[i-1]
                        else:
                            result[i] = result[i-1]
                return result
            
            # ATR та DI розрахунки з захистом від ділення на нуль
            atr = rma(tr, length)
            
            # Захист від ділення на нуль
            atr_safe = np.where(atr == 0, 1e-10, atr)  # Заміна нулів на дуже маленьке число
            
            plus_di = 100 * rma(plus_dm, length) / atr_safe
            minus_di = 100 * rma(minus_dm, length) / atr_safe
            
            # DX та ADX з захистом від ділення на нуль
            di_sum = plus_di + minus_di
            di_sum_safe = np.where(di_sum == 0, 1e-10, di_sum)  # Захист від ділення на нуль
            
            dx = 100 * np.abs(plus_di - minus_di) / di_sum_safe
            dx = np.where(np.isnan(dx) | np.isinf(dx), 0, dx)
            adx = rma(dx, length)
            
            # Заміна NaN та Inf значень на 0
            adx = np.where(np.isnan(adx) | np.isinf(adx), 0, adx)
            plus_di = np.where(np.isnan(plus_di) | np.isinf(plus_di), 0, plus_di)
            minus_di = np.where(np.isnan(minus_di) | np.isinf(minus_di), 0, minus_di)
            
            return {
                'adx': adx,
                'plus_di': plus_di,
                'minus_di': minus_di
            }
        except Exception as e:
            logger.error(f"Помилка розрахунку ADX: {e}")
            return {}
    
    def calculate_atr(self, high_prices: np.ndarray, low_prices: np.ndarray, 
                     close_prices: np.ndarray) -> np.ndarray:
        """Розрахунок ATR"""
        try:
            atr = talib.ATR(high_prices, low_prices, close_prices, 
                           timeperiod=self.config['atr_length'])
            # Заміна NaN значень
            atr = np.where(np.isnan(atr), 0, atr)
            return atr
        except Exception as e:
            logger.error(f"Помилка розрахунку ATR: {e}")
            return np.zeros(len(high_prices))
    
    def calculate_volume_indicators(self, volume: np.ndarray, close_prices: np.ndarray) -> Dict[str, np.ndarray]:
        """Розрахунок volume індикаторів"""
        try:
            # Volume SMA
            volume_sma = talib.SMA(volume, timeperiod=self.config['volume_lookback'])
            
            # Volume Filter - виправлено
            volume_filter_bool = volume > (volume_sma * self.config['min_volume_mult'])
            volume_filter = self._safe_convert_to_int_array(volume_filter_bool)
            
            # Volume Surge Detection - виправлено  
            volume_surge_bool = volume > (volume_sma * self.config['volume_surge_mult'])
            volume_surge = self._safe_convert_to_int_array(volume_surge_bool)
            
            super_volume_surge_bool = volume > (volume_sma * self.config['super_volume_mult'])
            super_volume_surge = self._safe_convert_to_int_array(super_volume_surge_bool)
            
            # Volume Trend
            volume_ema_10 = talib.EMA(volume, timeperiod=10)
            volume_ema_20 = talib.EMA(volume, timeperiod=20)
            
            # Захист від ділення на нуль
            volume_ema_20_safe = np.where(volume_ema_20 == 0, 1e-10, volume_ema_20)
            volume_trend = volume_ema_10 / volume_ema_20_safe
            volume_trend = np.where(np.isnan(volume_trend) | np.isinf(volume_trend), 1.0, volume_trend)
            
            # Sustained Volume - виправлено
            sustained_volume = np.zeros(len(volume), dtype=int)
            consecutive_count = 0
            
            for i in range(len(volume)):
                if not np.isnan(volume_sma[i]) and volume[i] > volume_sma[i] * 2.0:
                    consecutive_count += 1
                else:
                    consecutive_count = 0
                
                sustained_volume[i] = 1 if consecutive_count >= self.config['consecutive_vol_bars'] else 0
            
            # Volume Divergence - виправлено
            bullish_vol_divergence = np.zeros(len(volume), dtype=int)
            bearish_vol_divergence = np.zeros(len(volume), dtype=int)
            
            period = self.config['vol_divergence_period']
            volume_avg = talib.SMA(volume, timeperiod=period)
            
            for i in range(period, len(close_prices)):
                if i >= period:
                    price_change = close_prices[i] - close_prices[i-period]
                    volume_change = volume[i] - volume[i-period]
                    
                    # Bullish divergence: price down, volume up
                    if (price_change < 0 and volume_change > 0 and 
                        not np.isnan(volume_avg[i]) and volume[i] > volume_avg[i] * 1.5):
                        bullish_vol_divergence[i] = 1
                    
                    # Bearish divergence: price up, volume down  
                    if (price_change > 0 and volume_change < 0 and
                        not np.isnan(volume_avg[i]) and volume[i] < volume_avg[i] * 0.7):
                        bearish_vol_divergence[i] = 1
            
            return {
                'volume_sma': volume_sma,
                'volume_filter': volume_filter,
                'volume_surge': volume_surge,
                'super_volume_surge': super_volume_surge,
                'volume_trend': volume_trend,
                'sustained_volume': sustained_volume,
                'bullish_vol_divergence': bullish_vol_divergence,
                'bearish_vol_divergence': bearish_vol_divergence
            }
        except Exception as e:
            logger.error(f"Помилка розрахунку volume індикаторів: {e}")
            return {}
    
    def calculate_trend_indicators(self, close_prices: np.ndarray, ema_trend: np.ndarray) -> Dict[str, np.ndarray]:
        """Розрахунок трендових індикаторів"""
        try:
            bullish_trend_bool = close_prices > ema_trend
            bearish_trend_bool = close_prices < ema_trend
            
            bullish_trend = self._safe_convert_to_int_array(bullish_trend_bool)
            bearish_trend = self._safe_convert_to_int_array(bearish_trend_bool)
            
            return {
                'bullish_trend': bullish_trend,
                'bearish_trend': bearish_trend
            }
        except Exception as e:
            logger.error(f"Помилка розрахунку трендових індикаторів: {e}")
            return {}
    
    def calculate_all_indicators(self, df: pd.DataFrame) -> Dict[str, np.ndarray]:
        """Розрахунок всіх індикаторів"""
        try:
            if df.empty or len(df) < 50:
                logger.warning("Недостатньо даних для розрахунку індикаторів")
                return {}
            
            # Конвертація в numpy arrays
            close_prices = df['close_price'].values.astype(float)
            high_prices = df['high_price'].values.astype(float)
            low_prices = df['low_price'].values.astype(float)
            volume = df['volume'].values.astype(float)
            
            # Обробка NaN значень
            close_prices = np.where(np.isnan(close_prices) | (close_prices <= 0), 
                                  np.nanmean(close_prices[close_prices > 0]), close_prices)
            high_prices = np.where(np.isnan(high_prices) | (high_prices <= 0), 
                                 close_prices, high_prices)
            low_prices = np.where(np.isnan(low_prices) | (low_prices <= 0), 
                                close_prices, low_prices)
            volume = np.where(np.isnan(volume) | (volume < 0), 0, volume)
            
            all_indicators = {}
            
            # RSI
            rsi_indicators = self.calculate_rsi(close_prices)
            all_indicators.update(rsi_indicators)
            
            # EMA
            ema_indicators = self.calculate_ema(close_prices)
            all_indicators.update(ema_indicators)
            
            # MACD
            macd_indicators = self.calculate_macd(close_prices)
            all_indicators.update(macd_indicators)
            
            # ADX
            adx_indicators = self.calculate_adx(high_prices, low_prices, close_prices)
            all_indicators.update(adx_indicators)
            
            # ATR
            atr = self.calculate_atr(high_prices, low_prices, close_prices)
            all_indicators['atr'] = atr
            
            # Volume
            volume_indicators = self.calculate_volume_indicators(volume, close_prices)
            all_indicators.update(volume_indicators)
            
            # Trend
            if 'ema_trend' in all_indicators:
                trend_indicators = self.calculate_trend_indicators(close_prices, all_indicators['ema_trend'])
                all_indicators.update(trend_indicators)
            
            logger.debug("Всі індикатори розраховано успішно")
            return all_indicators
            
        except Exception as e:
            logger.error(f"Помилка розрахунку індикаторів: {e}")
            return {}
    
    def interpolate_nan_values(self, data: np.ndarray) -> np.ndarray:
        """Інтерполяція NaN значень"""
        try:
            if len(data) == 0:
                return data
                
            # Використання pandas для інтерполяції
            series = pd.Series(data)
            interpolated = series.interpolate(method='linear', limit_direction='both')
            
            # Заповнення залишкових NaN значень
            interpolated = interpolated.ffill().bfill()
            
            return interpolated.values
        except Exception as e:
            logger.error(f"Помилка інтерполяції: {e}")
            return data