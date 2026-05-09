---
name: convert-pdf
description: 撮影済みスクリーンショットフォルダをPDFに変換する
disable-model-invocation: true
---

## PDF変換手順

ターミナルで以下のコマンドを実行してください：

```bash
cd /Users/michika_maruyama/Desktop/kindle_coding
source .venv/bin/activate
python screenshot2pdf.py
```

実行後、変換したい書籍フォルダ名を入力するよう求められます。

### 仕様
- `screenshots_books/<書籍名>/` 内の画像をPDF化
- 20MBを超える場合は `_part1`, `_part2` ... と自動分割
- 対応フォーマット: `.png`, `.jpg`, `.jpeg`
