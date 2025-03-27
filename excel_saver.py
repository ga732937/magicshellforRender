import os
import time
import pandas as pd
from datetime import datetime

class ExcelSaver:
    """
    統一處理Excel檔案儲存的類別
    """
    def __init__(self):
        """初始化Excel儲存器"""
        self.data_dir = "data"  # 資料存放目錄
        
        # 確保資料目錄存在
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def save(self, df, filename_prefix="data"):
        """
        儲存DataFrame到Excel檔案
        :param df: pandas.DataFrame - 要儲存的數據
        :param filename_prefix: str - 檔案名稱前綴
        :return: tuple - (檔案路徑, 是否成功)
        """
        if not isinstance(df, pd.DataFrame):
            raise ValueError("❌ 儲存失敗，df 不是 DataFrame")
            
        # 建立檔案名稱，格式: prefix_YYYYMMDD_HHMMSS.xlsx
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{filename_prefix}_{timestamp}.xlsx"
        filepath = os.path.join(self.data_dir, filename)
        
        try:
            # 儲存到Excel
            df.to_excel(filepath, index=False)
            
            # 確認檔案已成功寫入
            self._wait_for_file_write(filepath)
            
            #print(f"✅ 已成功儲存到: {filepath}")
            return filepath, True
        except Exception as e:
            print(f"❌ 儲存失敗: {e}")
            return None, False
    
    def _wait_for_file_write(self, filepath, timeout=10):
        """
        等待檔案寫入完成
        :param filepath: str - 檔案路徑
        :param timeout: int - 超時秒數
        :return: bool - 是否成功
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                # 嘗試開啟檔案進行讀取
                with open(filepath, 'rb') as f:
                    f.read(1)
                return True
            except (IOError, PermissionError):
                # 檔案可能正在寫入，等待一段時間
                time.sleep(0.5)
        return False