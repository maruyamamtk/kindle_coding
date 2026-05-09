---
name: run-screenshot
description: 仮想環境を有効化してKindleスクリーンショットを実行する
disable-model-invocation: true
---

## Kindleスクリーンショット実行手順

ターミナルで以下のコマンドを実行してください：

```bash
cd /Users/michika_maruyama/Desktop/kindle_coding
source .venv/bin/activate
python kindle_screenshot.py
```

### 事前確認
- Kindleアプリが起動しているか確認
- スクリーンショットを保存したい本を開いておく
- 実行後5秒以内に最初のページを表示しておく

### 出力先
`screenshots_books/<書籍名>/` フォルダにPNGとPDFが生成されます
