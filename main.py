import asyncio
from prettytable import PrettyTable
from datetime import datetime
import time
from notify import notify
from websocket import ws_service
import yaml
import os
import signal

def load_config():
    """加载配置文件"""
    config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

# 加载配置
config = load_config()
cryptoData = config['trading_pairs']
notification_enabled = config['notification'].get('enabled', True)  # 默认启用通知
notification_interval = config['notification']['interval']
notification_icon = config['notification']['icon']

# 存储最新价格数据
latest_prices = {}

# 创建表格
table = PrettyTable()
table.field_names = ["交易对", "最新价格", "24h涨跌", "涨跌幅", "更新时间"]

def format_price(price):
    """根据价格大小决定小数位数"""
    if price < 10:
        return f"{price:.4f}"
    return f"{price:.2f}"

def format_price_change(price_change, price_change_percent):
    """格式化价格变化，添加颜色和箭头"""
    price_str = format_price(abs(price_change))
    if price_change > 0:
        return f"↑ +{price_str} (+{price_change_percent:.2f}%)"
    elif price_change < 0:
        return f"↓ -{price_str} ({price_change_percent:.2f}%)"
    else:
        return f"-- {price_str} ({price_change_percent:.2f}%)"

def get_trend_symbol(percent):
    """根据涨跌幅返回趋势符号"""
    if percent > 0:
        return "📈"
    elif percent < 0:
        return "📉"
    return "➡️"

async def handle_ticker(data):
    try:
        symbol = data['symbol']
        latest_prices[symbol] = data
        
        # 清空表格并重新添加所有数据
        table.clear_rows()
        for sym in cryptoData:
            if sym in latest_prices:
                price_data = latest_prices[sym]
                table.add_row([
                    sym,
                    format_price(price_data['price']),
                    format_price(price_data['price_change']),
                    f"{price_data['price_change_percent']:.2f}%",
                    price_data['last_update'].strftime('%H:%M:%S')
                ])
        
        # 清屏并打印表格
        print("\033[H\033[J")  # 清屏
        print(table)
    except Exception as e:
        print(f"处理价格更新时出错: {e}")

async def send_price_notification():
    if not notification_enabled:
        print("系统通知已禁用")
        return

    while True:
        try:
            # 等待配置的时间间隔
            await asyncio.sleep(notification_interval)
            
            if not latest_prices:
                print("暂无价格数据，跳过通知")
                continue
                
            # 构建通知消息
            current_time = datetime.now().strftime('%H:%M:%S')
            message_parts = []
            
            # 只显示 BTC 和 ETH
            main_pairs = ['BTCUSDT', 'ETHUSDT']
            for sym in main_pairs:
                if sym in latest_prices:
                    price_data = latest_prices[sym]
                    trend = get_trend_symbol(price_data['price_change_percent'])
                    price_change = format_price_change(
                        price_data['price_change'],
                        price_data['price_change_percent']
                    )
                    
                    # 使用更紧凑的格式
                    pair_info = (
                        f"{trend} {sym.replace('USDT', '')}: "
                        f"${format_price(price_data['price'])} "
                        f"{price_change}"
                    )
                    message_parts.append(pair_info)
            
            # 用空格连接消息
            message = "  |  ".join(message_parts)
            
            # 发送通知
            notify(
                title='加密货币实时行情',
                subtitle=f'更新时间: {current_time}',
                message=message,
                appIcon=notification_icon
            )
        except asyncio.CancelledError:
            break
        except Exception as e:
            print(f"发送通知时出错: {e}")

async def subscribe_all_pairs():
    """订阅所有交易对"""
    for symbol in cryptoData:
        print(f"订阅 {symbol} 的行情数据...")
        await ws_service.subscribe_ticker(symbol, handle_ticker)
        # 每个订阅之间稍微延迟一下，避免请求过于密集
        await asyncio.sleep(0.5)

async def cleanup(tasks):
    """清理所有任务"""
    for task in tasks:
        if not task.done():
            task.cancel()
    
    # 等待所有任务完成
    if tasks:
        await asyncio.gather(*tasks, return_exceptions=True)

async def main():
    # 存储所有任务以便清理
    tasks = set()
    
    try:
        print("正在启动加密货币价格监控...")
        print(f"系统通知状态: {'启用' if notification_enabled else '禁用'}")
        
        # 连接WebSocket
        await ws_service.connect()
        
        # 等待连接稳定
        await asyncio.sleep(2)
        
        print("正在订阅交易对...")
        # 订阅所有交易对
        await subscribe_all_pairs()
        
        print("所有交易对订阅完成，等待数据更新...")
        
        # 启动通知任务
        if notification_enabled:
            notification_task = asyncio.create_task(send_price_notification())
            tasks.add(notification_task)
        
        # 保持程序运行
        while True:
            await asyncio.sleep(1)
            
    except asyncio.CancelledError:
        print("\n正在优雅关闭程序...")
    except Exception as e:
        print(f"发生错误: {e}")
    finally:
        # 清理任务
        await cleanup(tasks)
        # 关闭连接
        await ws_service.disconnect()

def run():
    """程序入口点"""
    try:
        # 设置信号处理
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # 添加信号处理器
        def signal_handler():
            for task in asyncio.all_tasks(loop):
                task.cancel()
        
        loop.add_signal_handler(signal.SIGINT, signal_handler)
        
        # 运行主程序
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        pass
    finally:
        # 关闭事件循环
        try:
            loop.close()
        except Exception:
            pass
        print("\n程序已关闭")

if __name__ == "__main__":
    run()