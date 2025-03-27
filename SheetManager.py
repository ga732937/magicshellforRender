import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import os

class GoogleSheetsManager:
    """
    Google Sheets 管理工具，提供讀寫功能
    """
    def __init__(self, json_api, sheet_id):
        """
        初始化 Google Sheets 連線
        :param json_api: str - Google API 憑證 JSON 路徑
        :param sheet_id: str - Google 試算表 ID
        """
        self.json_api = json_api
        self.sheet_id = sheet_id
        self.client = None
        self.sheet = None
        
    def authenticate(self):
        """驗證 Google Sheets API 並連線"""
        try:
            if not os.path.exists(self.json_api):
                raise FileNotFoundError(f"❌ Google API 憑證不存在: {self.json_api}")
                
            creds = Credentials.from_service_account_file(
                self.json_api, 
                scopes=["https://www.googleapis.com/auth/spreadsheets"]
            )
            self.client = gspread.authorize(creds)
            return True
        except Exception as e:
            print(f"❌ Google Sheets 連線失敗: {e}")
            return False
            
    def open_worksheet(self, worksheet_name):
        """
        開啟指定的工作表
        :param worksheet_name: str - 工作表名稱
        :return: gspread.Worksheet - 工作表物件
        """
        if not self.client:
            self.authenticate()
            
        try:
            self.sheet = self.client.open_by_key(self.sheet_id).worksheet(worksheet_name)
            return self.sheet
        except Exception as e:
            print(f"❌ 開啟工作表失敗: {e}")
            return None
            
    def read_to_dataframe(self, worksheet_name):
        """
        讀取工作表內容到 DataFrame
        :param worksheet_name: str - 工作表名稱
        :return: pd.DataFrame - 工作表數據
        """
        sheet = self.open_worksheet(worksheet_name)
        if not sheet:
            return None
            
        try:
            data = sheet.get_all_records()
            df = pd.DataFrame(data)
            return df
        except Exception as e:
            print(f"❌ 讀取數據失敗: {e}")
            return None
            
    def update_sheet(self, worksheet_name, df):
        """
        更新工作表內容
        :param worksheet_name: str - 工作表名稱
        :param df: pd.DataFrame - 要更新的數據
        :return: bool - 是否成功
        """
        sheet = self.open_worksheet(worksheet_name)
        if not sheet:
            return False
            
        try:
            # 清除現有數據
            sheet.clear()
            
            # 寫入標題行
            sheet.append_row(df.columns.tolist())
            
            # 寫入數據行
            for _, row in df.iterrows():
                sheet.append_row(row.tolist())
                
            return True
        except Exception as e:
            print(f"❌ 更新工作表失敗: {e}")
            return False