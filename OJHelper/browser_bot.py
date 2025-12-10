from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class OJBot:
    def __init__(self, headless=False):
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument("--headless")
        
        options.add_argument('--ignore-certificate-errors')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 20)

    def login(self, login_url, username, password):
        """ 自動登入邏輯 """
        try:
            self.driver.get(login_url)
            
            # 等待 Modal 出現
            user_field = self.wait.until(EC.visibility_of_element_located((By.ID, "username")))
            
            user_field.clear()
            user_field.send_keys(username)
            
            pass_field = self.driver.find_element(By.ID, "password")
            pass_field.clear()
            pass_field.send_keys(password)
            
            # 使用 JS 點擊登入按鈕
            submit_btn = self.driver.find_element(By.CSS_SELECTOR, "#modalForm button[type='submit']")
            self.driver.execute_script("arguments[0].click();", submit_btn)
            
            time.sleep(2)
            return True, "登入動作已執行"

        except Exception as e:
            return False, f"登入失敗: {str(e)}"

    def check_contest_active(self):
        try:
            self.wait.until(EC.presence_of_element_located((By.ID, "countDownTimer")))
            timer_elem = self.driver.find_element(By.ID, "countDownTimer")
            if "EXPIRED" in timer_elem.text:
                return False
            return True
        except:
            return False

    def get_unsolved_questions(self):
        links = []
        try:
            # 選取有 striped 但沒有 small 屬性的表格 (題目列表)
            target_table_selector = "table.table-striped:not(.table-sm) tbody tr"
            
            # 等待表格出現
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table.table-striped")))
            
            rows = self.driver.find_elements(By.CSS_SELECTOR, target_table_selector)
            
            for row in rows:
                try:
                    cols = row.find_elements(By.TAG_NAME, "td")
                    if len(cols) < 4: continue 

                    # 題目連結在第 2 欄 (index 1)
                    link_elem = cols[1].find_element(By.TAG_NAME, "a")

                    # 抓沒有 "Accepted"
                    status_text = cols[3].text.strip()
                    
                    # 只要狀態文字中不包含 "Accepted"，就加入待解清單
                    if "Accepted" not in status_text: 
                        links.append(link_elem.get_attribute("href"))
                except Exception as e:
                    print(f"略過一列無效資料: {e}")
                    continue
                    
        except Exception as e:
            print(f"解析題目列表錯誤: {e}")
            
        return links

    def process_question(self, url, ai_solver_func, api_key, provider="gemini", model_name=None, custom_endpoint=None):
        """ 
        使用 JS 強制點擊提交按鈕 + 置中捲動 
        支援多種 AI 提供商
        """
        result_log = {"url": url, "status": "Fail", "msg": ""}
        
        self.driver.execute_script(f"window.open('{url}', '_blank');")
        self.driver.switch_to.window(self.driver.window_handles[-1])
        
        try:
            # 1. 爬取題目
            desc_elem = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.form-control")))
            problem_text = desc_elem.text
            
            # 2. 呼叫 AI
            success, ai_code = ai_solver_func(
                api_key, 
                problem_text, 
                language="Java",
                provider=provider,
                model_name=model_name,
                custom_endpoint=custom_endpoint
            )
            
            if not success:
                raise Exception(f"AI 生成失敗: {ai_code}")

            # 3. 填入答案
            js_code = ai_code.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\r', '')
            time.sleep(1)
            self.driver.execute_script(f'editor.setValue("{js_code}");')
            
            # 4. 提交
            submit_btn = self.wait.until(EC.presence_of_element_located((By.ID, "submitMyCode")))
            
            # 捲動到畫面正中央
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", submit_btn)
            time.sleep(1) 
            
            # JS 強制點擊
            self.driver.execute_script("arguments[0].click();", submit_btn)
            
            # 5. 等待結果
            self.wait.until(EC.visibility_of_element_located((By.ID, "mySpinner"))) 
            self.wait.until(EC.invisibility_of_element_located((By.ID, "mySpinner"))) 
            
            # 6. 讀取結果
            result_badge = self.driver.find_element(By.ID, "submission_result")
            result_text = result_badge.text
            
            output_area = self.driver.find_element(By.ID, "compile_output")
            detail_msg = output_area.get_attribute("value") 
            
            if "Accepted" in result_text:
                result_log["status"] = "Success"
                result_log["msg"] = "✅ AC (Accepted)"
                time.sleep(1)
                self.driver.close()
            else:
                result_log["status"] = "Fail"
                result_log["msg"] = f"❌ {result_text}: {detail_msg[:40]}..."
                
        except Exception as e:
            result_log["msg"] = f"Runtime Error: {str(e)}"
        
        self.driver.switch_to.window(self.driver.window_handles[0])
        return result_log

    def refresh_page(self):
        self.driver.refresh()

    def close(self):
        self.driver.quit()