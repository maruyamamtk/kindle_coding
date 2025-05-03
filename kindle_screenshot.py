import pyautogui
import time
import os
from datetime import datetime
from PIL import Image
from openai import OpenAI
from dotenv import load_dotenv
from capture_icons import capture_icons
import base64
import io

# 環境変数の読み込み
load_dotenv()

def encode_image(image_path):
    """画像をbase64エンコードする"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def get_book_names():
    """Kindleのライブラリから本の名称を取得する"""
    try:
        # ライブラリ画面のスクリーンショットを撮影
        screenshot = pyautogui.screenshot()
        screenshot_path = 'book_icon.png'
        screenshot.save(screenshot_path)
        print("ライブラリ画面のスクリーンショットを保存しました")
        
        # 画像をbase64エンコード
        base64_image = encode_image(screenshot_path)
        
        # OpenAI APIを使用して画像からテキストを抽出
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "この画像はKindleのライブラリ画面です。表示されている本のタイトルを全てリストアップしてください。タイトルを抽出し、余分な情報は含めないでください。"
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=1000
        )
        
        # レスポンスから本のタイトルを抽出
        book_titles = response.choices[0].message.content.split('\n')
        book_titles = [title.strip() for title in book_titles if title.strip()]
        
        print("検出された本のタイトル:")
        for i, title in enumerate(book_titles, 1):
            print(f"{i}. {title}")
        
        return book_titles
        
    except Exception as e:
        print(f"本の名称取得中にエラーが発生しました: {e}")
        return []

def open_kindle():
    """Kindleアプリケーションを開く"""
    try:
        # Windowsの場合、スタートメニューからKindleを検索して開く
        pyautogui.press('win')
        time.sleep(1)
        
        # 英数字入力モードに切り替え
        pyautogui.press(['capslock', 'capslock'])  # CapsLockを2回押して確実に英数字モードにする
        time.sleep(0.5)
        
        # Kindleと入力（一文字ずつ確実に入力）
        for char in 'kindle':
            pyautogui.press(char)
            time.sleep(0.1)
        
        time.sleep(1)
        pyautogui.press('enter')
        time.sleep(20)  # Kindleが起動するのを待つ
        
        return True
            
    except Exception as e:
        print(f"Kindleの起動中にエラーが発生しました: {e}")
        print("Kindleアプリケーションがインストールされているか確認してください。")
        return False

def take_screenshot():
    """現在表示されているページのスクリーンショットを撮影する"""
    try:
        # スクリーンショットを保存するディレクトリを作成
        if not os.path.exists('screenshots_books'):
            os.makedirs('screenshots_books')
        
        # タイムスタンプ付きのファイル名を生成
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'screenshots_books/kindle_page_{timestamp}.png'
        
        # スクリーンショットを撮影
        screenshot = pyautogui.screenshot()
        screenshot.save(filename)
        print(f"スクリーンショットを保存しました: {filename}")
        
    except Exception as e:
        print(f"スクリーンショットの撮影中にエラーが発生しました: {e}")

def main():
    print("Kindleの自動スクリーンショット撮影を開始します...")
    
    # Kindleを開く
    if not open_kindle():
        return
    
    # 本の一覧を取得
    book_titles = get_book_names()
    
    if not book_titles:
        print("本の一覧を取得できませんでした。")
        return
    
    # 最初の本を選択（必要に応じて変更可能）
    selected_book = book_titles[0]
    print(f"選択された本: {selected_book}")
    
    # 本をクリックして開く
    try:
        # 最初の本の領域をクリック
        pyautogui.click(x=100, y=100)  # 適切な座標に調整が必要
        time.sleep(3)  # 本が開くのを待つ
    except Exception as e:
        print(f"本の選択中にエラーが発生しました: {e}")
        return
    
    # スクリーンショットを撮影
    take_screenshot()
    
    print("処理が完了しました。")

if __name__ == "__main__":
    main() 