import pandas as pd
import os
import time
import re
from datetime import datetime
from excel_saver import ExcelSaver


class DataCleaner:
    """
    DataCleaner 負責清理單一 DataFrame，例如：
    - 移除指定欄位
    - 重設索引
    - 移除 NaN 欄位
    - 儲存 Excel 並確認寫入完成
    """

    def __init__(self, df):
        """
        初始化 DataCleaner
        :param df: pd.DataFrame - 需要清理的數據
        """
        self.df = df
        self.saver = ExcelSaver()  # ✅ **共用 Excel 儲存模組**

    def clean(self, columns_to_drop=None, index_to_drop=None):
        """
        清理數據，移除指定欄位與索引
        :param columns_to_drop: list - 需要移除的欄位
        :param index_to_drop: list - 需要移除的索引
        :return: pd.DataFrame - 清理後的數據
        """
        # print(f"📋 原始 DataFrame 欄位: {self.df.columns.tolist()}")

        # 移除指定欄位
        self.df.drop(columns=columns_to_drop, inplace=True, errors="ignore")
        self.df.reset_index(drop=True, inplace=True)  # 重設索引
        self.df.drop(index=index_to_drop, inplace=True, errors="ignore")
        self.df.reset_index(drop=True, inplace=True)  # 重設索引

        # 刪除所有值都是 NaN 的欄位
        self.df.dropna(axis=1, how="all", inplace=True)

        return self.df

    def save_to_excel(self, prefix="cleaned_data"):
        """使用 `ExcelSaver` 來存檔，並確保寫入完成"""
        return self.saver.save(self.df, filename_prefix=prefix)


class DataMerger:
    """
    DataMerger 負責合併兩個 DataFrame，並進行拆分、排序等進一步處理
    """

    def __init__(self, cleaned1_path, cleaned2_path):
        """初始化 DataMerger 載入兩份 Excel 檔案"""
        self.cleaned1_path = cleaned1_path
        self.cleaned2_path = cleaned2_path
        self.df_cleaned1 = pd.read_excel(cleaned1_path, sheet_name="Sheet1")
        self.df_cleaned2 = pd.read_excel(cleaned2_path, sheet_name="Sheet1")
        self.df_merged = None
        self.saver = ExcelSaver()  # ✅ **共用 Excel 儲存模組**

    def expand_data(self):
        """
        解析 `物品數量`，並展開數據
        """
        try:
            # 先檢查欄位是否存在
            if "物品數量" not in self.df_cleaned1.columns:
                print(
                    f"⚠️ 警告：找不到 '物品數量' 欄位，可用欄位: {self.df_cleaned1.columns.tolist()}"
                )
                return

            # 使用更安全的轉換方式，處理可能的 NaN 值
            extracted = self.df_cleaned1["物品數量"].str.extract(r"\((\d+)\)")
            # 將無法解析的值設為 1 (預設一個)
            self.df_cleaned1["物品數量解析"] = (
                pd.to_numeric(extracted[0], errors="coerce").fillna(1).astype("Int64")
            )

            # 使用更高效的方法展開數據
            expanded_rows = []
            for _, row in self.df_cleaned1.iterrows():
                count = row["物品數量解析"]
                # 確保 count 是有效的整數
                if pd.notna(count) and count > 0:
                    for _ in range(int(count)):
                        expanded_rows.append(row.to_dict())
                else:
                    # 如果無法解析數量，至少保留原始行
                    expanded_rows.append(row.to_dict())

            # 轉換回 DataFrame
            self.df_cleaned1 = pd.DataFrame(expanded_rows)
            print(f"✅ 數據展開完成：從 {len(expanded_rows)} 行展開")
        except Exception as e:
            print(f"❌ 展開數據時發生錯誤: {str(e)}")
            # 在錯誤情況下，保留原始數據
            pass

    def remove_empty_rows(self):
        """
        移除 cleaned2 內的空白列
        """
        self.df_cleaned2 = self.df_cleaned2.dropna(subset=["商品名稱"]).reset_index(
            drop=True
        )

    def merge(self):
        """
        將 cleaned1 和 cleaned2 進行橫向合併
        """
        self.df_merged = pd.concat(
            [
                self.df_cleaned1.reset_index(drop=True),
                self.df_cleaned2.reset_index(drop=True),
            ],
            axis=1,
        )

    def split_data(self):
        """
        拆分 `收件資料`、`會員資料`、`套組資訊`
        """
        self.df_merged["電話"] = self.df_merged["收件資料"].str.extract(r"^(\d{10})")
        self.df_merged["地址"] = self.df_merged["收件資料"].str.replace(
            r"^\d{10}\s*", "", regex=True
        )
        self.df_merged["郵遞區號"] = self.df_merged["地址"].str.extract(r"\((\d{3})\)")
        self.df_merged["縣市"] = self.df_merged["地址"].str.extract(r"(\D{2,3}市)")
        self.df_merged["區域"] = self.df_merged["地址"].str.extract(r"市(.{1,5})\(")

        self.df_merged["會員名稱"] = self.df_merged["會員資料"].str.extract(
            r"^(.+)\nID:"
        )
        self.df_merged["會員ID"] = (
            self.df_merged["會員資料"]
            .str.extract(r"ID: (\d+)")
            .astype(float)
            .astype("Int64")
        )
        self.df_merged["會員暱稱"] = self.df_merged["會員資料"].str.extract(
            r"當下暱稱: (.+)"
        )

        self.df_merged["套組ID"] = (
            self.df_merged["套組資訊"]
            .str.extract(r"^(\d+)")
            .astype(float)
            .astype("Int64")
        )
        self.df_merged["套組名稱"] = self.df_merged["套組資訊"].str.extract(
            r"-\s([^-\n]+)"
        )
        self.df_merged["抽獎類型"] = self.df_merged["套組資訊"].str.extract(r"\n(.+)$")

    def format_data(self):
        """
        格式化 `商品價格`、`建立時間` 和 `更新時間`
        """
        self.df_merged["商品價格"] = self.df_merged["商品價格"].astype("Int64")
        self.df_merged["建立時間"] = pd.to_datetime(
            self.df_merged["建立時間"]
        ).dt.strftime("%Y-%m-%d")
        self.df_merged["更新時間"] = pd.to_datetime(
            self.df_merged["更新時間"]
        ).dt.strftime("%Y-%m-%d")

    def remove_newlines(self):
        """
        移除所有欄位內的換行符號 `\n`
        """
        # print("🔄 格式化數據，移除換行符號...")
        self.df_merged = self.df_merged.map(
            lambda x: x.replace("\n", " ") if isinstance(x, str) else x
        )
        # self.df_merged = self.df_merged.apply(lambda col: col.map(lambda x: x.replace("\n", " ") if isinstance(x, str) else x))
        # 確保每一列數據都正確處理換行符號
        # self.df_merged = self.df_merged.apply(lambda col: col.map(lambda x: x.replace("\n", " ") if isinstance(x, str) else x))

    def sort_data(self):
        """
        根據 `運送狀態`、`領取方式`、`建立時間` 進行排序
        """
        運送狀態排序 = {"待處理": 1, "準備出貨": 2, "已出貨": 3, "完成": 4}
        領取方式排序 = {"自取": 1, "物流寄送": 2, "未設定": 3}
        self.df_merged["運送狀態排序"] = self.df_merged["運送狀態"].map(運送狀態排序)
        self.df_merged["領取方式排序"] = self.df_merged["領取方式"].map(領取方式排序)

        self.df_merged.sort_values(
            by=["運送狀態排序", "領取方式排序", "建立時間"],
            ascending=[True, True, True],
            inplace=True,
        )
        self.df_merged.drop(columns=["運送狀態排序", "領取方式排序"], inplace=True)

    def process_all(self):
        """
        執行所有數據處理步驟
        """
        self.expand_data()
        self.remove_empty_rows()
        self.merge()
        self.split_data()
        self.format_data()
        self.sort_data()
        self.remove_newlines()

        # 確保 df_merged 仍是 DataFrame
        if not isinstance(self.df_merged, pd.DataFrame):
            raise TypeError("❌ df_merged 不是 DataFrame，可能發生錯誤")

        return self.df_merged
