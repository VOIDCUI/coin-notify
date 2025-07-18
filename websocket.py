import json
import time
import websockets
import asyncio
from datetime import datetime

class CryptoWebSocketService:
    def __init__(self):
        self.ws = None
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5
        self.reconnect_delay = 1
        self.subscribers = {}
        self.kline_subscribers = {}
        self.ws_url = 'wss://ws.okx.com:8443/ws/v5/public'
        self.running = False

    async def connect(self):
        try:
            print("正在连接到 OKX WebSocket...")
            self.ws = await websockets.connect(self.ws_url)
            print("OKX WebSocket 连接成功")
            self.reconnect_attempts = 0
            self.running = True

            # 开始消息处理循环
            asyncio.create_task(self.message_handler())

        except Exception as error:
            print(f"连接失败: {error}")
            await self.attempt_reconnect()

    async def disconnect(self):
        """优雅关闭 WebSocket 连接"""
        print("正在关闭 WebSocket 连接...")
        self.running = False
        
        if self.ws:
            try:
                await self.ws.close()
            except Exception:
                pass  # 静默处理关闭错误
            self.ws = None
            
        self.subscribers.clear()
        self.kline_subscribers.clear()
        print("WebSocket 连接已关闭")

    async def subscribe_ticker(self, symbol, callback):
        print(f"正在订阅 {symbol} 的行情...")
        if symbol not in self.subscribers:
            self.subscribers[symbol] = set()
        self.subscribers[symbol].add(callback)

        if self.ws and not self.ws.closed:
            subscription = {
                "op": "subscribe",
                "args": [{
                    "channel": "tickers",
                    "instId": self.convert_symbol_for_okx(symbol)
                }]
            }
            print(f"发送订阅请求: {json.dumps(subscription)}")
            await self.ws.send(json.dumps(subscription))
            # 等待一小段时间确保订阅请求被处理
            await asyncio.sleep(0.1)

    async def unsubscribe_ticker(self, symbol, callback):
        if symbol in self.subscribers:
            self.subscribers[symbol].discard(callback)
            if not self.subscribers[symbol]:
                del self.subscribers[symbol]
                if self.ws and not self.ws.closed:
                    await self.send_unsubscription(symbol, 'ticker')

    async def subscribe_kline(self, symbol, interval, callback):
        key = f"{symbol}_{interval}"
        if key not in self.kline_subscribers:
            self.kline_subscribers[key] = set()
        self.kline_subscribers[key].add(callback)

        if self.ws and not self.ws.closed:
            await self.send_subscription(symbol, 'kline', interval)

    async def unsubscribe_kline(self, symbol, interval, callback):
        key = f"{symbol}_{interval}"
        if key in self.kline_subscribers:
            self.kline_subscribers[key].discard(callback)
            if not self.kline_subscribers[key]:
                del self.kline_subscribers[key]
                if self.ws and not self.ws.closed:
                    await self.send_unsubscription(symbol, 'kline', interval)

    async def send_subscription(self, symbol, type_, interval=None):
        if not self.ws or self.ws.closed:
            return

        message = {
            "op": "subscribe",
            "args": []
        }

        if type_ == 'ticker':
            message["args"].append({
                "channel": "tickers",
                "instId": self.convert_symbol_for_okx(symbol)
            })
        elif type_ == 'kline' and interval:
            message["args"].append({
                "channel": f"candle{self.convert_interval(interval)}",
                "instId": self.convert_symbol_for_okx(symbol)
            })

        print(f"发送订阅请求: {json.dumps(message)}")
        await self.ws.send(json.dumps(message))

    async def send_unsubscription(self, symbol, type_, interval=None):
        if not self.ws or self.ws.closed:
            return

        message = {
            "op": "unsubscribe",
            "args": []
        }

        if type_ == 'ticker':
            message["args"].append({
                "channel": "tickers",
                "instId": self.convert_symbol_for_okx(symbol)
            })
        elif type_ == 'kline' and interval:
            message["args"].append({
                "channel": f"candle{self.convert_interval(interval)}",
                "instId": self.convert_symbol_for_okx(symbol)
            })

        await self.ws.send(json.dumps(message))

    async def message_handler(self):
        print("开始处理 WebSocket 消息...")
        while self.running:
            try:
                if self.ws:
                    message = await self.ws.recv()
                    print(f"收到消息: {message}")
                    data = json.loads(message)
                    
                    # 处理订阅确认消息
                    if 'event' in data:
                        print(f"收到事件消息: {data['event']}")
                        continue

                    # 处理心跳消息
                    if 'op' in data and data['op'] == 'pong':
                        continue
                        
                    await self.handle_message(data)
            except websockets.ConnectionClosed:
                print("WebSocket 连接已关闭")
                await self.attempt_reconnect()
                break
            except Exception as error:
                print(f"处理消息时出错: {error}")
                import traceback
                print(traceback.format_exc())

    async def handle_message(self, data):
        try:
            if not data.get('data') or not isinstance(data['data'], list):
                print(f"无效的数据格式: {data}")
                return

            for item in data['data']:
                if data.get('arg', {}).get('channel') == 'tickers':
                    normalized_symbol = self.convert_okx_symbol_back(item['instId'])
                    crypto_data = {
                        'symbol': normalized_symbol,
                        'price': float(item['last']),
                        'price_change': float(item['last']) - float(item['open24h']),
                        'price_change_percent': ((float(item['last']) - float(item['open24h'])) / float(item['open24h'])) * 100,
                        'volume': float(item['vol24h']),
                        'last_update': datetime.fromtimestamp(int(item['ts']) / 1000)
                    }

                    if normalized_symbol in self.subscribers:
                        print(f"正在处理 {normalized_symbol} 的数据更新")
                        for callback in self.subscribers[normalized_symbol]:
                            await callback(crypto_data)

                elif data.get('arg', {}).get('channel', '').startswith('candle'):
                    normalized_symbol = self.convert_okx_symbol_back(data['arg']['instId'])
                    kline_data = {
                        'timestamp': int(item[0]),
                        'open': float(item[1]),
                        'high': float(item[2]),
                        'low': float(item[3]),
                        'close': float(item[4]),
                        'volume': float(item[5])
                    }

                    channel = data['arg']['channel']
                    interval = channel.replace('candle', '').lower()
                    key = f"{normalized_symbol}_{interval}"

                    if key in self.kline_subscribers:
                        for callback in self.kline_subscribers[key]:
                            await callback([kline_data])
        except Exception as e:
            print(f"处理数据时出错: {e}")
            import traceback
            print(traceback.format_exc())

    async def resubscribe_all(self):
        print("正在重新订阅所有交易对...")
        for symbol in self.subscribers:
            await self.send_subscription(symbol, 'ticker')
            # 添加延迟避免请求过于密集
            await asyncio.sleep(0.1)

        for key in self.kline_subscribers:
            symbol, interval = key.split('_')
            await self.send_subscription(symbol, 'kline', interval)
            await asyncio.sleep(0.1)

    async def attempt_reconnect(self):
        if self.reconnect_attempts < self.max_reconnect_attempts:
            self.reconnect_attempts += 1
            print(f"尝试重新连接... ({self.reconnect_attempts}/{self.max_reconnect_attempts})")

            await asyncio.sleep(self.reconnect_delay * self.reconnect_attempts)
            await self.connect()
        else:
            print("达到最大重连次数")
            self.running = False

    def convert_interval(self, interval):
        interval_map = {
            '1m': '1m',
            '5m': '5m',
            '15m': '15m',
            '1h': '1H',
            '4h': '4H',
            '1d': '1D'
        }
        return interval_map.get(interval, '1m')

    def convert_symbol_for_okx(self, symbol):
        if symbol.endswith('USDT'):
            base = symbol.replace('USDT', '')
            return f"{base}-USDT"
        return symbol

    def convert_okx_symbol_back(self, okx_symbol):
        return okx_symbol.replace('-', '')

# 创建单例实例
ws_service = CryptoWebSocketService()

# 使用示例
async def main():
    # 连接WebSocket
    await ws_service.connect()

    # 订阅示例
    async def handle_ticker(data):
        print(f"Received ticker data: {data}")

    async def handle_kline(data):
        print(f"Received kline data: {data}")

    # 示例：批量订阅多个交易对
    symbols = [
        "BTCUSDT",
        "ETHUSDT",
        # 可以在这里添加更多交易对
    ]
    
    # 批量订阅ticker
    for symbol in symbols:
        await ws_service.subscribe_ticker(symbol, handle_ticker)
    
    # 批量订阅K线数据
    intervals = ["1m", "5m"]  # 可以设置多个时间周期
    for symbol in symbols:
        for interval in intervals:
            await ws_service.subscribe_kline(symbol, interval, handle_kline)

    # 保持运行
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        await ws_service.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
