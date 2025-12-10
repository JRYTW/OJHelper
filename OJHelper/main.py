import customtkinter as ctk
import threading
import time
import os
from browser_bot import OJBot
from ai_engine import solve_challenge

# --- 強制清理殘留驅動 ---
def force_cleanup():
    try:
        os.system("taskkill /f /im chromedriver.exe >nul 2>&1")
    except Exception:
        pass

class OJHelprApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        ctk.set_appearance_mode("Light")
        
        # 設定視窗大小
        self.geometry("480x820")
        self.title("OJHelpr")
        self.resizable(False, True)
        self.minsize(480, 700)

        # ============ 配色方案 ============
        self.COLOR_BG = "#FAFAFA"            # 背景
        self.COLOR_ACCENT = "#607D8B"        # 主色（藍灰）
        self.COLOR_ACCENT_HOVER = "#455A64"  # 深藍灰
        self.COLOR_ACCENT_LIGHT = "#90A4AE"  # 淺藍灰
        self.COLOR_TEXT = "#37474F"          # 深灰文字
        self.COLOR_TEXT_SECONDARY = "#78909C" # 次要文字
        self.COLOR_INPUT_BG = "#ECEFF1"      # 輸入框背景
        self.COLOR_CARD_BG = "#FFFFFF"       # 卡片背景
        self.COLOR_LOG_BG = "#F5F5F5"        # 日誌區背景
        self.COLOR_SUCCESS = "#4CAF50"       # 成功綠
        self.COLOR_WARNING = "#FF7043"       # 警告橘
        self.COLOR_BORDER = "#E0E0E0"        # 邊框色
        
        # ============ 字體設定 ============
        self.FONT_TITLE = ("Microsoft JhengHei UI", 28, "bold")
        self.FONT_SECTION = ("Microsoft JhengHei UI", 14, "bold")
        self.FONT_LABEL = ("Microsoft JhengHei UI", 12)
        self.FONT_INPUT = ("Arial", 13)
        self.FONT_SMALL = ("Microsoft JhengHei UI", 11)
        self.FONT_LOG = ("Consolas", 11)

        self.configure(fg_color=self.COLOR_BG)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # ============ 主容器 ============
        self.main_container = ctk.CTkScrollableFrame(
            self, 
            fg_color="transparent",
            scrollbar_button_color=self.COLOR_ACCENT_LIGHT,
            scrollbar_button_hover_color=self.COLOR_ACCENT
        )
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)
        self.main_container.grid_columnconfigure(0, weight=1)

        self.bot = None
        self._build_header()
        self._build_ai_settings_card()
        self._build_account_card()
        self._build_action_section()
        self._build_log_section()

    # ============================
    # 1. Header 區塊
    # ============================
    def _build_header(self):
        header_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        header_frame.grid(row=0, column=0, pady=(10, 25), sticky="ew")
        header_frame.grid_columnconfigure(0, weight=1)

        # Logo 區域
        logo_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        logo_frame.pack()

        # 裝飾線
        accent_bar = ctk.CTkFrame(logo_frame, width=60, height=4, fg_color=self.COLOR_ACCENT, corner_radius=2)
        accent_bar.pack(pady=(0, 12))

        # 標題
        title_label = ctk.CTkLabel(
            logo_frame, 
            text="OJHelpr", 
            font=self.FONT_TITLE, 
            text_color=self.COLOR_ACCENT
        )
        title_label.pack()

        # 副標題
        subtitle_label = ctk.CTkLabel(
            logo_frame, 
            text="AI-Powered Online Judge Assistant\n\nV2.0 Made By JRYTW", 
            font=("Arial", 11), 
            text_color=self.COLOR_TEXT_SECONDARY
        )
        subtitle_label.pack(pady=(2, 0))

    # ============================
    # 2. AI 設定卡片
    # ============================
    def _build_ai_settings_card(self):
        # 卡片容器
        card = ctk.CTkFrame(
            self.main_container, 
            fg_color=self.COLOR_CARD_BG, 
            corner_radius=16,
            border_width=1,
            border_color=self.COLOR_BORDER
        )
        card.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        card.grid_columnconfigure(0, weight=1)

        # 卡片標題
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.grid(row=0, column=0, padx=20, pady=(18, 12), sticky="ew")
        
        icon_label = ctk.CTkLabel(header, text="🤖", font=("Segoe UI Emoji", 18))
        icon_label.pack(side="left")
        
        title_label = ctk.CTkLabel(
            header, 
            text="  AI 設定", 
            font=self.FONT_SECTION, 
            text_color=self.COLOR_TEXT
        )
        title_label.pack(side="left")

        # 分隔線
        separator = ctk.CTkFrame(card, fg_color=self.COLOR_BORDER, height=1)
        separator.grid(row=1, column=0, sticky="ew", padx=20)

        # 內容區
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.grid(row=2, column=0, padx=20, pady=15, sticky="ew")
        content.grid_columnconfigure((0, 1), weight=1)

        # 提供商選擇（左側）
        provider_frame = ctk.CTkFrame(content, fg_color="transparent")
        provider_frame.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        
        ctk.CTkLabel(
            provider_frame, 
            text="AI 提供商", 
            font=self.FONT_LABEL, 
            text_color=self.COLOR_TEXT_SECONDARY
        ).pack(anchor="w", pady=(0, 6))
        
        self.provider_var = ctk.StringVar(value="gemini")
        self.provider_menu = ctk.CTkOptionMenu(
            provider_frame,
            variable=self.provider_var,
            values=["gemini", "chatgpt", "claude", "custom"],
            font=self.FONT_INPUT,
            fg_color=self.COLOR_INPUT_BG,
            button_color=self.COLOR_ACCENT,
            button_hover_color=self.COLOR_ACCENT_HOVER,
            dropdown_fg_color=self.COLOR_CARD_BG,
            dropdown_hover_color=self.COLOR_INPUT_BG,
            text_color=self.COLOR_TEXT,
            height=40,
            corner_radius=10,
            command=self.on_provider_change
        )
        self.provider_menu.pack(fill="x")

        # 模型選擇（右側）
        model_frame = ctk.CTkFrame(content, fg_color="transparent")
        model_frame.grid(row=0, column=1, sticky="ew", padx=(8, 0))
        
        ctk.CTkLabel(
            model_frame, 
            text="模型", 
            font=self.FONT_LABEL, 
            text_color=self.COLOR_TEXT_SECONDARY
        ).pack(anchor="w", pady=(0, 6))
        
        self.model_var = ctk.StringVar(value="gemini-2.5-flash-lite")
        self.model_menu = ctk.CTkOptionMenu(
            model_frame,
            variable=self.model_var,
            values=["gemini-2.5-flash-lite", "gemini-1.5-flash", "gemini-1.5-pro"],
            font=self.FONT_INPUT,
            fg_color=self.COLOR_INPUT_BG,
            button_color=self.COLOR_ACCENT,
            button_hover_color=self.COLOR_ACCENT_HOVER,
            dropdown_fg_color=self.COLOR_CARD_BG,
            dropdown_hover_color=self.COLOR_INPUT_BG,
            text_color=self.COLOR_TEXT,
            height=40,
            corner_radius=10
        )
        self.model_menu.pack(fill="x")

        # RPM 提醒（警告框）
        self.rpm_frame = ctk.CTkFrame(content, fg_color="#FFF3E0", corner_radius=10)
        self.rpm_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(12, 0))
        
        self.lbl_rpm = ctk.CTkLabel(
            self.rpm_frame, 
            text="⚠️  請注意 Gemini API RPM 限制", 
            font=self.FONT_SMALL,
            text_color=self.COLOR_WARNING
        )
        self.lbl_rpm.pack(pady=8, padx=12)

        # API Key 輸入
        api_frame = ctk.CTkFrame(content, fg_color="transparent")
        api_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(12, 0))
        
        ctk.CTkLabel(
            api_frame, 
            text="API Key", 
            font=self.FONT_LABEL, 
            text_color=self.COLOR_TEXT_SECONDARY
        ).pack(anchor="w", pady=(0, 6))
        
        self.entry_api = ctk.CTkEntry(
            api_frame, 
            placeholder_text="在此貼上 API Key",
            font=self.FONT_INPUT,
            fg_color=self.COLOR_INPUT_BG,
            border_color=self.COLOR_BORDER,
            border_width=1,
            text_color=self.COLOR_TEXT,
            height=42,
            corner_radius=10,
            show="●"
        )
        self.entry_api.pack(fill="x")

        # 自訂端點（預設隱藏）
        self.endpoint_frame = ctk.CTkFrame(content, fg_color="transparent")
        
        ctk.CTkLabel(
            self.endpoint_frame, 
            text="自訂 API 端點", 
            font=self.FONT_LABEL, 
            text_color=self.COLOR_TEXT_SECONDARY
        ).pack(anchor="w", pady=(0, 6))
        
        self.entry_endpoint = ctk.CTkEntry(
            self.endpoint_frame, 
            placeholder_text="https://api.example.com/v1/chat/completions",
            font=self.FONT_INPUT,
            fg_color=self.COLOR_INPUT_BG,
            border_color=self.COLOR_BORDER,
            border_width=1,
            text_color=self.COLOR_TEXT,
            height=42,
            corner_radius=10
        )
        self.entry_endpoint.pack(fill="x")

    # ============================
    # 3. 帳號設定卡片
    # ============================
    def _build_account_card(self):
        # 卡片容器
        card = ctk.CTkFrame(
            self.main_container, 
            fg_color=self.COLOR_CARD_BG, 
            corner_radius=16,
            border_width=1,
            border_color=self.COLOR_BORDER
        )
        card.grid(row=2, column=0, sticky="ew", pady=(0, 15))
        card.grid_columnconfigure(0, weight=1)

        # 卡片標題
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.grid(row=0, column=0, padx=20, pady=(18, 12), sticky="ew")
        
        icon_label = ctk.CTkLabel(header, text="🔐", font=("Segoe UI Emoji", 18))
        icon_label.pack(side="left")
        
        title_label = ctk.CTkLabel(
            header, 
            text="  OJ 帳號設定", 
            font=self.FONT_SECTION, 
            text_color=self.COLOR_TEXT
        )
        title_label.pack(side="left")

        # 分隔線
        separator = ctk.CTkFrame(card, fg_color=self.COLOR_BORDER, height=1)
        separator.grid(row=1, column=0, sticky="ew", padx=20)

        # 內容區
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.grid(row=2, column=0, padx=20, pady=15, sticky="ew")
        content.grid_columnconfigure(0, weight=1)

        # Contest URL
        url_frame = ctk.CTkFrame(content, fg_color="transparent")
        url_frame.pack(fill="x", pady=(0, 12))
        
        ctk.CTkLabel(
            url_frame, 
            text="Contest URL", 
            font=self.FONT_LABEL, 
            text_color=self.COLOR_TEXT_SECONDARY
        ).pack(anchor="w", pady=(0, 6))
        
        self.entry_url = ctk.CTkEntry(
            url_frame, 
            placeholder_text="https://example.com/contest/123",
            font=self.FONT_INPUT,
            fg_color=self.COLOR_INPUT_BG,
            border_color=self.COLOR_BORDER,
            border_width=1,
            text_color=self.COLOR_TEXT,
            height=42,
            corner_radius=10
        )
        self.entry_url.pack(fill="x")

        # 帳號密碼區（並排）
        cred_frame = ctk.CTkFrame(content, fg_color="transparent")
        cred_frame.pack(fill="x")
        cred_frame.grid_columnconfigure((0, 1), weight=1)

        # 帳號（左側）
        user_frame = ctk.CTkFrame(cred_frame, fg_color="transparent")
        user_frame.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        
        ctk.CTkLabel(
            user_frame, 
            text="帳號", 
            font=self.FONT_LABEL, 
            text_color=self.COLOR_TEXT_SECONDARY
        ).pack(anchor="w", pady=(0, 6))
        
        self.entry_user = ctk.CTkEntry(
            user_frame, 
            placeholder_text="Username",
            font=self.FONT_INPUT,
            fg_color=self.COLOR_INPUT_BG,
            border_color=self.COLOR_BORDER,
            border_width=1,
            text_color=self.COLOR_TEXT,
            height=42,
            corner_radius=10
        )
        self.entry_user.pack(fill="x")

        # 密碼（右側）
        pass_frame = ctk.CTkFrame(cred_frame, fg_color="transparent")
        pass_frame.grid(row=0, column=1, sticky="ew", padx=(8, 0))
        
        ctk.CTkLabel(
            pass_frame, 
            text="密碼", 
            font=self.FONT_LABEL, 
            text_color=self.COLOR_TEXT_SECONDARY
        ).pack(anchor="w", pady=(0, 6))
        
        self.entry_pass = ctk.CTkEntry(
            pass_frame, 
            placeholder_text="Password",
            font=self.FONT_INPUT,
            fg_color=self.COLOR_INPUT_BG,
            border_color=self.COLOR_BORDER,
            border_width=1,
            text_color=self.COLOR_TEXT,
            height=42,
            corner_radius=10,
            show="●"
        )
        self.entry_pass.pack(fill="x")

    # ============================
    # 4. 啟動按鈕區
    # ============================
    def _build_action_section(self):
        action_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        action_frame.grid(row=3, column=0, sticky="ew", pady=(5, 15))

        self.btn_start = ctk.CTkButton(
            action_frame, 
            text="🚀  開始任務", 
            command=self.start_thread, 
            height=52, 
            corner_radius=14,
            font=("Microsoft JhengHei UI", 15, "bold"),
            fg_color=self.COLOR_ACCENT,
            hover_color=self.COLOR_ACCENT_HOVER,
            text_color="white"
        )
        self.btn_start.pack(fill="x")

        # 狀態指示器
        self.status_frame = ctk.CTkFrame(action_frame, fg_color="transparent")
        self.status_frame.pack(fill="x", pady=(10, 0))
        
        self.status_indicator = ctk.CTkFrame(
            self.status_frame, 
            width=10, 
            height=10, 
            fg_color=self.COLOR_SUCCESS, 
            corner_radius=5
        )
        self.status_indicator.pack(side="left")
        
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="  就緒",
            font=self.FONT_SMALL,
            text_color=self.COLOR_TEXT_SECONDARY
        )
        self.status_label.pack(side="left")

    # ============================
    # 5. 日誌區
    # ============================
    def _build_log_section(self):
        # 日誌卡片
        log_card = ctk.CTkFrame(
            self.main_container, 
            fg_color=self.COLOR_CARD_BG, 
            corner_radius=16,
            border_width=1,
            border_color=self.COLOR_BORDER
        )
        log_card.grid(row=4, column=0, sticky="nsew", pady=(0, 10))
        log_card.grid_columnconfigure(0, weight=1)
        log_card.grid_rowconfigure(1, weight=1)
        
        # 自動調整高度
        self.main_container.grid_rowconfigure(4, weight=1)

        # 標題列
        header = ctk.CTkFrame(log_card, fg_color="transparent")
        header.grid(row=0, column=0, padx=16, pady=(12, 8), sticky="ew")
        
        icon_label = ctk.CTkLabel(header, text="📋", font=("Segoe UI Emoji", 14))
        icon_label.pack(side="left")
        
        title_label = ctk.CTkLabel(
            header, 
            text="  執行日誌", 
            font=self.FONT_LABEL, 
            text_color=self.COLOR_TEXT_SECONDARY
        )
        title_label.pack(side="left")

        # 清除按鈕
        clear_btn = ctk.CTkButton(
            header,
            text="清除",
            width=50,
            height=24,
            corner_radius=6,
            font=self.FONT_SMALL,
            fg_color=self.COLOR_INPUT_BG,
            hover_color=self.COLOR_BORDER,
            text_color=self.COLOR_TEXT_SECONDARY,
            command=self.clear_log
        )
        clear_btn.pack(side="right")

        # 日誌內容
        self.textbox_log = ctk.CTkTextbox(
            log_card, 
            font=self.FONT_LOG,
            fg_color=self.COLOR_LOG_BG,
            text_color=self.COLOR_TEXT,
            corner_radius=10,
            height=150,
            scrollbar_button_color=self.COLOR_ACCENT_LIGHT,
            scrollbar_button_hover_color=self.COLOR_ACCENT
        )
        self.textbox_log.grid(row=1, column=0, padx=12, pady=(0, 12), sticky="nsew")
        
        self.log("系統準備就緒，請設定 AI 提供商和帳號資訊...")

    # ============================
    # 事件處理函式
    # ============================
    def on_provider_change(self, choice):
        """當 AI 提供商改變時，更新模型選單和 RPM 提醒"""
        if choice == "gemini":
            self.model_menu.configure(values=["gemini-2.5-flash-lite", "gemini-1.5-flash", "gemini-1.5-pro"])
            self.model_var.set("gemini-2.5-flash-lite")
            self.lbl_rpm.configure(text="⚠️  請注意 Gemini API RPM 限制")
            self.rpm_frame.configure(fg_color="#FFF3E0")
            self.endpoint_frame.grid_forget()
            
        elif choice == "chatgpt":
            self.model_menu.configure(values=["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"])
            self.model_var.set("gpt-4o-mini")
            self.lbl_rpm.configure(text="⚠️  請注意 ChatGPT API RPM 限制")
            self.rpm_frame.configure(fg_color="#FFF3E0")
            self.endpoint_frame.grid_forget()
            
        elif choice == "claude":
            self.model_menu.configure(values=["claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022", "claude-3-opus-20240229"])
            self.model_var.set("claude-3-5-sonnet-20241022")
            self.lbl_rpm.configure(text="⚠️  請注意 Claude API RPM 限制")
            self.rpm_frame.configure(fg_color="#FFF3E0")
            self.endpoint_frame.grid_forget()
            
        elif choice == "custom":
            self.model_menu.configure(values=["custom-model"])
            self.model_var.set("custom-model")
            self.lbl_rpm.configure(text="ℹ️  請確認自訂 API RPM 限制")
            self.rpm_frame.configure(fg_color="#E3F2FD")
            # 顯示自訂端點輸入框
            self.endpoint_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(12, 0))

    def clear_log(self):
        """清除日誌"""
        self.textbox_log.delete("1.0", "end")
        self.log("日誌已清除")

    def log(self, msg):
        """輸出日誌訊息"""
        timestamp = time.strftime('%H:%M:%S') 
        self.textbox_log.insert("end", f"[{timestamp}] {msg}\n")
        self.textbox_log.see("end")

    def set_status(self, text, color=None):
        """更新狀態指示器"""
        self.status_label.configure(text=f"  {text}")
        if color:
            self.status_indicator.configure(fg_color=color)

    def on_closing(self):
        """關閉視窗時清理資源"""
        if self.bot:
            try:
                self.bot.close()
            except:
                pass
        self.destroy()

    def start_thread(self):
        """啟動自動化執行緒"""
        api_key = self.entry_api.get().strip()
        contest_url = self.entry_url.get().strip()
        username = self.entry_user.get().strip()
        password = self.entry_pass.get().strip()

        if not all([api_key, contest_url, username, password]):
            self.log("⚠️ 請填寫所有必要欄位")
            self.set_status("欄位未完整", self.COLOR_WARNING)
            return

        self.btn_start.configure(state="disabled", text="⏳  執行中...")
        self.set_status("執行中", self.COLOR_WARNING)
        
        thread = threading.Thread(target=self.run_automation, args=(api_key, contest_url, username, password))
        thread.daemon = True
        thread.start()

    def run_automation(self, api_key, contest_url, username, password):
        """自動化流程主函式"""
        try:
            self.log("🌐 啟動瀏覽器...")
            self.bot = OJBot(headless=False)
            
            self.log(f"🔗 連線至: {contest_url}")
            success, msg = self.bot.login(contest_url, username, password)
            
            if success:
                self.log("✅ 登入成功")
            else:
                self.log(f"❌ 登入失敗: {msg}")
                time.sleep(10)

            if self.bot.driver.current_url != contest_url:
                self.bot.driver.get(contest_url)
                time.sleep(2)

            if not self.bot.check_contest_active():
                self.log("⚠️ 未偵測到計時器")
            
            questions = self.bot.get_unsolved_questions()
            
            if not questions:
                self.log("🎉 所有題目已完成！")
            else:
                self.log(f"📝 待處理: {len(questions)} 題")
                self.log("─" * 30)
                
                total = len(questions)
                for i, q_url in enumerate(questions):
                    q_id = q_url.split('/')[-2]
                    self.log(f"[{i+1}/{total}] 處理題目 ID: {q_id}")
                    
                    # 傳遞 AI 設定
                    provider = self.provider_var.get()
                    model = self.model_var.get()
                    endpoint = self.entry_endpoint.get().strip() if provider == "custom" else None
                    
                    result = self.bot.process_question(
                        q_url, 
                        solve_challenge, 
                        api_key,
                        provider=provider,
                        model_name=model,
                        custom_endpoint=endpoint
                    )
                    
                    if result["status"] == "Success":
                        self.log(f"   ✅ AC - 通過！")
                    else:
                        self.log(f"   ❌ {result['msg'][:30]}...") 
                    
                    time.sleep(3) 

            self.log("🏁 任務結束")
            self.set_status("完成", self.COLOR_SUCCESS)
            try:
                self.bot.refresh_page()
            except:
                pass

        except Exception as e:
            self.log(f"❌ 錯誤: {e}")
            self.set_status("錯誤", "#F44336")
        finally:
            self.btn_start.configure(state="normal", text="🚀  開始任務")

if __name__ == "__main__":
    force_cleanup()
    app = OJHelprApp()
    app.mainloop()