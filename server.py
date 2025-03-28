from flask import Flask, request, jsonify, render_template
import os
from main import main_process
import logging
from datetime import datetime
import threading
import json

# 確保日誌目錄存在
os.makedirs("logs", exist_ok=True)
# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(f"logs/server_{datetime.now().strftime('%Y%m%d')}.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# 設定密鑰，用於驗證請求
API_KEY = os.environ.get("API_KEY", "your_default_api_key_here")

# 全局變數，用於儲存爬蟲進度
scraper_status = {
    "status": "idle",  # idle, running, completed, failed
    "progress": 0,  # 0-100 百分比
    "message": "",  # 進度訊息
    "start_time": None,
    "end_time": None,
    "result": None,  # 最終結果
}

# 進度鎖，避免多線程問題
status_lock = threading.Lock()


def update_status(status, progress=None, message=None, result=None):
    """更新爬蟲狀態"""
    with status_lock:
        scraper_status["status"] = status

        if progress is not None:
            scraper_status["progress"] = progress

        if message is not None:
            scraper_status["message"] = message
            logger.info(f"進度更新: {message}")

        if status == "running" and scraper_status["start_time"] is None:
            scraper_status["start_time"] = datetime.now().isoformat()

        if status in ["completed", "failed"]:
            scraper_status["end_time"] = datetime.now().isoformat()
            scraper_status["result"] = result

        # 將狀態寫入檔案，以便重啟後恢復
        try:
            with open("scraper_status.json", "w", encoding="utf-8") as f:
                json.dump(scraper_status, f, ensure_ascii=False)
        except Exception as e:
            logger.error(f"無法寫入狀態檔案: {e}")


# 啟動時讀取之前的狀態
try:
    if os.path.exists("scraper_status.json"):
        with open("scraper_status.json", "r", encoding="utf-8") as f:
            saved_status = json.load(f)
            scraper_status.update(saved_status)
except Exception as e:
    logger.error(f"無法讀取狀態檔案: {e}")


@app.route("/")
def home():
    """首頁，顯示控制面板"""
    return render_template("index.html")


@app.route("/status")
def status():
    """查詢爬蟲狀態的 API 端點"""
    return jsonify(scraper_status)


@app.route("/run-scraper", methods=["POST"])
def run_scraper():
    """執行爬蟲的 API 端點，需要 API 金鑰驗證"""
    # 驗證 API 金鑰
    api_key = request.headers.get("X-API-Key")
    if api_key != API_KEY:
        logger.warning("API 金鑰驗證失敗")
        return jsonify({"status": "error", "message": "API 金鑰無效"}), 401

    # 檢查爬蟲是否已在執行中
    if scraper_status["status"] == "running":
        return (
            jsonify(
                {"status": "error", "message": "爬蟲已在執行中，請等待完成或查詢狀態"}
            ),
            409,
        )

    # 重設狀態
    update_status("running", 0, "開始執行爬蟲程序")

    # 在背景執行爬蟲，避免阻塞 API 回應
    def run_scraper_task():
        try:
            # 自訂進度回報函數，傳遞給 main_process
            def progress_callback(progress, message):
                update_status("running", progress, message)

            # 執行爬蟲主程序
            result = main_process(progress_callback)

            # 更新最終結果
            if result and result.get("status") == "success":
                update_status("completed", 100, "爬蟲程序執行成功", result)
                logger.info(f"爬蟲程序執行結果: {result}")
            else:
                update_status(
                    "failed",
                    None,
                    f"爬蟲程序執行失敗: {result.get('message', '未知錯誤')}",
                    result,
                )
                logger.error(f"爬蟲程序執行失敗: {result}")
        except Exception as e:
            error_msg = f"執行爬蟲時發生錯誤: {str(e)}"
            update_status(
                "failed", None, error_msg, {"status": "error", "message": error_msg}
            )
            logger.error(error_msg)

    # 啟動背景執行緒
    threading.Thread(target=run_scraper_task).start()

    # 立即回應請求，不等待爬蟲完成
    return jsonify(
        {
            "status": "accepted",
            "message": "爬蟲程序已開始執行，請使用 /status 端點查詢進度",
        }
    )


@app.route("/reset", methods=["POST"])
def reset_status():
    """重設爬蟲狀態的 API 端點，需要 API 金鑰驗證"""
    # 驗證 API 金鑰
    api_key = request.headers.get("X-API-Key")
    if api_key != API_KEY:
        logger.warning("API 金鑰驗證失敗")
        return jsonify({"status": "error", "message": "API 金鑰無效"}), 401

    # 檢查爬蟲是否正在執行
    if scraper_status["status"] == "running":
        return (
            jsonify({"status": "error", "message": "爬蟲正在執行中，無法重設狀態"}),
            409,
        )

    # 重設狀態
    with status_lock:
        scraper_status.update(
            {
                "status": "idle",
                "progress": 0,
                "message": "狀態已重設",
                "start_time": None,
                "end_time": None,
                "result": None,
            }
        )

        # 更新狀態檔案
        try:
            with open("scraper_status.json", "w", encoding="utf-8") as f:
                json.dump(scraper_status, f, ensure_ascii=False)
        except Exception as e:
            logger.error(f"無法寫入狀態檔案: {e}")

    return jsonify({"status": "success", "message": "爬蟲狀態已重設"})


@app.route("/api-docs")
def api_docs():
    """API 文件頁面"""
    return jsonify(
        {
            "api_endpoints": [
                {"path": "/", "method": "GET", "description": "控制面板首頁"},
                {"path": "/status", "method": "GET", "description": "查詢爬蟲狀態"},
                {
                    "path": "/run-scraper",
                    "method": "POST",
                    "description": "執行爬蟲程序",
                    "headers": {"X-API-Key": "API 金鑰，用於驗證"},
                },
                {
                    "path": "/reset",
                    "method": "POST",
                    "description": "重設爬蟲狀態",
                    "headers": {"X-API-Key": "API 金鑰，用於驗證"},
                },
            ]
        }
    )


if __name__ == "__main__":
    # 確保日誌目錄存在
    os.makedirs("logs", exist_ok=True)

    # 從環境變數獲取端口，Render 會自動設置 PORT 環境變數
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
