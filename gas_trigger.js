/**
 * 爬蟲觸發器 - 用於觸發 Render 上的爬蟲服務
 */

// 設定爬蟲 API 的 URL 和 API 金鑰
const SCRAPER_API_URL = "https://your-render-app-name.onrender.com/run-scraper";
const API_KEY = "your_api_key_here"; // 請替換為實際的 API 金鑰

/**
 * 觸發爬蟲服務的主函數
 */
function triggerWebScraper() {
  // 取得活動試算表
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const statusSheet = ss.getSheetByName("爬蟲狀態") || ss.insertSheet("爬蟲狀態");
  
  // 更新狀態為「執行中」
  statusSheet.getRange("A1").setValue("狀態");
  statusSheet.getRange("B1").setValue("執行中");
  statusSheet.getRange("A2").setValue("開始時間");
  statusSheet.getRange("B2").setValue(new Date().toLocaleString());
  
  try {
    // 設定 HTTP 請求選項
    const options = {
      "method": "post",
      "headers": {
        "X-API-Key": API_KEY
      },
      "muteHttpExceptions": true
    };
    
    // 發送請求到爬蟲 API
    const response = UrlFetchApp.fetch(SCRAPER_API_URL, options);
    const responseCode = response.getResponseCode();
    const responseText = response.getContentText();
    const responseJson = JSON.parse(responseText);
    
    // 更新執行結果
    if (responseCode === 200 && responseJson.status === "success") {
      statusSheet.getRange("B1").setValue("完成");
      statusSheet.getRange("A3").setValue("結果");
      statusSheet.getRange("B3").setValue("成功");
    } else {
      statusSheet.getRange("B1").setValue("失敗");
      statusSheet.getRange("A3").setValue("錯誤訊息");
      statusSheet.getRange("B3").setValue(responseJson.message || "未知錯誤");
    }
  } catch (error) {
    // 處理例外情況
    statusSheet.getRange("B1").setValue("失敗");
    statusSheet.getRange("A3").setValue("錯誤訊息");
    statusSheet.getRange("B3").setValue(error.toString());
  } finally {
    // 記錄結束時間
    statusSheet.getRange("A4").setValue("結束時間");
    statusSheet.getRange("B4").setValue(new Date().toLocaleString());
  }
}

/**
 * 建立選單項目，讓使用者可以手動觸發爬蟲
 */
function onOpen() {
  const ui = SpreadsheetApp.getUi();
  ui.createMenu('爬蟲工具')
    .addItem('執行資料爬取', 'triggerWebScraper')
    .addItem('查看爬蟲狀態', 'showScraperStatus')
    .addToUi();
}

/**
 * 顯示爬蟲狀態的對話框
 */
function showScraperStatus() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const statusSheet = ss.getSheetByName("爬蟲狀態");
  
  if (!statusSheet) {
    SpreadsheetApp.getUi().alert('尚未執行過爬蟲，沒有狀態資訊。');
    return;
  }
  
  const status = statusSheet.getRange("B1").getValue();
  const startTime = statusSheet.getRange("B2").getValue();
  const result = statusSheet.getRange("B3").getValue();
  const endTime = statusSheet.getRange("B4").getValue();
  
  const message = `爬蟲狀態：${status}\n開始時間：${startTime}\n結果：${result}\n結束時間：${endTime || "尚未完成"}`;
  
  SpreadsheetApp.getUi().alert(message);
}

/**
 * 設定每日自動執行爬蟲的觸發器
 */
function createDailyTrigger() {
  // 刪除現有的觸發器，避免重複
  const triggers = ScriptApp.getProjectTriggers();
  for (let i = 0; i < triggers.length; i++) {
    if (triggers[i].getHandlerFunction() === 'triggerWebScraper') {
      ScriptApp.deleteTrigger(triggers[i]);
    }
  }
  
  // 建立新的每日觸發器 (例如每天早上 8 點執行)
  ScriptApp.newTrigger('triggerWebScraper')
    .timeBased()
    .atHour(8)
    .everyDays(1)
    .create();
  
  SpreadsheetApp.getUi().alert('已設定每天早上 8 點自動執行爬蟲');
}