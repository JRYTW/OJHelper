import customtkinter as ctk
import threading
import time
import os
from browser_bot import OJBot
from ai_engine import solve_challenge

# 清理殘留驅動
def force_cleanup():
    try:
        os.system("taskkill /f /im chromedriver.exe >nul 2>&1")
    except Exception:
        pass

class OJHelprApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        ctk.set_appearance_mode("Light")
        
        # 設定視窗大小 450x800
        self.geometry("450x800")
        self.title("OJHelpr")
        self.resizable(False, True)

        # 定義配色
        self.COLOR_BG = "#FAFAFA"        # 背景
        self.COLOR_ACCENT = "#607D8B"    # 按鈕/標題
        self.COLOR_ACCENT_HOVER = "#455A64" # 深藍灰
        self.COLOR_TEXT = "#37474F"      # 深灰文字
        self.COLOR_INPUT_BG = "#ECEFF1"  # 輸入框背景
        self.COLOR_LOG_BG = "#F5F5F5"    # 日誌區背景
        
        # 字體設定
        self.FONT_TITLE = ("Microsoft JhengHei UI", 26, "bold")
        self.FONT_LABEL = ("Microsoft JhengHei UI", 13)
        self.FONT_INPUT = ("Arial", 14)
        self.FONT_LOG = ("Consolas", 12)

        self.configure(fg_color=self.COLOR_BG)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # ============================
        # 1. Header (頂部標題)
        # ============================
        self.frame_header = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_header.grid(row=0, column=0, pady=(40, 20), sticky="ew")
        
        # 線條
        self.bar = ctk.CTkFrame(self.frame_header, width=50, height=5, fg_color=self.COLOR_ACCENT, corner_radius=10)
        self.bar.pack(pady=(0, 15))

        self.lbl_title = ctk.CTkLabel(
            self.frame_header, 
            text="OJHelpr", 
            font=self.FONT_TITLE, 
            text_color=self.COLOR_ACCENT
        )
        self.lbl_title.pack()

        self.lbl_subtitle = ctk.CTkLabel(
            self.frame_header, 
            text="V1.0 Made By JRYTW", 
            font=("Arial", 12), 
            text_color="#999999"
        )
        self.lbl_subtitle.pack()

        # ============================
        # 2. Input Area (表單區)
        # ============================
        self.frame_form = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_form.grid(row=1, column=0, padx=35, pady=10, sticky="ew")
        self.frame_form.grid_columnconfigure(0, weight=1)

        # 封裝輸入框函式
        def create_input(parent, label_text, placeholder, is_password=False):
            # 標籤
            lbl = ctk.CTkLabel(parent, text=label_text, font=self.FONT_LABEL, text_color=self.COLOR_TEXT, anchor="w")
            lbl.pack(fill="x", pady=(12, 4))
            
            # 輸入框
            entry = ctk.CTkEntry(
                parent, 
                placeholder_text=placeholder,
                font=self.FONT_INPUT,
                fg_color=self.COLOR_INPUT_BG,
                border_color=self.COLOR_INPUT_BG,
                text_color=self.COLOR_TEXT,
                height=42,
                corner_radius=10,
                show="●" if is_password else ""
            )
            entry.pack(fill="x")
            return entry

        # 輸入框欄位
        self.entry_api = create_input(self.frame_form, "API KEY", "貼上 Gemini API Key", is_password=True)
        self.entry_url = create_input(self.frame_form, "CONTEST URL", "https://example.com/contest/123")
        self.entry_user = create_input(self.frame_form, "USERNAME", "使用者帳號")
        self.entry_pass = create_input(self.frame_form, "PASSWORD", "使用者密碼", is_password=True)

        # ============================
        # 3. Action Button (啟動)
        # ============================
        self.btn_start = ctk.CTkButton(
            self, 
            text="開始任務", 
            command=self.start_thread, 
            height=55, 
            corner_radius=15,
            font=("Microsoft JhengHei UI", 16, "bold"),
            fg_color=self.COLOR_ACCENT,
            hover_color=self.COLOR_ACCENT_HOVER,
            text_color="white"
        )
        self.btn_start.grid(row=2, column=0, padx=35, pady=35, sticky="ew")

        # ============================
        # 4. Log Area (底部終端)
        # ============================
        self.frame_log = ctk.CTkFrame(self, fg_color=self.COLOR_LOG_BG, corner_radius=15)
        self.frame_log.grid(row=3, column=0, padx=20, pady=(0, 20), sticky="nsew")
        
        self.frame_log.grid_rowconfigure(0, weight=1)
        self.frame_log.grid_columnconfigure(0, weight=1)

        self.textbox_log = ctk.CTkTextbox(
            self.frame_log, 
            font=self.FONT_LOG,
            fg_color="transparent",
            text_color="#000000",
            scrollbar_button_color="#CFD8DC",
            scrollbar_button_hover_color="#B0BEC5"
        )
        self.textbox_log.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        self.log("系統準備就緒...")
        self.bot = None

    def log(self, msg):
        timestamp = time.strftime('%H:%M') 
        self.textbox_log.insert("end", f"{timestamp} . {msg}\n")
        self.textbox_log.see("end")

    def on_closing(self):
        if self.bot:
            try:
                self.bot.close()
            except:
                pass
        self.destroy()

    def start_thread(self):
        api_key = self.entry_api.get().strip()
        contest_url = self.entry_url.get().strip()
        username = self.entry_user.get().strip()
        password = self.entry_pass.get().strip()

        if not all([api_key, contest_url, username, password]):
            self.log("提示：請填寫所有欄位")
            return

        self.btn_start.configure(state="disabled", text="執行中...")
        
        thread = threading.Thread(target=self.run_automation, args=(api_key, contest_url, username, password))
        thread.daemon = True
        thread.start()

    def run_automation(self, api_key, contest_url, username, password):
        try:
            self.log("啟動瀏覽器...")
            self.bot = OJBot(headless=False)
            
            self.log(f"連線至: {contest_url}")
            success, msg = self.bot.login(contest_url, username, password)
            
            if success:
                self.log(f"✔ 登入成功")
            else:
                self.log(f"✘ 登入失敗: {msg}")
                time.sleep(10)

            if self.bot.driver.current_url != contest_url:
                self.bot.driver.get(contest_url)
                time.sleep(2)

            if not self.bot.check_contest_active():
                self.log("！ 未偵測到計時器")
            
            questions = self.bot.get_unsolved_questions()
            
            if not questions:
                self.log("★ 無未完成題目")
            else:
                self.log(f"待處理: {len(questions)} 題")
                self.log("─" * 25)
                
                total = len(questions)
                for i, q_url in enumerate(questions):
                    q_id = q_url.split('/')[-2]
                    self.log(f"[{i+1}/{total}] ID: {q_id}")
                    
                    result = self.bot.process_question(q_url, solve_challenge, api_key)
                    
                    if result["status"] == "Success":
                        self.log(f"  ✔ AC")
                    else:
                        self.log(f"  ✘ {result['msg'][:15]}...") 
                    
                    time.sleep(3) 

            self.log("任務結束")
            try:
                self.bot.refresh_page()
            except:
                pass

        except Exception as e:
            self.log(f"錯誤: {e}")
        finally:
            self.btn_start.configure(state="normal", text="開始任務")

if __name__ == "__main__":
    force_cleanup()
    app = OJHelprApp()
    app.mainloop()
