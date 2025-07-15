# -*- coding: utf-8 -*-
"""
Telegram бот для сповіщень торгового бота
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from telegram import Bot
from telegram.error import TelegramError
from config.settings import TELEGRAM_CONFIG, API_CONFIG

logger = logging.getLogger(__name__)

class TelegramNotifier:
    """Клас для відправки сповіщень через Telegram"""
    
    def __init__(self):
        self.config = TELEGRAM_CONFIG
        self.bot = None
        self.chat_id = self.config.get('chat_id')
        
        if self.config.get('bot_token') and self.config.get('enable_notifications', True):
            try:
                self.bot = Bot(token=self.config['bot_token'])
                logger.info("Telegram бот ініціалізовано")
            except Exception as e:
                logger.error(f"Помилка ініціалізації Telegram бота: {e}")
                self.bot = None
        else:
            logger.warning("Telegram сповіщення вимкнено")
    
    def get_detailed_action_info(self, action: str, reason: str = "", side: str = "") -> Tuple[str, str]:
        """Визначає детальний тип дії та емодзі для торгових операцій"""

        action_lower = action.lower()
        reason_lower = reason.lower() if reason else ""
        side_upper = side.upper() if side else "UNKNOWN_SIDE"

        position_suffix = ""
        if side_upper == 'BUY':
            position_suffix = " (LONG)"
        elif side_upper == 'SELL':
            position_suffix = " (SHORT)"

        # Пріоритетний аналіз за reason (більш точний, якщо він детальний)
        if 'stop loss hit' in reason_lower or 'sl_hit' in action_lower: # Додано перевірку action_lower
            return f"STOP LOSS HIT{position_suffix}", "🛑"
        elif 'partial_1 hit' in reason_lower or 'partial_tp1_hit' in action_lower:
            return f"PARTIAL TP 1 HIT{position_suffix}", "💎"
        elif 'partial_2 hit' in reason_lower or 'partial_tp2_hit' in action_lower:
            return f"PARTIAL TP 2 HIT{position_suffix}", "💎"
        elif 'partial_3 hit' in reason_lower or 'partial_tp3_hit' in action_lower:
            return f"PARTIAL TP 3 HIT{position_suffix}", "💎"
        elif 'final tp hit' in reason_lower or ('take profit' in reason_lower and 'partial' not in reason_lower) or 'final_tp_hit' in action_lower:
            return f"FINAL TP HIT{position_suffix}", "🏆"
        elif 'volume divergence exit' in reason_lower or 'vol_div_exit' in action_lower:
            return f"VOLUME DIVERGENCE EXIT{position_suffix}", "📊"
        elif 'breakeven' in reason_lower or 'breakeven_close' in action_lower:
            return f"BREAKEVEN CLOSE{position_suffix}", "⚖️"
        elif 'trailing stop' in reason_lower or 'trailing_sl_hit' in action_lower:
            return f"TRAILING STOP HIT{position_suffix}", "⚡"
        elif 'pos_closed_on_tpsl_update_fail' in action_lower: # Новий тип
            return f"CLOSED (TP/SL Update Fail){position_suffix}", "⚠️"
        elif 'closed externally' in reason_lower or 'external_close' in action_lower or 'closed_externally' in action_lower:
            return f"EXTERNAL CLOSE{position_suffix}", "💨"
        elif 'already_closed' in action_lower: # Змінено з 'already closed' in reason_lower
            return f"ALREADY CLOSED{position_suffix}", "💨"

        # Аналіз за action, якщо reason не дав точного результату
        if 'open' in action_lower:
            return f"OPEN{position_suffix}", "🟢" if side_upper == "BUY" else "🔴"

        # Розбираємо action, якщо він має складний формат (наприклад, з _close_position)
        # PARTIAL_SL_HIT_BUY, PARTIAL_TP1_HIT_SELL etc.
        if "partial" in action_lower and "close" not in action_lower: # Наприклад, PARTIAL_TP1_HIT_BUY
            tp_type_part = "UNKNOWN_TP"
            if "tp1" in action_lower or "partial_1" in action_lower : tp_type_part = "PARTIAL TP 1"
            elif "tp2" in action_lower or "partial_2" in action_lower: tp_type_part = "PARTIAL TP 2"
            elif "tp3" in action_lower or "partial_3" in action_lower: tp_type_part = "PARTIAL TP 3"
            elif "final" in action_lower : tp_type_part = "FINAL TP"

            if "hit" in action_lower:
                return f"{tp_type_part} HIT{position_suffix}", "💎" if "final" not in tp_type_part.lower() else "🏆"

        # Загальні випадки закриття, якщо action містить 'close'
        if 'close' in action_lower or 'closed' in action_lower:
            if 'partial' in action_lower: # Наприклад, MANUAL_PARTIAL_CLOSE_BUY
                return f"PARTIAL CLOSE{position_suffix}", "📊"
            else: # Наприклад, MANUAL_CLOSE_BUY
                return f"CLOSE{position_suffix}", "🎯"

        # Якщо нічого не підійшло, повертаємо базову інформацію
        default_action_text = action.replace('_', ' ').upper()
        default_emoji = "ℹ️"
        if side_upper == "BUY": default_emoji = "📈"
        elif side_upper == "SELL": default_emoji = "📉"

        return f"{default_action_text}{position_suffix}", default_emoji
    
    async def send_message(self, message: str, parse_mode: str = 'HTML') -> bool:
        """Відправка повідомлення в Telegram"""
        if not self.bot or not self.chat_id:
            logger.debug("Telegram бот не налаштовано")
            return False
        
        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode=parse_mode
            )
            return True
            
        except TelegramError as e:
            logger.error(f"Помилка відправки Telegram повідомлення: {e}")
            return False
        except Exception as e:
            logger.error(f"Неочікувана помилка Telegram: {e}")
            return False
    
    async def send_bot_status(self, status: str, additional_info: Dict = None) -> bool:
        """Відправка статусу бота"""
        if not self.config.get('notification_types', {}).get('status', True):
            return False
        
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            message = f"🤖 <b>Статус бота</b>\n"
            message += f"⏰ Час: {timestamp}\n"
            message += f"📊 Статус: <b>{status}</b>\n"
            
            if additional_info:
                message += "\n📋 <b>Додаткова інформація:</b>\n"
                for key, value in additional_info.items():
                    message += f"• {key}: {value}\n"
            
            return await self.send_message(message)
            
        except Exception as e:
            logger.error(f"Помилка відправки статусу бота: {e}")
            return False
    
    async def send_balance_update(self, balance_data: Dict[str, Any]) -> bool:
        """Відправка оновлення балансу з правильним розрахунком P&L через різницю балансів"""
        if not self.config.get('notification_types', {}).get('balance', True):
            return False
        
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            message = f"💰 <b>Баланс акаунта</b>\n"
            message += f"⏰ Час: {timestamp}\n"
            
            # Поточний баланс USDT
            current_usdt_balance = balance_data.get('usdt_balance')
            if isinstance(current_usdt_balance, (int, float)):
                message += f"💵 USDT: <b>{float(current_usdt_balance):.2f}</b>\n"
            else:
                message += f"💵 USDT: <b>{current_usdt_balance or '0.00'}</b>\n"

            # ✅ ВИПРАВЛЕНО: P&L розраховується як різниця між поточним та початковим балансом
            initial_balance = balance_data.get('initial_balance')
            if isinstance(current_usdt_balance, (int, float)) and isinstance(initial_balance, (int, float)):
                pnl_from_balance_diff = float(current_usdt_balance) - float(initial_balance)
                pnl_emoji = "📈" if pnl_from_balance_diff >= 0 else "📉"
                message += f"{pnl_emoji} P&L: <b>{pnl_from_balance_diff:+.4f} USDT</b>\n"
            else:
                # Fallback на старий спосіб, якщо немає початкового балансу
                total_pnl_val = balance_data.get('total_pnl', 0)
                if isinstance(total_pnl_val, (int, float)):
                    pnl_val_num = float(total_pnl_val)
                    pnl_emoji = "📈" if pnl_val_num >= 0 else "📉"
                    message += f"{pnl_emoji} P&L: <b>{pnl_val_num:+.4f} USDT</b>\n"
                else:
                    message += f"📊 P&L: <b>{total_pnl_val or 'N/A'}</b>\n"
            
            # Кількість позицій
            open_positions_count = balance_data.get('open_positions_count', 0)
            message += f"📍 Відкритих позицій: <b>{open_positions_count}</b>\n"
            
            # ✅ ВИПРАВЛЕНО: Статистика торгівлі
            total_trades = balance_data.get('total_trades', 0)
            winning_trades = balance_data.get('winning_trades', 0)
            losing_trades = balance_data.get('losing_trades', 0)
            
            if total_trades > 0:
                win_rate = (winning_trades / total_trades) * 100
                message += f"\n📊 <b>Статистика торгівлі:</b>\n"
                message += f"🎯 Всього угод: <b>{total_trades}</b>\n"
                message += f"✅ Виграшних: <b>{winning_trades}</b>\n"
                message += f"❌ Програшних: <b>{losing_trades}</b>\n"
                message += f"📈 Вінрейт: <b>{win_rate:.1f}%</b>\n"
                
                # ✅ ВИПРАВЛЕНО: P&L від угод окремо (сума P&L з торгових записів)
                total_pnl_from_trades = balance_data.get('total_pnl', 0)
                if isinstance(total_pnl_from_trades, (int, float)):
                    avg_trade = total_pnl_from_trades / total_trades if total_trades > 0 else 0
                    message += f"💰 P&L від торгівлі: <b>{total_pnl_from_trades:+.4f} USDT</b>\n"
                    message += f"📊 Середня угода: <b>{avg_trade:+.4f} USDT</b>\n"
                    
                    # Показуємо різницю між P&L від балансу та угод (комісії, слипадж тощо)
                    if isinstance(current_usdt_balance, (int, float)) and isinstance(initial_balance, (int, float)):
                        balance_pnl = float(current_usdt_balance) - float(initial_balance)
                        difference = balance_pnl - total_pnl_from_trades
                        if abs(difference) > 0.0001:  # Показуємо тільки якщо різниця значна
                            message += f"⚖️ Різниця (комісії/слипадж): <b>{difference:+.4f} USDT</b>\n"
            
            return await self.send_message(message)
            
        except Exception as e:
            logger.error(f"Помилка відправки балансу: {e}", exc_info=True)
            return False
    
    async def send_trade_notification(self, trade_data: Dict[str, Any]) -> bool:
        """Відправка сповіщення про торгівлю з покращеними заголовками та точним P&L"""
        if not self.config.get('notification_types', {}).get('trades', True):
            return False

        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            action = trade_data.get('action', 'Unknown Trade Action')
            symbol = trade_data.get('symbol', 'N/A')
            side = trade_data.get('side', 'N/A')
            reason = trade_data.get('reason', '')

            detailed_action_text, action_emoji = self.get_detailed_action_info(action, reason, side)
            message = f"{action_emoji} <b>{detailed_action_text}</b>\n"

            message += f"⏰ Час: {timestamp}\n"
            message += f"📊 Пара: <b>{symbol}</b>\n"

            price_val = trade_data.get('price') # Ціна виконання або тригера
            if price_val is not None:
                try:
                    price_float = float(price_val)
                    price_str_fmt = str(price_float)
                    decimals = 0
                    if '.' in price_str_fmt:
                        decimals = len(price_str_fmt.split('.')[1])
                        if price_float > 100 and decimals > 2: decimals = 2
                        elif price_float > 1 and decimals > 4: decimals = 4
                        elif decimals > 6: decimals = 6
                    message += f"💰 Ціна: <b>{price_float:.{decimals}f}</b>\n"
                except (ValueError, TypeError):
                    message += f"💰 Ціна: <b>{price_val}</b>\n"
            
            # Додаємо ціну тригера, якщо вона є і відрізняється від ціни виконання
            trigger_price = trade_data.get('trigger_price_for_close')
            if trigger_price is not None and price_val is not None:
                try:
                    if abs(float(trigger_price) - float(price_val)) > 1e-9: # Якщо ціни суттєво відрізняються
                        trigger_price_float = float(trigger_price)
                        decimals_trigger = 0
                        if '.' in str(trigger_price_float):
                            decimals_trigger = len(str(trigger_price_float).split('.')[1])
                            if trigger_price_float > 100 and decimals_trigger > 2: decimals_trigger = 2
                            elif trigger_price_float > 1 and decimals_trigger > 4: decimals_trigger = 4
                            elif decimals_trigger > 6: decimals_trigger = 6
                        message += f"🔑 Тригер ціна: <b>{trigger_price_float:.{decimals_trigger}f}</b>\n"
                except (ValueError, TypeError):
                    pass


            quantity_display = trade_data.get('quantity_float', trade_data.get('quantity'))
            if quantity_display is not None:
                try:
                    qty_val = float(quantity_display)
                    qty_str_fmt = str(qty_val)
                    qty_decimals = 0
                    if '.' in qty_str_fmt:
                        qty_decimals = len(qty_str_fmt.split('.')[1])
                        if qty_val < 0.001 and qty_decimals > 8: qty_decimals = 8 # Для дуже малих кількостей
                        elif qty_val < 1 and qty_decimals > 6 : qty_decimals = 6
                        elif qty_val >=1 and qty_decimals > 4: qty_decimals = 4
                    message += f"📦 Кількість: <b>{qty_val:.{qty_decimals}f}</b>\n"
                except (ValueError, TypeError):
                    message += f"📦 Кількість: <b>{quantity_display}</b>\n"

            if 'OPEN' in detailed_action_text.upper():
                entry_price_val = trade_data.get('entry_price', trade_data.get('price'))
                if entry_price_val is not None and quantity_display is not None:
                    try:
                        total_value = float(entry_price_val) * float(quantity_display)
                        message += f"💵 Сума (орієнтовно): <b>{total_value:.2f} USDT</b>\n"
                    except (ValueError, TypeError): pass

                sl_val = trade_data.get('stop_loss')
                if sl_val is not None:
                    try:
                        sl_float = float(sl_val)
                        sl_decimals = 2 if sl_float > 100 else 4 if sl_float > 1 else 6
                        message += f"🛑 Stop Loss: <b>{sl_float:.{sl_decimals}f}</b>\n"
                    except (ValueError, TypeError):
                        message += f"🛑 Stop Loss: <b>{sl_val}</b>\n"

                tp_levels = trade_data.get('take_profits')
                if isinstance(tp_levels, list) and tp_levels:
                    message += f"🎯 Take Profits:\n"
                    for i, tp in enumerate(tp_levels):
                        if isinstance(tp, dict):
                            tp_price = tp.get('price')
                            tp_percentage = tp.get('percentage_to_close')
                            tp_type = tp.get('type', str(i+1))
                            if tp_price is not None and tp_percentage is not None:
                                try:
                                    tp_price_float = float(tp_price)
                                    tp_dec = 2 if tp_price_float > 100 else 4 if tp_price_float > 1 else 6
                                    message += f"  • TP {tp_type}: {tp_price_float:.{tp_dec}f} ({float(tp_percentage):.1f}%)\n"
                                except (ValueError, TypeError):
                                    message += f"  • TP {tp_type}: {tp_price} ({tp_percentage}%)\n"

                if trade_data.get('confidence') is not None:
                    message += f"📊 Впевненість: <b>{trade_data['confidence']}</b>\n"
                if trade_data.get('volume_surge_active'): message += f"⚡ Volume Surge активовано!\n"
                if trade_data.get('super_volume_surge_active'): message += f"🌟 SUPER Volume Surge активовано!\n"

            if any(keyword in detailed_action_text.upper() for keyword in ['CLOSE', 'HIT', 'EXIT', 'ALREADY', 'FAIL']): # Додано FAIL
                pnl_value_from_data = trade_data.get('pnl')
                pnl_display_text = "<b>N/A</b>"
                pnl_emoji_for_msg = "📊"

                if pnl_value_from_data is not None:
                    if isinstance(pnl_value_from_data, str) and "N/A" in pnl_value_from_data:
                        pass # Залишаємо N/A
                    else:
                        try:
                            pnl_float = float(pnl_value_from_data)
                            pnl_emoji_for_msg = "💚" if pnl_float >= 0 else "❤️"
                            pnl_display_text = f"<b>{pnl_float:+.4f} USDT</b>"

                            pnl_percentage = trade_data.get('pnl_percentage')
                            if pnl_percentage is not None:
                                try:
                                    pnl_display_text += f" ({float(pnl_percentage):+.2f}%)"
                                except (ValueError, TypeError): pass
                        except (ValueError, TypeError):
                            pnl_display_text = f"<b>{str(pnl_value_from_data)}</b>"

                message += f"{pnl_emoji_for_msg} P&L: {pnl_display_text}\n"

                remaining_qty = trade_data.get('remaining_quantity')
                if remaining_qty is not None and "PARTIAL" in detailed_action_text.upper():
                    try:
                        rem_qty_float = float(remaining_qty)
                        if rem_qty_float > 0.0000001 : # Показуємо залишок, тільки якщо він є
                            rem_qty_decimals = 0
                            if '.' in str(rem_qty_float): rem_qty_decimals = len(str(rem_qty_float).split('.')[1])
                            if rem_qty_float < 0.001 and rem_qty_decimals > 8: rem_qty_decimals = 8
                            elif rem_qty_float < 1 and rem_qty_decimals > 6 : rem_qty_decimals = 6
                            elif rem_qty_float >=1 and rem_qty_decimals > 4: rem_qty_decimals = 4
                            message += f"📦 Залишок: <b>{rem_qty_float:.{rem_qty_decimals}f}</b>\n"
                    except (ValueError, TypeError):
                        if remaining_qty: message += f"📦 Залишок: <b>{remaining_qty}</b>\n"


            if reason:
                reason_short = reason[:250] + "..." if len(reason) > 250 else reason # Збільшено ліміт
                message += f"📝 Причина: {reason_short}\n"
            
            # Додавання детальної причини закриття, якщо є
            detailed_reason = trade_data.get('detailed_close_reason')
            if detailed_reason and detailed_reason.lower() != reason.lower(): # Якщо відрізняється від основної причини
                message += f"🔩 Деталі причини: {detailed_reason}\n"


            exchange_order_id = trade_data.get('exchange_order_id')
            if exchange_order_id:
                message += f"🆔 ID ордера: <code>{exchange_order_id}</code>\n"


            details = trade_data.get('details') # Загальні деталі
            if details:
                details_short = str(details)[:200] + "..." if len(str(details)) > 200 else str(details)
                message += f"ℹ️ Додатково: {details_short}\n"


            return await self.send_message(message)

        except Exception as e:
            logger.error(f"Помилка відправки торгового сповіщення: {e}", exc_info=True)
            try:
                await self.send_message(f"🚨 Помилка формування торгового сповіщення: {str(e)[:200]}")
            except: pass
            return False
  
    async def send_signal_notification(self, signal_data: Dict[str, Any]) -> bool:
        """Відправка сповіщення про сигнал"""
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            signal = signal_data.get('signal', 'HOLD')
            symbol = signal_data.get('symbol', 'Unknown')
            confidence_val = signal_data.get('confidence') 
            confidence_str = str(confidence_val) if confidence_val is not None else "N/A"

            if signal == 'HOLD': 
                return False 
            
            # Покращене відображення сигналів
            if signal == 'BUY':
                signal_emoji = "🟢"
                signal_text = "BUY (LONG)"
            elif signal == 'SELL':
                signal_emoji = "🔴"
                signal_text = "SELL (SHORT)"
            else:
                signal_emoji = "⚪"
                signal_text = signal
            
            message = f"{signal_emoji} <b>Торговий сигнал: {signal_text}</b>\n"
            message += f"⏰ Час: {timestamp}\n"
            message += f"📊 Пара: <b>{symbol}</b>\n"
            message += f"💪 Впевненість: <b>{confidence_str}</b>\n" 
            
            entry_price_val = signal_data.get('entry_price')
            if entry_price_val is not None:
                 message += f"💰 Ціна входу: <b>{float(entry_price_val):.6f}</b>\n"
            
            stop_loss_val = signal_data.get('stop_loss_price') 
            if stop_loss_val is not None:
                message += f"🛑 Stop Loss: <b>{float(stop_loss_val):.6f}</b>\n"
            
            tp_levels = signal_data.get('take_profits')
            if isinstance(tp_levels, list) and tp_levels:
                message += f"🎯 Take Profits:\n"
                for i, tp in enumerate(tp_levels[:3], 1):
                    if isinstance(tp, dict):
                        tp_price = tp.get('price')
                        tp_percentage = tp.get('percentage_to_close') 
                        tp_type = tp.get('type', str(i))
                        if tp_price is not None and tp_percentage is not None:
                            message += f"  • TP {tp_type}: {float(tp_price):.6f} ({float(tp_percentage):.1f}%)\n"
            
            if signal_data.get('volume_surge_active'):
                message += f"⚡ <b>Volume Surge!</b>\n"
            if signal_data.get('super_volume_surge_active'):
                 message += f"🌟 <b>SUPER Volume Surge!</b>\n"
            
            market_regime_info = signal_data.get('market_regime_status', "N/A") 
            message += f"📈 Режим: <b>{market_regime_info}</b>\n"
            
            reason = signal_data.get('reason')
            if reason:
                message += f"📝 Причина: {reason}\n"
            
            return await self.send_message(message)
            
        except Exception as e:
            logger.error(f"Помилка відправки сповіщення про сигнал: {e}", exc_info=True)
            return False
    
    async def send_error_notification(self, error_data: Dict[str, Any]) -> bool:
        """Відправка сповіщення про помилку"""
        if not self.config.get('notification_types', {}).get('errors', True):
            return False
        
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            error_type = error_data.get('type', 'Unknown')
            error_message_val = error_data.get('message', 'Unknown error')
            # Обмеження довжини повідомлення про помилку
            error_message_str = str(error_message_val)
            if len(error_message_str) > 1000: # Обмеження, щоб не перевищити ліміти Telegram
                error_message_str = error_message_str[:1000] + "..."

            message = f"🚨 <b>Критична помилка</b>\n"
            message += f"⏰ Час: {timestamp}\n"
            message += f"❌ Тип: <b>{error_type}</b>\n"
            message += f"📝 Повідомлення: {error_message_str}\n" # Використовуємо обмежений рядок
            
            if 'symbol' in error_data:
                message += f"📊 Пара: <b>{error_data['symbol']}</b>\n"
            
            if 'action' in error_data:
                message += f"🔧 Дія: <b>{error_data['action']}</b>\n"
            
            # Додамо API відповідь, якщо вона є і це помилка біржі
            if 'api_response' in error_data and "EXCHANGE" in error_type.upper():
                api_response_str = str(error_data['api_response'])
                if len(api_response_str) > 500:
                    api_response_str = api_response_str[:500] + "..."
                message += f"📄 Відповідь API: {api_response_str}\n"

            return await self.send_message(message)
            
        except Exception as e:
            logger.error(f"Помилка відправки помилки: {e}") # Не exc_info, щоб уникнути рекурсії логування
            return False
    
    async def send_market_analysis(self, analysis_data: Dict[str, Any]) -> bool:
        """Відправка аналізу ринку"""
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            message = f"📊 <b>Аналіз ринку</b>\n"
            message += f"⏰ Час: {timestamp}\n\n"
            
            for symbol, data in analysis_data.items():
                if isinstance(data, dict):
                    signal = data.get('signal', 'HOLD')
                    confidence = data.get('confidence', 0)
                    
                    if signal == 'BUY':
                        signal_emoji = "🟢"
                        signal_text = "LONG"
                    elif signal == 'SELL':
                        signal_emoji = "🔴"
                        signal_text = "SHORT"
                    else:
                        signal_emoji = "⚪"
                        signal_text = "HOLD"
                    
                    message += f"{signal_emoji} <b>{symbol}</b>: {signal_text} ({confidence}/4)\n"
                    
                    if data.get('volume_surge'):
                        message += f"  ⚡ Volume Surge\n"
                    if data.get('super_volume_surge'):
                        message += f"  🌟 SUPER Volume Surge\n"
            
            return await self.send_message(message)
            
        except Exception as e:
            logger.error(f"Помилка відправки аналізу ринку: {e}", exc_info=True)
            return False
    
    async def send_daily_summary(self, summary_data: Dict[str, Any]) -> bool:
        """Відправка денного підсумку"""
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            message = f"📈 <b>Денний підсумок</b>\n"
            message += f"⏰ Дата: {timestamp[:10]}\n\n"
            
            total_trades = summary_data.get('total_trades', 0)
            winning_trades = summary_data.get('winning_trades', 0)
            losing_trades = summary_data.get('losing_trades', 0)
            
            message += f"🎯 Всього угод: <b>{total_trades}</b>\n"
            
            if total_trades > 0:
                win_rate = (winning_trades / total_trades) * 100
                message += f"✅ Прибуткових: <b>{winning_trades}</b>\n"
                message += f"❌ Збиткових: <b>{losing_trades}</b>\n"
                message += f"📊 Вінрейт: <b>{win_rate:.1f}%</b>\n\n"
            
            total_pnl = summary_data.get('total_pnl', 0)
            pnl_emoji = "💚" if total_pnl >= 0 else "❤️"
            message += f"{pnl_emoji} Загальний P&L: <b>{total_pnl:+.4f} USDT</b>\n"
            
            current_balance = summary_data.get('current_balance', 0)
            message += f"💰 Поточний баланс: <b>{current_balance:.2f} USDT</b>\n"
            
            return await self.send_message(message)
            
        except Exception as e:
            logger.error(f"Помилка відправки денного підсумку: {e}", exc_info=True)
            return False
    
    async def test_connection(self) -> bool:
        """Тестування з'єднання з Telegram"""
        if not self.bot:
            return False
        
        try:
            test_message = "🤖 Тест з'єднання: Telegram бот працює!"
            return await self.send_message(test_message)
            
        except Exception as e:
            logger.error(f"Помилка тестування Telegram з'єднання: {e}")
            return False