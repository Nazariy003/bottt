# -*- coding: utf-8 -*-
"""
Налаштування торгового бота
"""

import os
from dotenv import load_dotenv

# Завантаження змінних середовища
load_dotenv('config/.env')

# ===== API НАЛАШТУВАННЯ =====
API_CONFIG = {
    'live': {
        'api_key': os.getenv('BYBIT_LIVE_API_KEY'),
        'api_secret': os.getenv('BYBIT_LIVE_SECRET_KEY'),
    },
    'demo': {
        'api_key': os.getenv('BYBIT_DEMO_API_KEY'),
        'api_secret': os.getenv('BYBIT_DEMO_SECRET_KEY'),
    },
    'testnet': False,  # ЗАВЖДИ False!
    'unified_account': True,
    'rate_limit': 3,  # запитів на секунду
    'retry_attempts': 3,
    'retry_delay': 1.0,
    
    # ✅ ВИПРАВЛЕНО: Реальні комісії Bybit
    'commission_rate_maker': 0.001,  # 0.055% для maker ордерів
    'commission_rate_taker': 0.001,  # 0.075% для taker ордерів
    'commission_rate_default': 0.001,  # За замовчуванням maker (більш консервативно)
}

# ===== ТОРГОВІ НАЛАШТУВАННЯ =====
TRADING_CONFIG = {
    'mode': os.getenv('TRADING_MODE', 'DEMO'),  # LIVE або DEMO
    'trade_pairs': ['STRKUSDT', 'ADAUSDT', 'ETHUSDT',  'SOLUSDT', 'BTCUSDT', 'ZKUSDT',

    # Додаткові популярні та середньо-популярні пари
    'XRPUSDT', 'DOGEUSDT', 'AVAXUSDT', 'DOTUSDT', 'TRXUSDT', 'LTCUSDT',
    'LINKUSDT', 'UNIUSDT', 'ETCUSDT', 'XLMUSDT', 'NEARUSDT', 'ALGOUSDT',
    'VETUSDT', 'ICPUSDT', 'FILUSDT', 'SANDUSDT', 'MANAUSDT', 'AXSUSDT', 'AAVEUSDT',
    'XTZUSDT', 'THETAUSDT', 'GRTUSDT', 'MKRUSDT', 'RUNEUSDT', 'EGLDUSDT', 'KSMUSDT',

    # Деякі менш популярні або новіші пари для різноманітності
    'CHZUSDT', 'ENJUSDT', 'SUSHIUSDT', 'SNXUSDT', 'CRVUSDT', 'DYDXUSDT',
    'GALAUSDT', 'APEUSDT', 'GMTUSDT', 'OPUSDT', 'APTUSDT', 'ARBUSDT', 'SUIUSDT', 'BLURUSDT',
    'SEIUSDT', 'TIAUSDT'],
    'timeframe': '5',  # хвилини
    'load_candles_amount': 500,  # Increased from 300 to 500 for better indicator calculation
    'min_candles_for_strategy': 150,  # Minimum candles required for strategy analysis
    'min_order_amount': 10,  # відсоток від балансу на одну угоду
    'max_orders_qty': 5,     # максимальна кількість одночасних позицій
    'leverage': 10,          # кредитне плече
    'min_order_value_usdt': 5.0,  # мінімальна вартість ордера в USDT (без врахування левереджа)
    'delay_after_market_order_ms': 2000,  # затримка після розміщення ордера
    'delay_between_symbols_ms': 500,      # затримка між символами
    'balance_report_interval_minutes': 30, # інтервал звітів про баланс
    'trade_cycle_buffer_seconds': 15,      # буфер торгового циклу
    'main_loop_error_sleep_seconds': 60,   # пауза при помилці в основному циклі
    'min_sl_market_distance_tick_multiplier': 5,  # мінімальна відстань SL від ринку в тіках
    'position_sync_enabled': True,  # Включити після виправлення
    'position_check_interval_seconds': 30,  # Швидка перевірка кожні 30 сек
    'sync_check_interval_minutes': 2,       # Повна синхронізація кожні 2 хв (замість 10)
    'balance_report_interval_minutes': 15,  # Звіт балансу кожні 15 хв (замість 30)
    'sync_check_interval_minutes': 2,  # Перевірка кожні 10 хвилин
    'sync_lookback_hours': 72,  # Аналізувати останні 72 години
    'sync_tolerance_qty': 0.0000001,  # Толерантність для кількості
    'sync_tolerance_price': 0.000001,  # Толерантність для цін
    'sync_debug_mode': True,  # Детальне логування синхронізації
}

# ===== НАЛАШТУВАННЯ ІНДИКАТОРІВ =====
INDICATORS_CONFIG = {
    # RSI
    'rsi_length': 14,
    'rsi_overbought': 70,
    'rsi_oversold': 30,
    
    # EMA
    'fast_ma': 8,
    'slow_ma': 21,
    'trend_ema': 21,
    
    # MACD
    'macd_fast': 12,
    'macd_slow': 26,
    'macd_signal': 9,
    
    # ADX
    'adx_period': 14,
    'adx_threshold': 20,
    
    # ATR
    'atr_length': 14,
    
    # Volume
    'volume_lookback': 5,
    'min_volume_mult': 1.1,
    'volume_surge_mult': 4.0,
    'super_volume_mult': 8.0,
    'consecutive_vol_bars': 2,
    'vol_divergence_period': 5,
}

# ===== СТРАТЕГІЯ =====
STRATEGY_CONFIG = {
    # Часові фільтри
    'use_time_filter': False,
    'avoid_early_hours': True,
    'avoid_late_hours': True,
    'avoid_lunch_time': True,
    'early_session_start': 0,
    'early_session_end': 2,
    'late_session_start': 21,
    'late_session_end': 23,
    'lunch_time_start': 12,
    'lunch_time_end': 14,
    
    # Адаптивний ризик
    'use_adaptive_risk': True,
    'risk_reduction_percent': 25.0,
    
    # Ринкові режими
    'use_market_regime': True,
    'regime_period': 20,
    'trend_strength': 1.5,
    'volatility_threshold': 0.02,
    'momentum_period': 10,
    
    # Адаптивні параметри
    'use_adaptive_params': True,
    'trending_min_conf_long': 2,
    'trending_min_conf_short': 2,
    'trending_adx_thresh': 25,
    'trending_tp_mult': 2.8,
    'trending_sl_mult': 1.0,
    
    'ranging_min_conf_long': 3,
    'ranging_min_conf_short': 3,
    'ranging_adx_thresh': 15,
    'ranging_tp_mult': 1.5,
    'ranging_sl_mult': 0.8,
    
    'mixed_min_conf_long': 2,
    'mixed_min_conf_short': 2,
    'mixed_adx_thresh': 20,
    'mixed_tp_mult': 2.2,
    'mixed_sl_mult': 1.0,
    
    # Lightning Volume System
    'use_lightning_volume': True,
    'vol_surge_tp_boost': 15.0,
    'super_volume_tp_boost': 35.0,
    'use_volume_extension': True,
    'volume_extension_mult': 1.3,
    
     # ✅ НОВА СИСТЕМА TP (без Final TP)
    'use_triple_partial_tp': True,
    'first_partial_percent': 30.0,    # Змінено з 15.0 на 30.0
    'first_partial_multiplier': 0.8,
    'second_partial_percent': 50.0,   # Змінено з 25.0 на 50.0  
    'second_partial_multiplier': 1.3,
    'third_partial_percent': 20.0,    # Змінено з 30.0 на 20.0
    'third_partial_multiplier': 1.8,
    
    # ✅ ВИМКНУТО Final TP
    'use_final_tp': False,  # Новий параметр
    
    'use_breakeven': True,
    'breakeven_buffer': 0.05,
    'breakeven_min_buffer_ticks': 3,  # мінімальний буфер в тіках для беззбитка
    
    # Trailing Stop
    'use_trailing_stop': True,
    'trail_atr_mult': 0.7,

    # Volume Divergence
    'use_volume_divergence': True,
    'volume_divergence_close_percent': 50.0, # Відсоток закриття

    # Stop Loss налаштування
    'sl_atr_multiplier': 1.5,  # множник ATR для розрахунку SL
     # ✅ НОВІ НАЛАШТУВАННЯ для кращого розрахунку TP
    'final_tp_safety_buffer': 0.2,  # Додатковий буфер для final TP (в частках ATR)
    'min_tp_distance': 0.1,         # Мінімальна відстань між TP рівнями (в частках ATR)
    'strict_tp_order_validation': True,  # Строга перевірка порядку TP

}

# ===== БАЗА ДАНИХ =====
DATABASE_CONFIG = {
    'db_path': os.getenv('DB_PATH', 'data/candles.db'),
    'connection_timeout': 30.0,
    'isolation_level': None,
}

# ===== TELEGRAM =====
TELEGRAM_CONFIG = {
    'bot_token': os.getenv('TELEGRAM_BOT_TOKEN'),
    'chat_id': os.getenv('TELEGRAM_CHAT_ID'),
    'enable_notifications': True,
    'notification_types': {
        'trades': True,
        'errors': True,
        'status': True,
        'balance': True,
    },
}

# ===== ЛОГУВАННЯ =====
LOGGING_CONFIG = {
    'level': os.getenv('LOG_LEVEL', 'DEBUG'),
    'trade_log_level': 'INFO',  # окремий рівень для торгових логів
    'enable_console': os.getenv('ENABLE_CONSOLE_LOGGING', 'True').lower() == 'true',
    'log_dir': 'logs',
    'max_file_size': 10 * 1024 * 1024,  # 10MB
    'backup_count': 5,
}

# ===== ВАЛІДАЦІЯ КОНФІГУРАЦІЇ =====
def validate_config():
    """Валідація конфігурації при запуску"""
    errors = []
    
    # Перевірка API конфігурації
    mode = TRADING_CONFIG['mode'].upper()
    if mode not in ['LIVE', 'DEMO']:
        errors.append(f"Невірний trading mode: {mode}. Має бути LIVE або DEMO")
    
    api_creds = API_CONFIG['demo'] if mode == 'DEMO' else API_CONFIG['live']
    if not api_creds['api_key'] or not api_creds['api_secret']:
        errors.append(f"API ключі не налаштовані для режиму {mode}")
    
    # Перевірка торгових пар
    if not TRADING_CONFIG['trade_pairs'] or len(TRADING_CONFIG['trade_pairs']) == 0:
        errors.append("Не вказано торгові пари")
    
    # Перевірка числових параметрів
    if TRADING_CONFIG['leverage'] <= 0 or TRADING_CONFIG['leverage'] > 100:
        errors.append(f"Невірний леверидж: {TRADING_CONFIG['leverage']}")
    
    if TRADING_CONFIG['min_order_amount'] <= 0 or TRADING_CONFIG['min_order_amount'] > 100:
        errors.append(f"Невірний розмір ордера: {TRADING_CONFIG['min_order_amount']}%")
    
    # Перевірка Telegram конфігурації
    if TELEGRAM_CONFIG['enable_notifications']:
        if not TELEGRAM_CONFIG['bot_token'] or not TELEGRAM_CONFIG['chat_id']:
            errors.append("Telegram налаштування не повні при включених сповіщеннях")
    
    return errors

# Валідуємо конфігурацію при імпорті
_config_errors = validate_config()
if _config_errors:
    import logging
    logger = logging.getLogger(__name__)
    for error in _config_errors:
        logger.error(f"Помилка конфігурації: {error}")
    raise ValueError(f"Знайдено {len(_config_errors)} помилок конфігурації")