import google.generativeai as genai
import time
from google.api_core import exceptions

def solve_challenge(api_key, problem_text, language="Java"):
    """
    接收 API Key 與題目文字，回傳程式碼解答。
    """
    if not api_key:
        return False, "錯誤：未提供 API Key"

    # 設定 API Key
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
    except Exception as e:
        return False, f"API 設定錯誤: {e}"

    prompt = f"""
    你是一個程式競賽專家。請閱讀以下題目，並撰寫一個正確的 {language} 解答。
    
    【嚴格規則】
    1. 僅輸出程式碼本身，不要包含 Markdown 標記 (如 ```java 或 ```)。
    2. 不要包含任何解釋、註釋或 print debug。
    3. 如果題目要求完整的 Class (如 Circle, BodyBMI)，請提供完整類別定義。
    4. 如果是一般演算法題，請提供包含 main 方法的完整 class (class 名稱請用 Main)。
    5. 程式碼必須處理標準輸入(stdin)與標準輸出(stdout)。
    
    【題目內容】
    {problem_text}
    """

    try:
        # 發送請求
        response = model.generate_content(prompt)
        
        # 清理 markdown
        clean_code = response.text.replace("```java", "").replace("```", "").strip()
        return True, clean_code
        
    except Exception as e:
        return False, f"AI Error: {str(e)}"
    