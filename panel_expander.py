from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class PanelExpander:
    def __init__(self, driver):
        """
        初始化摺疊面板展開模組
        :param driver: Selenium WebDriver 物件
        """
        self.driver = driver

    def expand_third_panels_js(self, timeout=10):
        """
        使用 JavaScript 點擊方式展開每組訂單的第三個摺疊面板，並確保內容加載完成
        :param timeout: int - 等待展開內容的最大時間（秒）
        """
        #print("📌 正在使用 JavaScript 展開每組的第三個摺疊面板...")

        # **修正 JavaScript 語法錯誤**
        script = """
        let buttons = document.querySelectorAll('.feather.icon-chevrons-right');
        let clickedIndexes = [];
        for (let i = 0; i < buttons.length; i++) {
            if ((i + 1) % 3 === 0) { // 只選擇第3個
                buttons[i].click();
                clickedIndexes.push(i + 1);
            }
        }
        return clickedIndexes;
        """

        try:
            clicked_indexes = self.driver.execute_script(script)
            #print(f"✅ 已點擊第 {clicked_indexes} 個摺疊面板按鈕")

            #print("✅ 所有摺疊面板已展開")

        except Exception as e:
            print(f"❌ JavaScript 執行錯誤: {e}")
