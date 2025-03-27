from web_scraper import WebScraper
import pandas as pd

class WebScraper2(WebScraper):
    """
    獲取完整表格數據
    """
    def fetch_table_data(self):
        #print("📌 獲取完整表格結構的表格數據中...")

        # 先確認表格完全載入
        self.wait_for_table() 
        
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

        df = pd.DataFrame(table_data)
        
        # ✅ 使用 `save_to_excel()`（共用 `ExcelSaver`）
        return self.save_to_excel(df, prefix="raw_data")
