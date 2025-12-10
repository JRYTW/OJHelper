import google.generativeai as genai
import time
from google.api_core import exceptions
import openai
from anthropic import Anthropic
import requests

def solve_challenge(api_key, problem_text, language="Java", provider="gemini", model_name=None, custom_endpoint=None):
    """
    接收 API Key 與題目文字，回傳程式碼解答。
    支援多種 AI 提供商：gemini, chatgpt, claude, custom
    
    Args:
        api_key: API 金鑰
        problem_text: 題目文字
        language: 程式語言 (預設 Java)
        provider: AI 提供商 ('gemini', 'chatgpt', 'claude', 'custom')
        model_name: 模型名稱 (可選)
        custom_endpoint: 自訂 API 端點 (僅 provider='custom' 時使用)
    """
    if not api_key:
        return False, "錯誤：未提供 API Key"

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
        if provider == "gemini":
            return _solve_with_gemini(api_key, prompt, model_name)
        elif provider == "chatgpt":
            return _solve_with_openai(api_key, prompt, model_name)
        elif provider == "claude":
            return _solve_with_claude(api_key, prompt, model_name)
        elif provider == "custom":
            return _solve_with_custom(api_key, prompt, custom_endpoint, model_name)
        else:
            return False, f"不支援的提供商: {provider}"
            
    except Exception as e:
        return False, f"AI Error: {str(e)}"


def _solve_with_gemini(api_key, prompt, model_name=None):
    """使用 Google Gemini API"""
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name or 'gemini-2.5-flash-lite')
        response = model.generate_content(prompt)
        clean_code = response.text.replace("```java", "").replace("```", "").strip()
        return True, clean_code
    except Exception as e:
        return False, f"Gemini Error: {str(e)}"


def _solve_with_openai(api_key, prompt, model_name=None):
    """使用 OpenAI ChatGPT API"""
    try:
        openai.api_key = api_key
        response = openai.chat.completions.create(
            model=model_name or "gpt-4o-mini",
            messages=[
                {"role": "system", "content": "你是程式競賽專家，只輸出程式碼，不包含任何解釋或 Markdown。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        clean_code = response.choices[0].message.content.replace("```java", "").replace("```", "").strip()
        return True, clean_code
    except Exception as e:
        return False, f"OpenAI Error: {str(e)}"


def _solve_with_claude(api_key, prompt, model_name=None):
    """使用 Anthropic Claude API"""
    try:
        client = Anthropic(api_key=api_key)
        message = client.messages.create(
            model=model_name or "claude-3-5-sonnet-20241022",
            max_tokens=4096,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        clean_code = message.content[0].text.replace("```java", "").replace("```", "").strip()
        return True, clean_code
    except Exception as e:
        return False, f"Claude Error: {str(e)}"


def _solve_with_custom(api_key, prompt, endpoint, model_name=None):
    """使用自訂 API 端點（OpenAI 相容格式）"""
    try:
        if not endpoint:
            return False, "錯誤：未提供自訂端點"
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model_name or "default",
            "messages": [
                {"role": "system", "content": "你是程式競賽專家，只輸出程式碼。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3
        }
        
        response = requests.post(endpoint, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        clean_code = result["choices"][0]["message"]["content"].replace("```java", "").replace("```", "").strip()
        return True, clean_code
        
    except Exception as e:
        return False, f"Custom API Error: {str(e)}"
    