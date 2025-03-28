import os


class Config:
    """
    存放所有全域設定參數，如登入資訊、API 憑證等
    """

    LOGIN_URL = "https://want1yo.com/admin/auth/login"  # 管理後台登入網址
    # WAIT_ORDER_URL = "https://want1yo.com/admin/orders?delivery_status%5B0%5D=101&_order_prize_has=1&delivery_method%5B0%5D=1&delivery_method%5B1%5D=2&per_page=200"  # 待處理訂單頁面 URL
    # 未完成訂單:待處理、準備出貨 | 自取、寄送、未設定
    WAIT_ORDER_URL = "https://want1yo.com/admin/orders?per_page=200&id=&user_id=&user_name_now=&token=&_order_items_check=&shipping_address=&full_name=&user%5Bphone%5D=&shipping_phone=&final_price%5Bstart%5D=&final_price%5Bend%5D=&lottery%5Bname%5D=&lottery%5Bid%5D=&_lotttery_prize_name=&lottery%5Bstore_id%5D=&status=&delivery_status%5B%5D=101&delivery_status%5B%5D=104&_order_items_count=&_order_items_finish=&_order_prize_has=1&_is_only_point=&_is_sell_and_goods=&delivery_method%5B%5D=1&delivery_method%5B%5D=2&delivery_method%5B%5D=0&remark=&_has_remark=&created_at%5Bstart%5D=&created_at%5Bend%5D=&updated_at%5Bstart%5D=&updated_at%5Bend%5D=&orderItems%5Bupdated_at%5D%5Bstart%5D=&orderItems%5Bupdated_at%5D%5Bend%5D=&lottery%5Blottery_type_id%5D=&_has_cost_value="  # 待處理訂單頁面 URL
    # 換點
    # WAIT_ORDER_URL = "https://want1yo.com/admin/orders?_sort%5Bcolumn%5D=updated_at&_sort%5Btype%5D=desc&per_page=200&id=&user_id=&user_name_now=&token=&_order_items_check=&shipping_address=&full_name=&user%5Bphone%5D=&shipping_phone=&final_price%5Bstart%5D=&final_price%5Bend%5D=&lottery%5Bname%5D=&lottery%5Bid%5D=&_lotttery_prize_name=&lottery%5Bstore_id%5D=&status=&delivery_status%5B%5D=999&_order_items_count=&_order_items_finish=&_order_prize_has=1&_is_only_point=1&_is_sell_and_goods=&remark=&_has_remark=0&created_at%5Bstart%5D=&created_at%5Bend%5D=&updated_at%5Bstart%5D=&updated_at%5Bend%5D=&orderItems%5Bupdated_at%5D%5Bstart%5D=&orderItems%5Bupdated_at%5D%5Bend%5D=&lottery%5Blottery_type_id%5D=&_has_cost_value="  # 待處理訂單頁面 URL

    # 使用環境變數管理機密資訊
    USERNAME = os.environ.get("LOGIN_USERNAME", "kuo")  # 從環境變數獲取
    PASSWORD = os.environ.get("LOGIN_PASSWORD", "aaaa1111")  # 從環境變數獲取

    # 設定 Google Sheets API 參數
    # JSON_API = "C:\\Users\\user1\\Python_Program\\order_module_1\\data-analysis-want1yo-01dac495ad8a.json"
    # SHEET_ID = "1DCilPtEVtTUa6Pz9RsExE0jGEJl02NGaB0CbkYRXZAc"   # 試算表ID AppScript研究
    # SHEET_ID = "1pVvYc_RAWADyp0DNURglcf7AS7kCGWEcAOo9S037URU"   # 試算表ID 圈存商品整理
    # SHEET_ID = "1yxANJozq2p0OPp7ilu2iJtwBvie06FWkfDoS4K2kFY4"  # 試算表 比奇堡
    # WORKSHEET_NAME = "Order_Scraper"
    # WORKSHEET_NAME = "良級訂單"
    # 設定 Google Sheets API 參數
    SHEET_ID = os.environ.get(
        "SHEET_ID", "1yxANJozq2p0OPp7ilu2iJtwBvie06FWkfDoS4K2kFY4"
    )  # 試算表 ID
    WORKSHEET_NAME = os.environ.get("WORKSHEET_NAME", "良級訂單")  # 工作表名稱

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    JSON_API = os.path.join(BASE_DIR, "data-analysis-want1yo-01dac495ad8a.json")
