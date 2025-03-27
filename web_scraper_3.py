# 抓取展開折疊面板數據
from web_scraper import WebScraper
import pandas as pd

class WebScraper3(WebScraper):
    """
    抓取展開折疊面板的數據
    """
    def fetch_table_data(self):
        #print("📌 獲取展開折疊面板數據中...")        
        table_data = self.driver.execute_script("""
            let data = [];
            // 選擇所有展開的折疊面板內的表格
            let expandedPanels = document.querySelectorAll('div[id^="grid-collapse-"]:not([style*="display: none"]) table');
            expandedPanels.forEach(table => {
                // 抓取表格標題
                let headers = table.querySelectorAll('thead th');
                if (headers.length > 0 && data.length === 0) { // 只需要加一次標題
                    let headerRow = [];
                    headers.forEach(header => headerRow.push(header.innerText.trim()));
                    data.push(headerRow); // 將標題行加入資料
                }
                // 抓取表格數據行
                let rows = table.querySelectorAll('tbody tr'); 
                rows.forEach(row => {
                    let rowData = [];
                    let cells = row.querySelectorAll('td');
                    rowData.push(cells[0]?.querySelector('img')?.src || ''); // 商品圖片 URL
                    rowData.push(cells[1]?.innerText.trim() || '');         // 商品名稱
                    rowData.push(cells[2]?.innerText.trim() || '');         // 商品等級
                    rowData.push(cells[3]?.innerText.trim() || '');         // 商品價格
                    rowData.push(cells[4]?.innerText.trim() || '');         // 商品成本
                    rowData.push(cells[5]?.innerText.trim() || '');         // 品項編號
                    rowData.push(cells[6]?.innerText.trim() || '');         // 是否換回點數
                    if (rowData.length > 0) data.push(rowData);
                });
            });
            return data;
        """)

        # ✅ 轉換為 DataFrame
        df = pd.DataFrame(table_data, columns=["商品圖片", "商品名稱", "商品等級", "商品價格", "商品成本", "品項編號", "是否換回點數"])
        
        # ✅ 使用 `save_to_excel()`（共用 `ExcelSaver`）
        self.save_to_excel(df, prefix="inner_data")
        
        
        #print("✅ 展開折疊面板數據已獲取！")
        return df
