# Kindle スクリーンショット → PDF 変換ツール ✅

**短い説明**

このプロジェクトは、macOS 環境で Kindle アプリのページを自動でスクリーンショットし、撮影した画像を PDF に変換して保存するツールです。

---

## 🔧 主な機能

- Kindle アプリを開き自動でページめくりしてスクリーンショットを撮影
- 撮影した画像を並べて PDF に変換（サイズが大きくなる場合はパート分割）
- スクリーンショットは `screenshots_books/<safe_book_title>/` に保存

---

## ⚙️ 前提条件（Prerequisites）

- macOS
- Kindle (Macアプリ) がインストールされていること
- Python 3.8+
- 仮想環境の使用を推奨
- 追加（OCR を使う場合）: Tesseract (`brew install tesseract`)

必要な Python パッケージは `requirements.txt` に記載されています。

---

## 🚀 セットアップ

1. 仮想環境を作成（任意）

```bash
python -m venv .venv
```

2. 仮想環境を有効化して依存をインストール

```bash
source .venv/bin/activate && pip install -r requirements.txt
```

---

## ▶️ 実行方法

指定のコマンドを実行して開始します（あなたがいつも使っているコマンド）:

```bash
source .venv/bin/activate && python kindle_screenshot.py
```

実行時の流れ:

1. スクリプトが Kindle を起動してフォーカスします（`com.amazon.Lassen` バンドルID を使用）
2. コンソールで「検索する本のタイトル」を入力
3. 指定した本のフォルダ（`screenshots_books/<safe_book_title>/`）に順次画像を保存
4. ページ終了検出後、自動で `screenshot2pdf.convert_to_pdf` が呼ばれて PDF を生成

---

## 📁 出力先とファイル名

- スクリーンショット: `screenshots_books/<safe_book_title>/kindle_page_<timestamp>.png`
- 生成される PDF: `screenshots_books/<safe_book_title>/<book_title>_part{n}.pdf`
  - 20MB を超える場合はパート分割されます

---

## ❗ 注意・トラブルシューティング

- Kindle が起動しない・ウィンドウにフォーカスできない場合は、`kindle_screenshot.py` の `open_kindle()` と `focus_kindle_window()` を確認してください。バンドルID は `com.amazon.Lassen` になっています。

> macOS の「システム環境設定」→「セキュリティとプライバシー」→「アクセシビリティ」/「スクリーン録画」で **Terminal または 使用する IDE を許可** する必要があります。AppleScript によるページキー送信やスクリーンショット取得にはこれらの権限が必須です。⚠️

- 画像比較の閾値や最大ページ数は `kindle_screenshot.py` の `compare_images()` および `screenshot_count` のロジックで調整可能です。

- `pytesseract` を使う場合は先に Tesseract バイナリをインストールしておいてください（`brew install tesseract`）。

---

## 🛠 補足: スクリプト一覧

- `kindle_screenshot.py` : メインのスクリーンショット撮影 & ページめくり → 最後に `convert_to_pdf` を呼ぶ
- `screenshot2pdf.py` : 画像フォルダから PDF を生成（分割ロジックあり）
- `making_booklist.py` : 本のリスト作成に関する補助スクリプト（必要に応じて確認してください）

---

## Contributing / ライセンス

必要な修正点や追加したい機能があれば Issue/PR で提案してください。

---

## よくあるコマンドまとめ

```bash
# 仮想環境を作る（初回）
python -m venv .venv

# 仮想環境を有効化してデペンデンシーを入れる
source .venv/bin/activate && pip install -r requirements.txt

# スクリーンショット実行（主コマンド）
source .venv/bin/activate && python kindle_screenshot.py

# すでに画像があるフォルダだけを PDF に変換する場合
python screenshot2pdf.py
```

---

**よくある変更点**: Kindle のバンドルIDが変わった場合や、macOS 権限設定の違いがある場合は `open_kindle()` / `focus_kindle_window()` を編集してください。

---

もしこの README に追加したい情報（例: 実行時のスクリーンショット例、`README` に載せたいスクリーンショットのサンプル、CI 設定等）があれば教えてください。