# 贡献指南

感谢您对本项目感兴趣！我们欢迎任何形式的贡献，包括但不限于：

- 报告问题
- 提交功能建议
- 提交代码改进
- 改进文档

## 如何贡献

1. Fork 本仓库
2. 创建您的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交您的改动 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建一个 Pull Request

## 开发指南

### 环境设置

1. 创建并激活虚拟环境：
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
.\venv\Scripts\activate  # Windows
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

### 代码风格

- 遵循 PEP 8 编码规范
- 使用有意义的变量名和函数名
- 添加适当的注释和文档字符串
- 保持代码简洁清晰

### 提交消息规范

提交消息应该清晰地描述改动内容，建议使用以下格式：

- feat: 新功能
- fix: 修复问题
- docs: 文档改动
- style: 代码格式改动
- refactor: 代码重构
- test: 测试相关
- chore: 构建过程或辅助工具的变动

示例：`feat: 添加价格波动提醒功能`

### 测试

- 在提交代码前，请确保程序能够正常运行
- 测试各种可能的使用场景
- 确保错误处理机制正常工作

## 问题报告

创建 issue 时，请包含以下信息：

- 问题描述
- 复现步骤
- 期望行为
- 实际行为
- 运行环境（操作系统、Python 版本等）
- 相关的错误信息或截图

## 功能建议

提出新功能建议时，请说明：

- 功能描述
- 使用场景
- 预期效果
- 可能的实现方式（可选）

## 注意事项

- 请确保您的代码符合项目的开源协议（MIT）
- 不要提交敏感信息（如 API 密钥）
- 保持代码的向后兼容性
- 重大改动请先创建 issue 讨论

再次感谢您的贡献！ 