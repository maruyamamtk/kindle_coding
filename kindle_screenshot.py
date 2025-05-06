import pyautogui
import time
import os
from datetime import datetime
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

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
        time.sleep(10)  # Kindleが起動するのを待つ
        
        return True
            
    except Exception as e:
        print(f"Kindleの起動中にエラーが発生しました: {e}")
        print("Kindleアプリケーションがインストールされているか確認してください。")
        return False

def take_screenshot(book_title):
    """現在表示されているページのスクリーンショットを撮影する"""
    try:
        # タイムスタンプ付きのファイル名を生成
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'screenshots_books/{book_title}/kindle_page_{timestamp}.png'
        
        # スクリーンショットを撮影
        screenshot = pyautogui.screenshot()
        screenshot.save(filename)
        print(f"スクリーンショットを保存しました: {filename}")
        
    except Exception as e:
        print(f"スクリーンショットの撮影中にエラーが発生しました: {e}")

### 一連の処理を実行する関数
def main():    
    # Kindleを開く
    if not open_kindle():
        return

    # 検索する本のタイトルを入力
    print("スクリーンショットを開始します。")
    book_title = input("検索する本のタイトルを入力してください: ")

    # スクリーンショットを保存するディレクトリを作成
    if not os.path.exists(f'screenshots_books/{book_title}'):
        os.makedirs(f'screenshots_books/{book_title}')

    # スクリーンショットを撮影
    take_screenshot(book_title)
    
    print("処理が完了しました。")

if __name__ == "__main__":
    main() 