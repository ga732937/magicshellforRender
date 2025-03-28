from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import Config
from login_manager import LoginManager
from web_scraper_1 import WebScraper1
from web_scraper_2 import WebScraper2
from web_scraper_3 import WebScraper3
from panel_expander import PanelExpander
from data_processor import DataCleaner
from data_processor import DataMerger
from google_sheets_uploader import GoogleSheetsUploader
import time
import os
import pandas as pd
from utils import wait_for_file, log_message
from SheetManager import GoogleSheetsManager
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from excel_saver import ExcelSaver


class MainProcess:
    """
    主程式，負責執行完整流程：
    1. 初始化 WebDriver
    2. 登入網站
    3. 抓取數據
    4. 清理與處理數據
    5. 上傳數據至 Google Sheets
    """

    def __init__(self, progress_callback=None):
        """
        初始化 WebDriver

        Args:
            progress_callback: 進度回報的回調函數，格式為 callback(progress, message)
                               progress 為 0-100 的整數，message 為進度訊息
        """
        self.progress_callback = progress_callback or (lambda progress, message: None)

        # 建立必要的目錄
        os.makedirs("data", exist_ok=True)
        os.makedirs("logs", exist_ok=True)

        # 回報進度：初始化
        self.report_progress(5, "正在初始化 WebDriver...")

        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        options.add_argument("--headless=new")  # 在 Render 上必須使用無頭模式
        options.add_argument("--disable-gpu")  # 避免 GPU 相關問題
        options.add_argument("--no-sandbox")  # 避免 sandbox 問題
        options.add_argument("--disable-dev-shm-usage")  # 限制共享內存使用
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        options.add_experimental_option(
            "prefs", {"credentials_enable_service": False}
        )  # 禁用密碼儲存
        options.add_argument("--disable-notifications")  # 禁用通知
        options.add_experimental_option(
            "excludeSwitches", ["enable-automation"]
        )  # 移除自動化軟體提示
        options.add_argument("--blink-settings=imagesEnabled=false")
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        # self.driver = webdriver.Chrome(options=options)

        # 初始化所有模組
        self.login_manager = LoginManager(self.driver)
        self.scraper1 = WebScraper1(self.driver)
        self.scraper2 = WebScraper2(self.driver)
        self.scraper3 = WebScraper3(self.driver)
        self.panel_expander = PanelExpander(self.driver)
        # 初始化 Google Sheets 上傳工具
        self.uploader = GoogleSheetsUploader(
            Config.JSON_API, Config.SHEET_ID, Config.WORKSHEET_NAME
        )
        # 初始化 ExcelSaver
        self.saver = ExcelSaver()

        # 回報進度：初始化完成
        self.report_progress(10, "初始化完成，準備開始爬蟲...")

    def report_progress(self, progress, message):
        """回報進度"""
        if self.progress_callback:
            self.progress_callback(progress, message)
        log_message(message)

    def run(self):
        """執行完整的數據處理流程"""
        try:
            self.report_progress(10, "🚀 開始執行數據處理流程...")

            # 登入網站
            self.report_progress(15, "正在登入網站...")
            self.login_manager.login(Config.LOGIN_URL, Config.USERNAME, Config.PASSWORD)
            self.report_progress(20, "登入成功！")

            # 前往待處理訂單頁面
            self.report_progress(25, "正在前往待處理訂單頁面...")
            self.driver.get(Config.WAIT_ORDER_URL)
            time.sleep(5)

            # 抓取訂單數據
            self.report_progress(30, "正在抓取訂單數據...")
            head_data = self.scraper1.fetch_table_data()
            self.report_progress(35, "訂單數據抓取完成！")

            # 展開所有第三個摺疊面板
            self.report_progress(40, "正在展開訂單詳細資訊...")
            self.panel_expander.expand_third_panels_js()
            time.sleep(3)
            self.report_progress(45, "訂單詳細資訊展開完成！")

            # 抓取展開後原始數據
            self.report_progress(50, "正在抓取展開後的原始數據...")
            self.scraper2.fetch_table_data()
            self.report_progress(55, "原始數據抓取完成！")

            # 抓取展開折疊面板數據
            self.report_progress(60, "正在抓取折疊面板數據...")
            inner_data = self.scraper3.fetch_table_data()
            self.report_progress(65, "折疊面板數據抓取完成！")

            # 數據清理
            self.report_progress(70, "正在清理數據...")
            cleaner1 = DataCleaner(head_data)
            cleaned_df1 = cleaner1.clean(
                columns_to_drop=[
                    "Copy",
                    "Token",
                    "訂單狀態",
                    "編輯備註",
                    "編輯者",
                    "訂單物品已處理/總數",
                    "物流公司",
                    "操作",
                ],
                index_to_drop=[0],
            )
            cleaned1_path, _ = self.saver.save(
                cleaned_df1, filename_prefix="cleaned_data1"
            )

            cleaner2 = DataCleaner(inner_data)
            cleaned_df2 = cleaner2.clean(
                columns_to_drop=["商品圖片", "商品成本", "品項編號"],
                index_to_drop=[0, 1],
            )
            cleaned2_path, _ = self.saver.save(
                cleaned_df2, filename_prefix="cleaned_data2"
            )
            self.report_progress(75, "數據清理完成！")

            # 數據合併
            self.report_progress(80, "正在合併數據...")
            merger = DataMerger(cleaned1_path, cleaned2_path)
            df_final = merger.process_all()

            if not isinstance(df_final, pd.DataFrame):
                raise TypeError("❌ df_final 不是 DataFrame，可能發生變數覆蓋")

            # 儲存合併後的數據
            final_path, _ = self.saver.save(
                df_final, filename_prefix="final_processed_data"
            )
            self.report_progress(85, "數據合併與處理完成！")

            # 上傳數據到 Google Sheets
            self.report_progress(90, "正在上傳數據到 Google Sheets...")
            self.uploader.upload_to_sheets(df_final)
            self.report_progress(100, "✅ 整個流程執行完畢！")

            return {
                "status": "success",
                "message": "Python script executed successfully!",
            }

        except Exception as e:
            error_message = f"❌ 程式執行失敗: {e}"
            self.report_progress(0, error_message)
            return {"status": "error", "message": error_message}

        finally:
            self.driver.quit()


# 供 Flask 呼叫的主函式
def main_process(progress_callback=None):
    """
    供 Flask 呼叫的主函式

    Args:
        progress_callback: 進度回報的回調函數，格式為 callback(progress, message)
                           progress 為 0-100 的整數，message 為進度訊息

    Returns:
        dict: 執行結果，包含 status 和 message
    """
    try:
        process = MainProcess(progress_callback)  # 初始化主流程，傳入進度回調函數
        result = process.run()  # 執行爬蟲邏輯
        return result  # 返回結果（成功或失敗訊息）
    except Exception as e:
        return {"status": "error", "message": str(e)}


# 只有當手動執行時，才會運行
if __name__ == "__main__":
    result = main_process()
    print(result)
