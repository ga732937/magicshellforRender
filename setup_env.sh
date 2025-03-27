#完整自動化流程
#✅ 建立虛擬環境
#✅ 安裝 requirements.txt（如果存在）
#✅ 建立 .gitignore（如果不存在）
#在終端機執行 (bash)
#chmod +x setup_env.sh  # 給予執行權限
#./setup_env.sh



#!/bin/bash

# Step 1: 建立虛擬環境
python -m venv venv
source venv/bin/activate  # Windows 使用 venv\Scripts\activate

# Step 2: 安裝套件
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo "No requirements.txt found, skipping installation"
fi

# Step 3: 建立 .gitignore（如果不存在）
if [ ! -f ".gitignore" ]; then
    echo "venv/" > .gitignore
    echo ".vscode/" >> .gitignore
    echo "__pycache__/" >> .gitignore
    echo "*.pyc" >> .gitignore
    echo "*.pyo" >> .gitignore
    echo "Created .gitignore"
fi

# Step 4: 提交 .gitignore 到 Git
git add .gitignore
git commit -m "Added .gitignore to ignore venv"
git push origin main

echo "✅ 環境設定完成！"
