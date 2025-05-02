@echo off
echo 正在刪除所有 .pyc 檔案與 __pycache__ 資料夾...

for /R %%f in (*.pyc) do del "%%f"
for /R %%d in (.) do (
    if exist "%%d\__pycache__" (
        rmdir /s /q "%%d\__pycache__"
    )
)

echo 成功刪除所有快取檔案！

REM 確保 .gitignore 存在
IF NOT EXIST .gitignore (
    echo. > .gitignore
)

REM 檢查並新增 ignore 規則
findstr /x /c:"*.pyc" .gitignore >nul || echo *.pyc>>.gitignore
findstr /x /c:"__pycache__/" .gitignore >nul || echo __pycache__/>>.gitignore

echo .gitignore 更新完成！

git add .gitignore
git commit -m "Clean .pyc and update .gitignore"
git push

echo 🎉 專案快取清理完成！
pause