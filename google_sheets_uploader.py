import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
import os

class GoogleSheetsUploader:
    """
    負責將處理後的數據上傳到 Google Sheets
    """
    def __init__(self, json_api, sheet_id, worksheet_name):
        """
        初始化 Google Sheets 連線
        :param json_api: str - Google API 憑證 JSON 路徑
        :param sheet_id: str - Google 試算表 ID
        :param worksheet_name: str - 要上傳的工作表名稱
        """
        self.json_api = json_api
        self.sheet_id = sheet_id
        self.worksheet_name = worksheet_name
        self.client = None
        self.sheet = None

    def authenticate(self):
        """ 驗證 Google Sheets API 並連線 """
        try:
            if not os.path.exists(self.json_api):
                raise FileNotFoundError(f"❌ Google API 憑證不存在: {self.json_api}")

            creds = Credentials.from_service_account_file(self.json_api, scopes=["https://www.googleapis.com/auth/spreadsheets"])
            self.client = gspread.authorize(creds)
            self.sheet = self.client.open_by_key(self.sheet_id).worksheet(self.worksheet_name)
            print("✅ 成功連線至 Google Sheets")
        except Exception as e:
            print(f"❌ Google Sheets 連線失敗: {e}")
            self.sheet = None  # 確保不會執行後續程式    

    def upload_to_sheets(self, df):
        """
        將 DataFrame 上傳到 Google Sheets
        :param df: pd.DataFrame - 要上傳的數據
        """

        if not isinstance(df, pd.DataFrame):
            raise ValueError("❌ 上傳失敗，df 不是 DataFrame")

        if df.empty:
            print("❌ 沒有數據可上傳")
            return

        try:
            self.authenticate()  # 確保 API 連線
            df = df.fillna("")  # ✅ 避免 NaN 值導致上傳錯誤
            values = [df.columns.tolist()] + df.values.tolist()  # ✅ 加入標題列

            """
            # **取得 Google Sheets 現有數據範圍**            
            # ✅ 如果 Google Sheets 是空的，則寫入標題列
            # ✅ 如果 Google Sheets 有數據，則從下一行開始追加數據            
            if  len(self.sheet.get_all_values()) == 0:
                 
                print("✅ 數據成功上傳至 Google Sheets")
            else:
                start_row = len(self.sheet.get_all_values()) + 1  # **從最後一行開始追加**
                cell_range = f"A{start_row}"  # **從 A 開始**
                print(f"✅ 資料成功上傳至 Google Sheets，從 {cell_range} 開始")
                # **使用 batch_update 上傳**
                self.sheet.update(cell_range, values)
            """
            

            # **如果需要清除 Google Sheets 數據，請取消註解以下程式碼**
            self.sheet.clear()  # **清除 Google Sheets 內所有數據**
            self.sheet.append_row(df.columns.tolist())  # **重新寫入標題**
            self.sheet.update("A2", df.values.tolist())  # **從 A2 開始寫入數據**
            
            print("✅ 資料成功上傳至 Google Sheets")
        except Exception as e:
            print(f"❌ 上傳失敗: {e}")

    def delete_first_row(self):
        """
        刪除 Google Sheets 第一行
        """
        self.authenticate()
        if self.sheet is None:
            print("❌ 無法執行刪除，Google Sheets 連線失敗")
            return

        try:
            self.sheet.delete_rows(1)  # 刪除第一行
            print("✅ 成功刪除 Google Sheets 第一行")
        except Exception as e:
            print(f"❌ 刪除第一行失敗: {e}")