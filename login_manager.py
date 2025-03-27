from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
import time
import os

class LoginManager:
    """
    負責處理網站登入功能
    """
    def __init__(self, driver, max_retries=2):
        """
        初始化 LoginManager
        :param driver: Selenium WebDriver 物件
        :param max_retries: 最大登入嘗試次數
        """
        self.driver = driver
        self.max_retries = max_retries

    def login(self, url, username, password):
        """
        執行登入動作
        """
        print("📌 打開登入頁面")
        self.driver.get(url)
        self.driver.maximize_window()

        retries = 0
        while retries < self.max_retries:
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.NAME, "username"))
                )

                # 輸入帳號密碼並登入
                self.driver.find_element(By.NAME, "username").clear()
                self.driver.find_element(By.NAME, "username").send_keys(username)
                self.driver.find_element(By.ID, "password").clear()
                self.driver.find_element(By.ID, "password").send_keys(password)
                self.driver.find_element(By.XPATH, '//button[@type="submit"]').click()

                # 檢查是否登入成功
                if self.check_login_success():
                    print("✅ 登錄成功")
                    return True
                retries += 1
                time.sleep(2)

            except Exception as e:
                logging.error(f"❌ 登錄異常: {e}")
                retries += 1

        raise RuntimeError("❌ 登入失敗，請檢查帳號密碼或網頁狀態")

    def check_login_success(self):
        """
        確保登入成功，檢查是否進入主頁
        """
        try:
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.XPATH, '//span[contains(text(), "訂單管理")]'))
            )
            return True
        except:
            return False
