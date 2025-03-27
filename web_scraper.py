# 基礎類別 父類別
import os
import time
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
from excel_saver import ExcelSaver  # ✅ **導入 ExcelSaver**


class WebScraper:
    """
    WebScraper 基礎類別，定義通用的方法：
    - 抓取數據 (由子類別覆寫)
    - 儲存數據
    - 儲存數據（統一使用 ExcelSaver）
    - 等待表格載入完成
    """
    def __init__(self, driver):
        self.driver = driver
        self.saver = ExcelSaver()  # ✅ **統一使用 ExcelSaver**


    def fetch_table_data(self):
        """
        這個方法應該由子類別覆寫，根據不同的 HTML 結構抓取數據
        """
        raise NotImplementedError("請在子類別中實作 fetch_table_data 方法")

    def save_to_excel(self, df, prefix="data"):
        """
        統一使用 `ExcelSaver` 來儲存 Excel 檔案
        """
        return self.saver.save(df, filename_prefix=prefix)    

    def wait_for_table(self, timeout=10):
        """
        等待網頁中的表格完全加載
        """
        #print("⌛ 等待網頁表格加載...")
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, "table"))
            )
            #print("✅ 表格加載完成！")
        except:
            print("❌ 表格加載超時！")

