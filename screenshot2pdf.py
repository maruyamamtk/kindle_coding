from PIL import Image
import os
from dotenv import load_dotenv

# 毎回の実行前に仮想環境を有効化する
# source .venv/bin/activate
# pip install -r requirements.txt

# 環境変数の読み込み
load_dotenv()

def convert_to_pdf(book_title):
    # 入力ディレクトリ
    input_dir = f'screenshots_books/{book_title}'

    # 対象拡張子
    image_extensions = [".png", ".jpg", ".jpeg"]

    # 画像ファイルを読み込み（ファイル名でソート）
    image_files = sorted(
        [f for f in os.listdir(input_dir) if os.path.splitext(f)[1].lower() in image_extensions]
    )

    # 画像をPillowのImageオブジェクトとして読み込む
    image_list = []
    part = 1
    pdf_files = []
    for i, file in enumerate(image_files):
        img_path = os.path.join(input_dir, file)
        img = Image.open(img_path).convert("RGB")
        image_list.append(img)
        # 画像を追加して一時PDFを作成
        if len(image_list) == 1:
            continue  # 1枚目は基準画像として次へ
        temp_pdf = os.path.join(input_dir, f"_temp_{part}.pdf")
        image_list[0].save(temp_pdf, save_all=True, append_images=image_list[1:])
        # 20MBを超えたら分割
        if os.path.getsize(temp_pdf) > 20 * 1024 * 1024:
            # 直前までの画像で保存
            output_pdf = os.path.join(input_dir, f"{book_title}_part{part}.pdf")
            image_list.pop()  # 最後の画像は次のパートへ
            image_list[0].save(output_pdf, save_all=True, append_images=image_list[1:])
            pdf_files.append(output_pdf)
            print(f"{output_pdf} に保存しました。")
            # 新しいパート開始
            part += 1
            image_list = [img]  # 最後の画像から再開
        os.remove(temp_pdf)
    # 残りの画像を保存
    if image_list:
        output_pdf = os.path.join(input_dir, f"{book_title}_part{part}.pdf")
        image_list[0].save(output_pdf, save_all=True, append_images=image_list[1:])
        pdf_files.append(output_pdf)
        print(f"{output_pdf} に保存しました。")
    if not pdf_files:
        print("画像が見つかりませんでした。")

if __name__ == "__main__":
    # コマンドラインから実行された場合
    book_title = input("pdf化する本のタイトルを入力してください: ")
    convert_to_pdf(book_title)
