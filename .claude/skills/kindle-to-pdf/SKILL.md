---
name: kindle-to-pdf
description: Kindle書籍のスクリーンショットを撮影してPDFに変換する（引数: 書籍名）
---

## 概要
指定した書籍のスクリーンショットを自動撮影し、PDFに変換します。

## 引数
書籍名: `{args}`

## 手順

### ステップ1: ユーザーへの確認（必須）
以下のメッセージをユーザーに伝え、「はい」などの準備完了の返答を受け取るまで次のステップに進んではならない。

> 「**{args}** のスクリーンショット撮影を開始します。
> Kindleアプリで **{args}** の**冒頭ページ**を開いてください。
> 準備ができたら「はい」と教えてください。」

### ステップ2: スクリーンショット撮影 & PDF変換
ユーザーが準備完了を確認したら、以下のコマンドを実行する：

```bash
cd /Users/michika_maruyama/Desktop/kindle_coding && source .venv/bin/activate && echo "{args}" | python kindle_screenshot.py
```

実行中はユーザーに以下を伝えること：
- 撮影開始まで5秒のカウントダウンがあります
- 撮影中はKindleウィンドウを操作しないでください
- 撮影完了後、PDFへの変換も自動で実行されます

### 出力先
`screenshots_books/{args}/` フォルダ内にPNGとPDFが生成されます
