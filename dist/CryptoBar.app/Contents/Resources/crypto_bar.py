import rumps
import requests
import threading
import time
import json
import os
import sys
from Cocoa import (
    NSWindow, NSTextField, NSButton, NSApplication,
    NSMakeRect, NSBackingStoreBuffered, NSClosableWindowMask,
    NSTitledWindowMask, NSWindowStyleMaskClosable, NSWindowStyleMaskTitled,
    NSApp, NSAlert
)
from AppKit import NSFont

# 配置文件路径
CONFIG_FILE = os.path.expanduser("~/.crypto_bar_config.json")

# 默认配置
DEFAULT_CONFIG = {
    "coins": ["BTC", "ETH", "SOL", "HYPE"],
    "refresh_interval": 3,
    "source": "hyperliquid",
    "api_url": "https://api.hyperliquid.xyz/info"
}

class CryptoTickerApp(rumps.App):
    def __init__(self):
        # 初始标题设为非常短的字符，防止被系统隐藏
        super(CryptoTickerApp, self).__init__("⏳", icon=None)
        
        print("App launched. Waiting for header space...")
        
        # 发送一个通知，证明程序活着
        rumps.notification("CryptoBar 已启动", "正在获取数据...", "如果菜单栏没显示，请关闭一些右侧的其他图标")

        self.config = self.load_config()
        self.coins = self.config["coins"]
        self.current_coin_index = 0
        self.market_data = {} 
        self.last_error = None
        
        # 添加锁，防止多线程同时请求 API
        self.fetch_lock = threading.Lock()
        
        self.menu = [
            rumps.MenuItem("设置 (Preferences)", callback=self.open_preferences),
            rumps.MenuItem("立即刷新 (Refresh)", callback=self.force_refresh),
            rumps.separator,
        ]

        self.data_thread = threading.Thread(target=self.fetch_data_loop, daemon=True)
        self.data_thread.start()

        self.timer = rumps.Timer(self.update_display, self.config["refresh_interval"])
        self.timer.start()

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    return json.load(f)
            except:
                return DEFAULT_CONFIG
        return DEFAULT_CONFIG

    def save_config(self):
        with open(CONFIG_FILE, 'w') as f:
            json.dump(self.config, f)

    def fetch_data_loop(self):
        while True:
            self.fetch_hyperliquid_data()
            time.sleep(10)

    def fetch_hyperliquid_data(self):
        # 使用锁确保同一时间只有一个线程在请求 API
        with self.fetch_lock:
            try:
                url = self.config["api_url"]
                headers = {"Content-Type": "application/json"}
                payload = {"type": "metaAndAssetCtxs"}
                
                # 使用更短的超时时间，并分别设置连接超时和读取超时
                response = requests.post(url, json=payload, headers=headers, timeout=(5, 10))
                
                if response.status_code == 200:
                    data = response.json()
                    universe = data[0]['universe']
                    asset_ctxs = data[1]
                    
                    new_data = {}
                    
                    for i, asset in enumerate(universe):
                        coin_name = asset['name']
                        if coin_name in self.coins:
                            price_info = asset_ctxs[i]
                            current_price = float(price_info['markPx'])
                            prev_day_price = float(price_info['prevDayPx'])
                            
                            if prev_day_price > 0:
                                change_percent = ((current_price - prev_day_price) / prev_day_price) * 100
                            else:
                                change_percent = 0.0
                                
                            new_data[coin_name] = {
                                "price": current_price,
                                "change_24h": change_percent
                            }
                    
                    self.market_data = new_data
                    self.last_error = None
                else:
                    self.last_error = f"Err: {response.status_code}"
                        
            except Exception as e:
                self.last_error = "Net Err"
                print(f"Fetch Error: {type(e).__name__}: {e}")

    def update_display(self, _):
        if self.last_error and not self.market_data:
            self.title = "⚠️"
            return

        if not self.market_data:
            self.title = "..."
            return

        if not self.coins:
            self.title = "No Coins"
            return

        coin = self.coins[self.current_coin_index]
        data = self.market_data.get(coin)

        if data:
            price = data['price']
            change = data['change_24h']
            
            if price >= 1000:
                price_str = f"{int(price)}" 
            elif price >= 1:
                price_str = f"{price:.2f}"
            else:
                price_str = f"{price:.3f}"
            
            # 确定百分比符号
            if change >= 0:
                change_sign = "+"
            else:
                change_sign = "-"
            
            display_text = f"{coin}|{price_str}|{change_sign}{abs(change):.1f}%"
            
            self.title = display_text
        else:
            self.title = f"{coin} ?"

        self.current_coin_index = (self.current_coin_index + 1) % len(self.coins)

    def open_preferences(self, _):
        """使用 PyObjC 创建原生 macOS 设置窗口"""
        try:
            # 创建窗口
            window_style = NSWindowStyleMaskTitled | NSWindowStyleMaskClosable
            window = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
                NSMakeRect(0, 0, 400, 220),
                window_style,
                NSBackingStoreBuffered,
                False
            )
            window.setTitle_("CryptoBar 设置")
            window.center()
            window.setLevel_(3)  # 确保窗口在最前面
            
            # 标签：币种列表
            label1 = NSTextField.alloc().initWithFrame_(NSMakeRect(20, 160, 150, 24))
            label1.setStringValue_("币种列表（逗号分隔）:")
            label1.setBezeled_(False)
            label1.setDrawsBackground_(False)
            label1.setEditable_(False)
            label1.setSelectable_(False)
            window.contentView().addSubview_(label1)
            
            # 输入框：币种列表
            self.coins_field = NSTextField.alloc().initWithFrame_(NSMakeRect(20, 130, 360, 24))
            self.coins_field.setStringValue_(",".join(self.coins))
            self.coins_field.setFont_(NSFont.systemFontOfSize_(13))
            window.contentView().addSubview_(self.coins_field)
            
            # 标签：刷新间隔
            label2 = NSTextField.alloc().initWithFrame_(NSMakeRect(20, 90, 150, 24))
            label2.setStringValue_("刷新间隔（秒）:")
            label2.setBezeled_(False)
            label2.setDrawsBackground_(False)
            label2.setEditable_(False)
            label2.setSelectable_(False)
            window.contentView().addSubview_(label2)
            
            # 输入框：刷新间隔
            self.interval_field = NSTextField.alloc().initWithFrame_(NSMakeRect(20, 60, 100, 24))
            self.interval_field.setStringValue_(str(self.config["refresh_interval"]))
            self.interval_field.setFont_(NSFont.systemFontOfSize_(13))
            window.contentView().addSubview_(self.interval_field)
            
            # 保存按钮
            save_button = NSButton.alloc().initWithFrame_(NSMakeRect(280, 20, 100, 32))
            save_button.setTitle_("保存")
            save_button.setBezelStyle_(1)  # Rounded
            save_button.setTarget_(self)
            save_button.setAction_("savePreferences:")
            window.contentView().addSubview_(save_button)
            
            # 取消按钮
            cancel_button = NSButton.alloc().initWithFrame_(NSMakeRect(170, 20, 100, 32))
            cancel_button.setTitle_("取消")
            cancel_button.setBezelStyle_(1)  # Rounded
            cancel_button.setTarget_(self)
            cancel_button.setAction_("cancelPreferences:")
            window.contentView().addSubview_(cancel_button)
            
            # 保存窗口引用
            self.settings_window = window
            
            # 显示窗口
            window.makeKeyAndOrderFront_(None)
            NSApp.activateIgnoringOtherApps_(True)
            
        except Exception as e:
            print(f"Settings Error: {e}")
            import traceback
            traceback.print_exc()
            rumps.alert("错误", f"无法打开设置窗口: {e}")
    
    def savePreferences_(self, sender):
        """保存设置"""
        try:
            # 获取输入值
            coins_text = self.coins_field.stringValue()
            interval_text = self.interval_field.stringValue()
            
            # 处理币种列表
            coins_text = coins_text.replace("，", ",").replace(" ", "")
            new_coins = [c.upper() for c in coins_text.split(",") if c]
            
            # 处理刷新间隔
            try:
                new_interval = int(interval_text)
                if new_interval < 1:
                    new_interval = 1
            except ValueError:
                rumps.alert("错误", "刷新间隔必须是一个正整数")
                return
            
            # 应用配置
            self.coins = new_coins
            self.config["coins"] = self.coins
            self.config["refresh_interval"] = new_interval
            self.save_config()
            
            # 停止定时器
            self.timer.stop()
            
            # 重置显示状态
            self.current_coin_index = 0
            self.title = "⏳"
            
            # 清空旧数据，强制重新获取
            self.market_data = {}
            
            # 关闭窗口
            self.settings_window.close()
            
            # 重启定时器（使用新的刷新间隔）
            self.timer = rumps.Timer(self.update_display, new_interval)
            self.timer.start()
            
            # 显示通知
            rumps.notification("设置已保存", "配置已更新", f"数据将在 {new_interval} 秒内自动刷新")
            
        except Exception as e:
            print(f"Save Error: {e}")
            import traceback
            traceback.print_exc()
            rumps.alert("错误", f"保存设置失败: {e}")
    
    def cancelPreferences_(self, sender):
        """取消设置"""
        try:
            self.settings_window.close()
        except Exception as e:
            print(f"Cancel Error: {e}")

    def force_refresh(self, _):
        self.title = "..."
        t = threading.Thread(target=self.fetch_hyperliquid_data)
        t.start()

if __name__ == "__main__":
    rumps.debug_mode(False)
    app = CryptoTickerApp()
    app.run()