import pytesseract
import os
from PIL import Image
import asyncio
from edge_tts import Communicate

# Tesseractのパスを指定
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# 言語データのパスを設定
os.environ['TESSDATA_PREFIX'] = r'C:\Program Files\Tesseract-OCR\tessdata'

# 非同期で音声合成を実行する関数
async def text_to_speech(text, voice, output_file):
    communicate = Communicate(text=text, voice=voice)
    await communicate.save(output_file)

# 画像を音声に変換する関数
def convert_to_audio(book_title):
    try:
        ###################################
        # 画像の読み込みを実施
        ###################################
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
        for i, file in enumerate(image_files):
            img_path = os.path.join(input_dir, file)
            img = Image.open(img_path).convert("RGB")
            image_list.append(img)
        
        ###################################
        # OCRでテキストを抽出
        ###################################
        text = ''
        for i, image in enumerate(image_list):
            print(f'ページ {i+1} のテキストを抽出中...')
            # 画像の前処理（必要に応じて）
            # image = image.convert('L')  # グレースケール変換
            # image = ImageEnhance.Contrast(image).enhance(2.0)  # コントラスト強調
            
            # OCRでテキスト抽出
            page_text = pytesseract.image_to_string(image, lang='jpn')
            text += page_text + '\n'
        
        print(f'抽出されたテキストの長さ: {len(text)} 文字')
        print(text[:100])
        
        if not text.strip():
            raise ValueError("PDFからテキストを抽出できませんでした。PDFが正しく読み込めているか確認してください。")

        
        ###################################
        # テキストを音声に変換
        ###################################
        voice = "ja-JP-NanamiNeural"
        output_file = f'screenshots_books/{book_title}/audiobook_{book_title}.mp3'
        asyncio.run(text_to_speech(text, voice, output_file))
        
        # ファイルサイズの確認
        if os.path.exists(output_file):
            file_size = os.path.getsize(output_file)
            print(f'生成された音声ファイルのサイズ: {file_size} バイト')
            if file_size < 1000:  # 1KB未満の場合は警告
                print('警告: 生成されたファイルが小さすぎます。音声が正しく生成されていない可能性があります。')
        else:
            print('エラー: 音声ファイルが生成されませんでした。')
            
    except Exception as e:
        print(f'エラーが発生しました: {str(e)}')
        raise

if __name__ == "__main__":
    # コマンドラインから実行された場合
    book_title = input("音声化する本のタイトルを入力してください: ")
    convert_to_audio(book_title)
