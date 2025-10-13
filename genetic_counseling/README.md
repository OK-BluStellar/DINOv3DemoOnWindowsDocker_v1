# 🧬 遺伝カウンセリング教育用エージェント

Docker完結型の遺伝カウンセリング教育用AIエージェントシステムです。WindowsのDocker環境で動作し、ブラウザから簡単にアクセスできます。

## 📋 概要

このシステムは、遺伝カウンセリングの練習と評価を目的とした教育用ツールです。ローカルLLM（Ollama）を使用し、プロンプトによって定義された患者のロールを学生が相手にすることで、カウンセリングスキルの向上を支援します。

## ✨ 主な機能

### 🎯 コア機能
- **AIチャット**: ローカルLLMを使用した患者役とのリアルタイム対話
- **柔軟な設定管理**: Hydraによる構成管理で、プロンプトとモデル設定を完全分離
- **ブラウザUI**: Gradioによる直感的なWebインターフェース
- **簡単セットアップ**: Dockerコマンド一つで環境構築完了

### ⚙️ 設定機能
- **モデル選択**: LLMモデルを動的に切り替え（llama3, gemma等）
- **プロンプト編集**: 患者の性格・背景・症状をプロンプトで定義
- **パラメータ調整**: Temperature、Max Tokens、Top Pなどの細かい調整
- **プリセット機能**: 事前定義された患者ロールとモデルの組み合わせ

## 🏗️ システムアーキテクチャ

### 技術スタック

```
┌─────────────────────────────────────────┐
│           Windows + Docker              │
│  ┌─────────────────────────────────┐   │
│  │  Gradio UI (Port 7860)          │   │
│  │  - チャットインターフェース       │   │
│  │  - 設定パネル                    │   │
│  │  - プロンプト編集                │   │
│  └────────────┬────────────────────┘   │
│               │                          │
│  ┌────────────▼────────────────────┐   │
│  │  Python Application              │   │
│  │  - Hydra Config Manager          │   │
│  │  - Ollama Client                 │   │
│  └────────────┬────────────────────┘   │
│               │                          │
│  ┌────────────▼────────────────────┐   │
│  │  Ollama (Port 11434)             │   │
│  │  - ローカルLLM実行環境            │   │
│  │  - 各種モデル対応                 │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

### 主要コンポーネント

- **Ollama**: ローカルでLLMを実行するエンジン
- **Gradio**: Webベースの対話型UI
- **Hydra**: 階層的な設定管理フレームワーク
- **Docker**: 完全なコンテナ化環境

## 📁 ディレクトリ構造

```
genetic_counseling/
├── config/                  # Hydra設定ファイル
│   ├── config.yaml         # メイン設定
│   ├── llm/                # LLMモデル設定
│   │   ├── llama3.yaml
│   │   └── gemma.yaml
│   └── prompt/             # 患者プロンプト定義
│       ├── default_patient.yaml
│       └── brca_patient.yaml
├── src/                     # ソースコード
│   ├── app.py              # Gradioアプリケーション
│   ├── config_manager.py   # Hydra設定管理
│   └── llm_client.py       # Ollamaクライアント
├── Dockerfile              # アプリケーションコンテナ
├── docker-compose.yml      # Docker Compose設定
├── requirements.txt        # Python依存関係
└── README.md              # このファイル
```

## 🚀 セットアップ手順

### 前提条件

- **Windows 10/11** (64-bit)
- **Docker Desktop for Windows** (最新版推奨)
- **WSL2** (Windows Subsystem for Linux 2)
- **メモリ**: 最低8GB RAM（16GB以上推奨）

### 1. Docker Desktop のインストール

1. [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/)をダウンロード
2. インストーラーを実行
3. WSL2バックエンドを有効化

### 2. リポジトリのクローン

```bash
git clone https://github.com/OK-BluStellar/DINOv3DemoOnWindowsDocker_v1.git
cd DINOv3DemoOnWindowsDocker_v1/genetic_counseling
```

### 3. システムの起動

```bash
docker-compose up --build
```

初回起動時は以下の処理が実行されます（10〜15分程度）：
- Dockerイメージのビルド
- Ollamaのセットアップ
- 必要なLLMモデルのダウンロード

### 4. モデルのダウンロード（初回のみ）

別のターミナルで以下を実行してモデルをダウンロード：

```bash
docker exec -it gc-ollama ollama pull llama3:8b
docker exec -it gc-ollama ollama pull gemma:7b
```

### 5. アプリケーションへのアクセス

ブラウザで以下のURLにアクセス：

```
http://localhost:7860
```

## 📖 使用方法

### 基本的な使い方

1. **プリセット選択**
   - 左側のパネルから「LLMプリセット」と「患者プロンプトプリセット」を選択
   - 「プリセット読み込み」ボタンをクリック

2. **カウンセリング開始**
   - チャット欄に患者への質問やコメントを入力
   - AIが患者役として応答を返します

3. **会話のリセット**
   - 「会話をリセット」ボタンで新しいセッションを開始

### カスタマイズ

#### LLMモデル設定の変更

1. 「LLMモデル設定」アコーディオンを展開
2. 以下のパラメータを調整：
   - **モデル名**: 使用するLLMモデル（例: llama3:8b）
   - **Temperature**: 0.0（保守的）〜 2.0（創造的）
   - **最大トークン数**: 応答の長さ制限
   - **Top P**: 応答の多様性
3. 「モデル設定を更新」をクリック

#### システムプロンプトの編集

1. 「システムプロンプト（患者の定義）」アコーディオンを展開
2. テキストエリアで患者の設定を編集：
   - 患者プロフィール（年齢、性別、主訴など）
   - 家族歴
   - 性格・特徴
   - 患者役としての指示
3. 「プロンプトを更新」をクリック

### 新しい患者プロンプトの作成

`config/prompt/`ディレクトリに新しいYAMLファイルを作成：

```yaml
# config/prompt/your_patient.yaml
system_prompt: |
  あなたは遺伝カウンセリングを受けに来た患者役を演じてください。
  
  # 患者プロフィール
  - 年齢: XX歳
  - 性別: XXX
  - 主訴: XXXXXXXXXXXX
  
  # 指示
  - XXXXXXXXXXXX

description: "患者の簡単な説明"
```

## 🔧 設定ファイルの詳細

### Hydra設定構造

```
config/
├── config.yaml          # ルート設定
├── llm/                 # LLMモデル設定群
│   ├── llama3.yaml
│   └── gemma.yaml
└── prompt/              # 患者プロンプト群
    ├── default_patient.yaml
    └── brca_patient.yaml
```

### 設定の優先順位

1. UIから直接入力された値（最優先）
2. プリセット選択による設定
3. デフォルト設定（config.yaml）

## 🎓 教育的活用例

### 1. 基本的なカウンセリングスキルの練習

- 傾聴スキルの向上
- 適切な質問技法の習得
- 情報提供の練習

### 2. 様々な患者ケースへの対応

- 家族歴を持つ患者
- BRCA変異キャリア
- 検査結果の説明

### 3. モデル性能の比較研究

- 異なるLLMモデルでの患者役の比較
- プロンプトエンジニアリングの実験
- 応答品質の評価

## 🛠️ トラブルシューティング

### Dockerが起動しない

- Docker Desktopが正しくインストールされているか確認
- WSL2が有効になっているか確認
- Windowsを再起動

### Ollamaに接続できない

```bash
docker logs gc-ollama
```

でログを確認し、エラーがないかチェック

### モデルが見つからない

```bash
docker exec -it gc-ollama ollama list
```

で利用可能なモデルを確認し、必要に応じてダウンロード：

```bash
docker exec -it gc-ollama ollama pull <model-name>
```

### メモリ不足エラー

- Docker Desktopの設定でメモリ割り当てを増やす
- 他のアプリケーションを終了

## 📊 対応モデル

### 推奨モデル

- **llama3:8b** - バランスの取れた性能
- **gemma:7b** - 高速な応答
- **mistral:7b** - 高品質な対話

### モデルの追加方法

```bash
docker exec -it gc-ollama ollama pull <model-name>
```

利用可能なモデル一覧は[Ollama Library](https://ollama.ai/library)を参照

## 🔬 研究・論文化への活用

### データ収集

- 会話履歴の保存（今後実装予定）
- 評価指標の記録
- プロンプトバリエーションの管理

### 分析可能な要素

- モデル間の性能比較
- プロンプトの効果測定
- カウンセリング品質の定量化

## 🤝 貢献

プルリクエストを歓迎します。大きな変更の場合は、まずIssueを開いて変更内容を議論してください。

## 📝 ライセンス

このプロジェクトはMITライセンスの下で公開されています。

## 🙏 謝辞

- [Ollama](https://ollama.ai/) - ローカルLLM実行環境
- [Gradio](https://gradio.app/) - WebUIフレームワーク
- [Hydra](https://hydra.cc/) - 設定管理フレームワーク
- Meta AI（Llama）、Google（Gemma）などのLLMモデル提供者

## 📞 お問い合わせ

問題や質問がある場合は、GitHubのIssuesでお知らせください。
