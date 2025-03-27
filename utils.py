import os
import time
from datetime import datetime

def wait_for_file(filepath, timeout=30):
    """
    等待文件寫入完成
    :param filepath: 文件路徑
    :param timeout: 超時時間（秒）
    :return: 是否成功
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            # 嘗試打開文件進行讀取，如果成功則表示文件已寫入完成
            with open(filepath, 'r') as f:
                f.read(1)  # 嘗試讀取一個字節
            return True
        except (IOError, PermissionError):
            # 文件可能正在被寫入，等待一段時間
            time.sleep(0.5)
    return False

def log_message(message):
    """
    記錄日誌訊息
    :param message: 要記錄的訊息
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_dir = "logs"
    
    # 確保日誌目錄存在
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        
    log_file = os.path.join(log_dir, f"app_{datetime.now().strftime('%Y%m%d')}.log")
    
    # 寫入日誌文件
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"{timestamp} - {message}\n")
    
    # 同時輸出到控制台
    print(f"{timestamp} - {message}")