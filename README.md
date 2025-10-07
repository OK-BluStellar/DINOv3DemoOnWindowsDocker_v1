# DINOv3 Zero-Shot セグメンテーションデモ

DINOv3の強力な密な特徴量（Dense Features）を利用して、学習なし（Zero-Shot）で画像セグメンテーションを実行するデモアプリケーションです。

## 概要

このプロジェクトは、Meta AIが開発したDINOv2（DINOv3とも呼ばれる）モデルを使用して、画像上の参照領域と類似した領域を自動的に検出します。事前学習済みモデルの密な特徴量とコサイン類似度を用いることで、特定のタスクに対する追加学習なしでセグメンテーションを実行できます。

## 主な機能

- **画像アップロード**: 任意の画像をアップロードして処理
- **参照領域選択**: マウスドラッグで矩形を描画し、参照パッチを指定
- **Zero-Shotセグメンテーション**: DINOv2/DINOv3の特徴量を使用して類似領域を自動検出
- **複数モデルサポート**: DINOv2とDINOv3の両方に対応し、環境変数で簡単に切り替え可能
- **マスク表示**: セグメンテーション結果を元画像にオーバーレイ表示
- **透明度調整**: スライダーでマスクの透明度を調整可能

## モデルの切り替え

このアプリケーションは、DINOv2とDINOv3の両方のモデルをサポートしています。デフォルトではDINOv2が使用されますが、環境変数を設定することでDINOv3に切り替えることができます。

### 利用可能なモデル

#### DINOv2 (デフォルト)
- モデル名: `facebook/dinov2-base`
- 特徴: 安定した性能、より高速
- トークン構造: [CLS token, patch tokens]

#### DINOv3
- モデル名: `facebook/dinov3-vitb16-pretrain-lvd1689m`
- 特徴: 最新のアーキテクチャ、より高精度
- トークン構造: [CLS token, register tokens, patch tokens]
- その他のサイズ:
  - Small: `facebook/dinov3-vits16-pretrain-lvd1689m`
  - Large: `facebook/dinov3-vitl16-pretrain-lvd1689m`
  - Huge: `facebook/dinov3-vithuge16-pretrain-lvd1689m`

### モデルの変更方法

**方法1: 環境変数を使用（推奨）**

```bash
# DINOv3を使用する場合
export MODEL_NAME=facebook/dinov3-vitb16-pretrain-lvd1689m
docker-compose up --build

# DINOv2に戻す場合（または環境変数を削除）
export MODEL_NAME=facebook/dinov2-base
docker-compose up --build
```

**方法2: .envファイルを使用**

プロジェクトのルートディレクトリに`.env`ファイルを作成し、以下を記述:

```
MODEL_NAME=facebook/dinov3-vitb16-pretrain-lvd1689m
```

その後、Docker Composeを起動:

```bash
docker-compose up --build
```

**注意事項:**
- モデルを切り替えた後は、`docker-compose up --build`を実行してコンテナを再構築してください
- 初回起動時は、モデルのダウンロードに時間がかかる場合があります
- DINOv3モデルは、DINOv2と比較してメモリ使用量が若干多くなる場合があります
- **重要**: DINOv3モデルは**Gated Repository**（制限付きリポジトリ）です。使用するにはHugging Faceアカウントでの認証が必要です

### DINOv3モデルの認証設定

DINOv3モデルを使用する場合は、以下の手順で認証を設定してください：

1. **Hugging Faceアカウントの作成**
   - [Hugging Face](https://huggingface.co/)でアカウントを作成

2. **モデルへのアクセス申請**
   - [DINOv3モデルページ](https://huggingface.co/facebook/dinov3-vitb16-pretrain-lvd1689m)にアクセス
   - "Agree and Access Repository"をクリックして利用規約に同意

3. **アクセストークンの取得**
   - [Settings > Access Tokens](https://huggingface.co/settings/tokens)でトークンを作成
   - "Read"権限で十分です

4. **トークンの設定**
   
   プロジェクトのルートディレクトリに`.env`ファイルを作成し、以下を記述:
   
   ```
   MODEL_NAME=facebook/dinov3-vitb16-pretrain-lvd1689m
   HF_TOKEN=your_huggingface_token_here
   ```

5. **Docker Composeファイルの更新**
   
   `docker-compose.yml`のbackendサービスに環境変数を追加:
   
   ```yaml
   backend:
     environment:
       - PYTHONUNBUFFERED=1
       - MODEL_NAME=${MODEL_NAME:-facebook/dinov2-base}
       - HF_TOKEN=${HF_TOKEN:-}
   ```

6. **コンテナの起動**
   
   ```bash
   docker-compose up --build
   ```

**DINOv2は認証不要**: DINOv2モデル（`facebook/dinov2-base`）は認証なしで使用できます。DINOv3の認証設定が面倒な場合は、DINOv2をご利用ください。

## デモンストレーション

以下は、アプリケーションの動作を示すスクリーンショットです。

### 1. 初期画面
アプリケーション起動時の画面です。画像アップロードボタンが表示されています。

![初期画面](demo_images/01_initial_state.png)

### 2. 画像アップロード
画像をアップロードすると、キャンバスに表示されます。参照領域の選択が可能になります。

![画像アップロード](demo_images/02_image_uploaded.png)

### 3. 参照領域の選択
マウスドラッグで矩形を描画し、セグメンテーションの参照領域を指定します。この例では、猫の顔部分を参照領域として選択しています。

![参照領域の選択](demo_images/02_5_rectangle_selected.png)

### 4. セグメンテーション結果
「セグメンテーション実行」ボタンをクリックすると、DINOv2モデルが参照領域と類似した部分を検出し、セグメンテーションマスクとして表示します。参照領域（猫の顔）と類似した特徴を持つ領域が明るく表示されています。

![セグメンテーション結果](demo_images/04_segmentation_result.png)

### デモ動作の特徴
- **Zero-Shot**: 事前学習なしで、参照領域に類似した領域を自動検出
- **リアルタイム処理**: 数秒でセグメンテーション結果を取得
- **視覚的フィードバック**: 透明度調整可能なマスクオーバーレイ表示
- **インタラクティブUI**: マウス操作で直感的に参照領域を選択可能

## 技術スタック

### バックエンド
- **Python 3.12**
- **FastAPI**: 高速なWeb APIフレームワーク
- **PyTorch 2.8.0**: 深層学習フレームワーク
- **Transformers 4.57.0**: Hugging Faceのモデルライブラリ
- **DINOv2/DINOv3モデル**: `facebook/dinov2-base` (デフォルト) または `facebook/dinov3-vitb16-pretrain-lvd1689m` (Hugging Face)

### フロントエンド
- **React 18** + **TypeScript**
- **Vite**: 高速ビルドツール
- **Tailwind CSS**: ユーティリティファーストCSSフレームワーク
- **shadcn/ui**: モダンなUIコンポーネントライブラリ

### デプロイメント
- **Docker** + **Docker Compose**
- **Nginx**: フロントエンドの静的ファイル配信

## システム要件

### 必須
- **Windows 10/11** (64-bit)
- **Docker Desktop for Windows** (最新版推奨)
- **WSL2** (Windows Subsystem for Linux 2)
- **メモリ**: 最低8GB RAM（16GB以上推奨）
- **ストレージ**: 10GB以上の空き容量

### GPU使用時（オプション）
- **NVIDIA GPU** (CUDA対応)
- **NVIDIA Driver** (最新版)
- **NVIDIA Container Toolkit**

## セットアップ手順

### 1. Docker Desktop for Windowsのインストール

1. [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/)をダウンロード
2. インストーラーを実行し、指示に従ってインストール
3. インストール完了後、Dockerを起動
4. WSL2バックエンドが有効になっていることを確認

### 2. リポジトリのクローン

```bash
git clone https://github.com/OK-BluStellar/DINOv3DemoOnWindowsDocker_v1.git
cd DINOv3DemoOnWindowsDocker_v1
```

### 3. アプリケーションの起動

Docker Composeを使用してバックエンドとフロントエンドを同時に起動します：

```bash
docker-compose up --build
```

初回起動時は、Dockerイメージのビルドとモデルのダウンロードに時間がかかります（10〜15分程度）。

### 4. アプリケーションへのアクセス

ブラウザで以下のURLにアクセスします：

- **フロントエンド**: http://localhost:3000
- **バックエンドAPI**: http://localhost:8000
- **APIドキュメント**: http://localhost:8000/docs

### 5. 使用方法

1. **画像をアップロード**: 「画像をアップロード」ボタンをクリックして画像を選択
2. **参照領域を選択**: 画像上でマウスをドラッグして矩形を描画
3. **セグメンテーション実行**: 「セグメンテーション実行」ボタンをクリック
4. **結果の確認**: セグメンテーションマスクが画像上にオーバーレイ表示されます
5. **透明度調整**: スライダーでマスクの透明度を調整できます

## GPU対応（オプション）

### Windows + WSL2でのGPU使用

Windows 11およびWindows 10（バージョン21H2以降）では、WSL2を通じてDockerコンテナからGPUにアクセスできます。

#### 前提条件
1. **NVIDIA GPU**がインストールされている
2. **NVIDIA Driver**（最新版）がWindowsにインストールされている
3. **WSL2**が有効になっている

#### セットアップ手順

1. **NVIDIA Container Toolkitのインストール（WSL2内）**

WSL2のUbuntuターミナルで以下を実行：

```bash
# リポジトリの設定
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list | \
    sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
    sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

# インストール
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit

# Dockerの設定
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```

2. **docker-compose.ymlの変更**

`docker-compose.yml`のbackendサービスに以下を追加：

```yaml
services:
  backend:
    # ... 既存の設定 ...
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

3. **動作確認**

```bash
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi
```

GPUが正しく認識されていれば、nvidia-smiの出力が表示されます。

### 注意事項

- GPU使用時はVRAMを大量に消費します（最低4GB、推奨8GB以上）
- GPUが利用できない環境でもCPUで動作しますが、処理時間が長くなります
- 初回実行時はモデルのダウンロードに時間がかかります（約3GB）

## DINOv2/DINOv3モデルについて

このデモでは、Meta AIが開発した**DINOv2**および**DINOv3**モデルを使用しています。デフォルトでは`facebook/dinov2-base`が使用されますが、環境変数で`facebook/dinov3-vitb16-pretrain-lvd1689m`などに切り替え可能です。

### モデルの特徴
- **自己教師あり学習**: ラベルなしデータから特徴量を学習
- **密な特徴量**: 画像の各パッチから高品質な特徴ベクトルを抽出
- **汎用性**: 様々な下流タスクに適用可能
- **Zero-Shot能力**: 追加学習なしで新しいタスクに対応

### DINOv3の改善点
- **レジスタートークン**: 4つのレジスタートークンを導入し、より安定した特徴抽出を実現
- **大規模データセット**: LVD-142Mデータセットでの事前学習
- **高精度化**: 様々なビジョンタスクでDINOv2を上回る性能

### 処理フロー
1. 画像を14×14ピクセルまたは16×16ピクセルのパッチに分割（モデルによる）
2. 各パッチから768次元の特徴ベクトルを抽出（DINOv2-base、DINOv3-base）
3. レジスタートークンをスキップしてパッチ特徴量のみを取得（DINOv3の場合）
4. 参照領域のパッチ特徴量を平均化
5. 全パッチとのコサイン類似度を計算
6. 類似度マップを元の画像サイズにアップサンプリング

## トラブルシューティング

### Dockerが起動しない
- Docker Desktopが正しくインストールされているか確認
- WSL2が有効になっているか確認
- Windowsを再起動してみる

### モデルのダウンロードが遅い
- 初回起動時は約3GBのモデルをダウンロードするため時間がかかります
- ネットワーク接続を確認してください

### メモリ不足エラー
- Docker Desktopの設定でメモリ割り当てを増やす
- 他のアプリケーションを終了してメモリを確保

### ポートが使用中
- `docker-compose.yml`でポート番号を変更
- 例: `3000:80` → `3001:80`

## 開発

### ローカル開発環境

#### バックエンド

```bash
cd backend
poetry install
poetry run fastapi dev app/main.py
```

APIは http://localhost:8000 で起動します。

#### フロントエンド

```bash
cd frontend
npm install
npm run dev
```

開発サーバーは http://localhost:5173 で起動します。

### コンテナの停止

```bash
docker-compose down
```

コンテナとネットワークを削除する場合：

```bash
docker-compose down -v
```

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。

## 謝辞

- Meta AIのDINOv2/DINOv3モデル
- Hugging Face Transformersライブラリ
- FastAPIとReactのコミュニティ

## お問い合わせ

問題や質問がある場合は、GitHubのIssuesでお知らせください。
