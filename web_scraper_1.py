from web_scraper import WebScraper
import pandas as pd

class WebScraper1(WebScraper):
    """
    抓取未展開表格數據
    """
    def fetch_table_data(self):
        #print("📌 獲取未展開表格數據中...")
        
        # ✅ **JavaScript 爬取表格數據**
        table_data = self.driver.execute_script("""
            let rows = document.querySelectorAll('table tr');
            let data = [];
            rows.forEach(row => {
                let cells = row.querySelectorAll('th, td');
                let rowData = [];
                cells.forEach(cell => rowData.push(cell.innerText.trim()));
                if (rowData.length > 0) data.push(rowData);
            });
            return data;
        """)

        # ✅ 轉換為 DataFrame
        df = pd.DataFrame(table_data)
        df.columns = ["Copy", "訂單ID", "最終售價", "收件資料", "收件人電話", "會員資料", "Token", "訂單狀態", "運送狀態","編輯備註","備註", "編輯者", "套組資訊", "店家", "訂單物品已處理/總數","物流公司" , "領取方式", "物品數量","建立時間", "更新時間", "操作"]

       # ✅ 使用 `save_to_excel()`（共用 `ExcelSaver`）
        self.save_to_excel(df, prefix="head_data")

        return df
           
       
