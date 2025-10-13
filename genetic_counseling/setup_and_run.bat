@echo off
echo 🚀 遺伝カウンセリングエージェント セットアップスクリプト
echo ==================================================
echo.

echo 📋 ステップ1: Docker Composeでサービスを起動...
docker-compose up -d

echo.
echo ⏳ ステップ2: Ollamaサービスの起動を待機中...
timeout /t 10 /nobreak > nul

echo.
echo 📥 ステップ3: LLMモデルのダウンロード...
echo    - llama3:8b をダウンロード中...
docker exec -it gc-ollama ollama pull llama3:8b

echo.
echo    - gemma:7b をダウンロード中...
docker exec -it gc-ollama ollama pull gemma:7b

echo.
echo ✅ セットアップ完了！
echo.
echo 🌐 アプリケーションにアクセス:
echo    Gradio UI: http://localhost:7860
echo    Ollama API: http://localhost:11434
echo.
echo 📝 使い方:
echo    1. ブラウザで http://localhost:7860 にアクセス
echo    2. プリセットを選択してカウンセリングセッションを開始
echo    3. システムプロンプトやモデル設定をカスタマイズ可能
echo.
echo 🛑 停止方法:
echo    docker-compose down
echo.
pause
