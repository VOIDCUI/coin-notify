# 加密货币价格监控工具

这是一个实时监控加密货币价格的工具，通过 WebSocket 连接获取实时价格数据，并通过控制台表格展示和系统通知提醒功能。

## 功能特点

- 实时监控多个加密货币交易对的价格
- 控制台表格实时展示价格、涨跌幅等信息
- 可选的系统通知功能，每分钟推送 BTC 和 ETH 的最新价格
- 价格显示智能精度：
  - 价格 < 10 时显示 4 位小数
  - 价格 ≥ 10 时显示 2 位小数
- 支持的交易对：
  - BTC/USDT
  - ETH/USDT
  - SOL/USDT
  - XRP/USDT
  - DOGE/USDT
  - ADA/USDT
  - BNB/USDT
  - 更多...

## 系统要求

- Python 3.7+
- macOS（系统通知功能需要）
- Terminal-notifier（用于 macOS 系统通知，仅在启用通知功能时需要）

## 安装步骤

1. 克隆项目到本地：
```bash
git clone https://github.com/VOIDCUI/coin-notify.git
cd coin-notify
```

2. 创建并激活虚拟环境：
```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
## macOS/Linux:
source venv/bin/activate
## Windows:
.\venv\Scripts\activate
```

3. 安装项目依赖：
```bash
pip install -r requirements.txt
```

4. 安装 terminal-notifier（仅 macOS 且需要系统通知时）：
```bash
sudo gem install terminal-notifier
```

## 使用方法

1. 确保已激活虚拟环境：
```bash
# macOS/Linux:
source venv/bin/activate
# Windows:
.\venv\Scripts\activate
```

2. 运行程序：
```bash
python main.py
```

3. 查看输出：
   - 控制台会显示一个实时更新的价格表格，包含所有交易对的详细信息
   - 如果启用了通知功能，每分钟会收到一次系统通知，显示 BTC 和 ETH 的最新价格和涨跌情况
   - 价格显示会根据大小自动调整精度
   - 使用趋势图标（📈 📉）直观显示价格走势

4. 退出程序：
   - 按 `Ctrl+C` 终止程序运行（程序会优雅关闭）
   - 使用 `deactivate` 命令退出虚拟环境

## 项目结构

```
coin-notify/
├── README.md           # 项目说明文档
├── requirements.txt    # 项目依赖
├── config.yaml        # 配置文件
├── main.py            # 主程序
├── notify.py          # 通知模块
└── websocket.py       # WebSocket 连接模块
```

## 配置文件说明

项目使用 `config.yaml` 文件进行配置管理。您可以根据需要修改以下配置项：

```yaml
# 交易对配置
trading_pairs:  # 要监控的交易对列表
  - BTCUSDT
  - ETHUSDT
  - SOLUSDT
  # 可以添加更多...

# 通知配置
notification:
  enabled: false   # 是否启用系统通知（true/false）
  interval: 60    # 通知间隔（秒）
  icon: "图标URL" # 通知图标

# WebSocket配置
websocket:
  max_reconnect_attempts: 5  # 最大重连次数
  reconnect_delay: 1  # 重连延迟（秒）
```

### 通知配置说明
- `enabled`: 设置为 `false` 可以完全禁用系统通知
- `interval`: 控制通知推送的时间间隔
- `icon`: 通知图标的 URL

## 注意事项

1. 确保网络连接稳定，以保证 WebSocket 连接的可靠性
2. 程序会自动处理断线重连，最多尝试 5 次重连
3. 如果长时间没有数据更新，请检查网络连接
4. 虚拟环境可以有效避免与系统其他 Python 项目的依赖冲突
5. 修改配置后需要重启程序才能生效
6. 系统通知仅显示 BTC 和 ETH 的信息，以保持通知的简洁性
7. 如果禁用了通知功能，无需安装 terminal-notifier

## 常见问题

1. 如果收不到系统通知：
   - 确认配置文件中的 notification.enabled 是否为 true
   - 确认是否已安装 terminal-notifier
   - 检查系统通知设置是否允许通知
   - 确认通知图标 URL 是否可访问

2. 如果表格显示异常：
   - 确认终端窗口大小是否足够
   - 尝试调整终端窗口大小

3. 如果程序无法启动：
   - 确认是否已激活虚拟环境
   - 检查依赖是否安装完整
   - 查看错误信息进行相应处理

4. 如果配置文件有误：
   - 检查 YAML 格式是否正确
   - 确保所有必需的配置项都存在
   - 使用有效的交易对符号

## 贡献指南

欢迎提交 Issue 和 Pull Request 来帮助改进这个项目。详细信息请参考 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详细信息。 