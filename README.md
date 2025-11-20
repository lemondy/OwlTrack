# CryptoBar - macOS 菜单栏加密货币行情显示

一个在 macOS 菜单栏显示加密货币实时价格的轻量级应用。

## 功能特点

- ✅ 实时显示多个币种价格和涨跌幅
- ✅ 自动轮播切换币种
- ✅ 支持自定义币种列表
- ✅ 支持自定义刷新间隔
- ✅ 原生 macOS 设置界面
- ✅ 数据来源：Hyperliquid 交易所

## 使用说明

### 安装

```bash
# 安装依赖
pip3 install rumps requests pyobjc-framework-Cocoa

# 打包应用
python3 setup.py py2app

# 运行
open dist/OwlTrack.app
```

### 菜单栏图标位置调整

**如何将 OwlTrack 移到菜单栏最右侧：**

1. 按住 `⌘ Command` 键
2. 用鼠标点击并拖动 OwlTrack 图标
3. 拖到您想要的位置（越靠右越接近系统图标）

**注意事项：**
- 无法拖到系统图标（时间、电池等）的右侧
- macOS 会记住图标位置，下次启动时保持相同位置
- 您可以随时重新调整位置

### 设置

点击菜单栏图标 → 选择"设置 (Preferences)"

**币种列表：**
- 输入币种代码，用英文逗号分隔
- 例如：`BTC,ETH,SOL,HYPE`
- 支持的币种：Hyperliquid 交易所上线的所有币种

**刷新间隔：**
- 设置菜单栏轮播切换的时间间隔（秒）
- 建议：3-5 秒
- 数据每 10 秒自动更新

### 支持的币种示例

常见币种（大小写不敏感）：
- **主流币**：BTC, ETH, SOL, BNB, ADA
- **Layer 2**：ARB, OP
- **DeFi**：UNI, AAVE, LINK
- **其他**：ATOM, DOGE, LTC, XRP, SUI, INJ, APE, HYPE

**查看所有支持的币种：**
访问 [Hyperliquid](https://hyperliquid.xyz) 查看完整币种列表。

## 显示格式

```
币种|价格|涨跌幅
例如：BTC|90038|-3.4%
     SOL|134.56|-3.6%
```

## 开发

### 直接运行（开发模式）

```bash
python3 owl_track.py
```


### 配置文件位置

```
~/.owl_track_config.json
```

## 故障排除

### 1. 菜单栏不显示图标

- 检查菜单栏空间是否足够
- 关闭一些不常用的菜单栏图标
- 重启应用

### 2. 显示 "..." 或 "⚠️"

- `...` = 正在加载数据
- `⚠️` = 网络错误

**解决方法：**
- 检查网络连接
- 点击"立即刷新 (Refresh)"
- 等待 10 秒自动重试

### 3. 某些币种不显示

- 确认币种在 Hyperliquid 交易所上线
- 检查币种代码拼写是否正确
- 币种代码大小写不敏感

### 4. 设置保存后没反应

- 数据会在最多 10 秒内自动更新
- 可手动点击"立即刷新"

## 技术栈

- **UI 框架**：rumps (macOS 菜单栏应用)
- **原生界面**：PyObjC (macOS 原生窗口)
- **网络请求**：requests
- **数据源**：Hyperliquid API
- **打包工具**：py2app

## 许可证

MIT License

## 更新日志

### v1.0.0
- 初始版本
- 支持多币种实时显示
- 支持自定义设置
- 原生 macOS 设置界面

