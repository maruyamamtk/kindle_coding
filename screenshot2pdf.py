from PIL import Image
import os
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

# スクリーンショットの保存フォルダを指定
book_title = input("pdf化する本のタイトルを入力してください: ")
input_dir = f'screenshots_books/{book_title}'

# 出力ファイル名
output_pdf = f"screenshots_books/{book_title}/{book_title}.pdf"

# 対象拡張子
image_extensions = [".png", ".jpg", ".jpeg"]

# 画像ファイルを読み込み（ファイル名でソート）
image_files = sorted(
    [f for f in os.listdir(input_dir) if os.path.splitext(f)[1].lower() in image_extensions]
)

# 画像をPillowのImageオブジェクトとして読み込む
image_list = []
for i, file in enumerate(image_files):
    img_path = os.path.join(input_dir, file)
    img = Image.open(img_path).convert("RGB")
    image_list.append(img)

# 最初の画像を基準に、残りを追加してPDF出力
if image_list:
    first_image = image_list[0]
    rest_images = image_list[1:]
    first_image.save(output_pdf, save_all=True, append_images=rest_images)
    print(f"{output_pdf} に保存しました。")
else:
    print("画像が見つかりませんでした。")
