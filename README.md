# OJHelper - 校內 OJ 平台自動解題輔助工具

這是一個基於 Python 的 AI 自動化解題輔助程式，專為校內 OJ 平台設計。該工具使用 Selenium 網頁自動化技術與 AI 的能力，透過 CustomTkinter 製作出現代化的簡約 GUI 介面，實現從讀題、解題到提交的全自動化流程。

-----

## 功能簡介

### 🌟 功能亮點

1.  **簡約 GUI 介面** 採用 9:16 手機比例設計，搭配柔和的色系與圓角佈局，提供直觀且舒適的操作體驗。

2.  **自選 AI 模型（Gemini、ChatGPT、Claude、Custom）** 可自訂任何相容 OpenAI 格式的 API 端點。

2.  **AI 智慧解題** 調用 AI 模型，自動讀取題目敘述並生成符合規範的回應。

3.  **全自動化互動流程**
      - **自動登入**：自動處理 Modal 彈窗登入。
      - **智慧填答**：透過 JavaScript 注入技術 (JS Injection) 實現直接輸入。
      - **強制提交**：使用 JS 強制觸發點擊，無視頁面遮擋物。

5.  **防呆與容錯機制**
      - 支援「斷點續傳」，略過已 Expired 的題組。
      - 支援「斷點續傳」，略過已 Accepted 的題目。
      - 啟動時自動清理殘留的瀏覽器驅動程序。

-----

## 使用技術

  - **Python 3.13+** (建議版本)
  - **Selenium 4.x** 用於驅動 Chrome 瀏覽器，執行 DOM 操作與 JS 注入。
  - **Google Generative AI (Gemini SDK)** 用於理解程式題目並生成解答。
  - **CustomTkinter** 基於 Tkinter 的現代化 UI 庫，實現簡約介面。
  - **PyInstaller** 用於將 Python 腳本打包為獨立 EXE 執行檔。

-----

##  技術細節

### API 整合架構

```
main.py (UI)
    ↓
browser_bot.py (爬蟲邏輯)
    ↓
ai_engine.py (AI 呼叫)
    ↓
[Gemini | ChatGPT | Claude | Custom API]
```

### ai_engine.py 函式簽章

```python
def solve_challenge(
    api_key: str,
    problem_text: str,
    language: str = "Java",
    provider: str = "gemini",
    model_name: str = None,
    custom_endpoint: str = None
) -> Tuple[bool, str]
```

**參數說明**：
- `api_key`: API 金鑰
- `problem_text`: 題目描述文字
- `language`: 程式語言（預設 Java）
- `provider`: AI 提供商（`gemini` | `chatgpt` | `claude` | `custom`）
- `model_name`: 模型名稱（可選，使用預設值若未提供）
- `custom_endpoint`: 自訂 API 端點（僅 `provider="custom"` 時需要）

**回傳值**：
- `(True, code_string)`: 成功，回傳生成的程式碼
- `(False, error_message)`: 失敗，回傳錯誤訊息

-----

## 自訂 API 端點範例

### LocalAI（本地部署）
```
端點: http://localhost:8080/v1/chat/completions
模型: gpt-3.5-turbo (或您部署的模型名稱)
API Key: 可留空或填入本地設定的 token
```

### Ollama（透過 OpenAI 相容層）
```
端點: http://localhost:11434/v1/chat/completions
模型: llama2 (或您下載的模型)
API Key: 可留空
```

-----

## 安裝與配置 (開發者模式)

如果您是直接使用打包好的 `.exe` 檔，請跳過此步驟直接看「使用方法」。若您要執行原始碼，請參考以下步驟：

### 1\. 安裝依賴

確保您已安裝 Python 3.13，然後使用以下命令安裝必要的依賴庫：

```bash
pip install customtkinter selenium google-generativeai packaging
```

### 2\. 配置環境

  - **API Key 準備** 前往 [Google AI Studio](https://aistudio.google.com/) 免費獲取 Gemini API Key。
  - **瀏覽器驅動** 本程式使用 Selenium 4.x，會自動管理 ChromeDriver，**無需手動下載**。

### 3\. 打包成執行檔 (可選)

若要製作可直接使用的 `.exe` 檔，請執行：

```bash
pyinstaller --noconfirm --onefile --windowed --name "OJHelpr" --collect-all customtkinter main.py
```

-----

## 使用方法

### 啟動程式

#### 方式 A：執行 EXE (推薦)

直接雙擊 `OJHelpr.exe` 即可啟動。

#### 方式 B：執行原始碼

在終端機中執行：

```bash
python main.py
```

### 操作步驟

1.  **填寫參數**：
    在 GUI 介面上依序填入：

      - **AI PROVIDER**：選擇您的 AI 模型提供商。
      - **AI MODEL**：選擇您想使用的 AI 模型。
      - **API KEY**：您的 AI API Key (例如 [Google AI Studio](https://aistudio.google.com/))。
      - **CONTEST URL**：目標題組網址 (例如 `https://.../contest/227/`)。
      - **USERNAME / PASSWORD**：您的 OJ 登入帳號與密碼。

2.  **開始任務**：
    點擊底部的 **「開始任務」** 按鈕。

3.  **自動化執行**：

      - 程式將自動開啟瀏覽器並登入。
      - 掃描該題組內所有「未提交」的題目。
      - 逐題進行 AI 解題與提交。
      - 結果將即時顯示於下方的日誌區 (Log Area)。

-----

## 注意事項

  - **學術誠信聲明**：本工具僅供程式自動化教學使用，**請勿用於正式考試作弊或惡意刷題**。
  - **API 頻率限制**：使用免費版 Gemini API 可能會遇到速率限制 (Rate Limit)，請詳閱 Gemini 2.5 Flash 模型規則。
  - **瀏覽器操作**：程式執行過程中，請勿手動關閉或操作跳出來的 Chrome 視窗，以免流程中斷。
  - **環境要求**：建議使用 **Python 3.13** 版本以確保 CustomTkinter 與 Selenium 的最佳相容性。
  - **實測環境**：本程式針對特定的 LetsOJ 平台架構 (程式版本:v0.5 版本日期:2025/11/26) 設計，若 HTML 結構變更可能導致功能失效。

-----

有任何問題或建議，請隨時聯繫我！ 🚀
