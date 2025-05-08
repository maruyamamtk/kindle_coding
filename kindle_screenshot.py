import pyautogui
import time
import os
import random
from datetime import datetime
from dotenv import load_dotenv
from PIL import Image
import numpy as np
import win32gui
import win32con

# 環境変数の読み込み
load_dotenv()

def get_kindle_window():
    """Kindleウィンドウのハンドルを取得する"""
    def callback(hwnd, windows):
        if win32gui.IsWindowVisible(hwnd):
            window_title = win32gui.GetWindowText(hwnd)
            if "Kindle" in window_title:
                windows.append(hwnd)
        return True
    
    windows = []
    win32gui.EnumWindows(callback, windows)
    return windows[0] if windows else None

def focus_kindle_window():
    """Kindleウィンドウにフォーカスを当てる"""
    hwnd = get_kindle_window()
    if hwnd:
        # ウィンドウを前面に持ってくる
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(hwnd)
        time.sleep(1)  # フォーカスが確実に移るまで待機
        return True
    return False

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
        # Kindleウィンドウにフォーカスを当てる
        if not focus_kindle_window():
            print("Kindleウィンドウが見つかりません。")
            return None
            
        # タイムスタンプ付きのファイル名を生成(書籍名のフォルダを作成して格納)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'screenshots_books/{book_title}/kindle_page_{timestamp}.png'
        
        # スクリーンショットを撮影
        screenshot = pyautogui.screenshot()
        screenshot.save(filename)
        print(f"スクリーンショットを保存しました: {filename}")
        
        return filename
        
    except Exception as e:
        print(f"スクリーンショットの撮影中にエラーが発生しました: {e}")
        return None

def turn_page():
    """Kindleのページをめくる"""
    try:
        # Kindleウィンドウにフォーカスを当てる
        if not focus_kindle_window():
            print("Kindleウィンドウが見つかりません。")
            return False
            
        # 右矢印キーで次のページへ
        pyautogui.press('right')
        # ランダムな待機時間（0.5秒から1.5秒）
        time.sleep(random.uniform(0.5, 1.5))
        return True
    except Exception as e:
        print(f"ページめくり中にエラーが発生しました: {e}")
        return False

def compare_images(image1_path, image2_path):
    """2つの画像が同じかどうかを比較する"""
    try:
        img1 = Image.open(image1_path)
        img2 = Image.open(image2_path)
        
        # 画像をnumpy配列に変換
        img1_array = np.array(img1)
        img2_array = np.array(img2)
        
        # 画像のサイズが異なる場合はFalseを返す
        if img1_array.shape != img2_array.shape:
            return False
            
        # 画像の差分を計算
        diff = np.sum(np.abs(img1_array - img2_array))
        # 差分が一定値以下なら同じ画像とみなす
        return diff < 5
        
    except Exception as e:
        print(f"画像比較中にエラーが発生しました: {e}")
        return False

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

    # スクリーンショットの履歴を保存
    screenshot_history = []
    screenshot_count = 0
    
    # 最初のページを表示するための待機時間
    print("最初のページを表示するまで待機します...")
    wait_time = 5
    for i in range(wait_time, 0, -1):
        print(f"残り {i} 秒...", end='\r')
        time.sleep(1)
    print("開始します！      ")  # 余分な空白で前の行を上書き
    
    while True:
        # スクリーンショットを撮影
        current_screenshot = take_screenshot(book_title)
        
        if current_screenshot:
            screenshot_history.append(current_screenshot)
            screenshot_count += 1
            
            # 終了条件のチェック
            if screenshot_count >= 2:
                # 直近の2枚の画像を比較
                if compare_images(screenshot_history[-1], screenshot_history[-2]):
                    print("同じページが検出されました。処理を終了します。")
                    # 最後の画像を削除
                    os.remove(screenshot_history[-1])
                    break
                    
            if screenshot_count >= 1000:
                print("最大撮影枚数に達しました。処理を終了します。")
                # 最後の画像を削除
                os.remove(screenshot_history[-1])
                break
            
            # ページをめくる
            if not turn_page():
                print("ページめくりに失敗しました。処理を終了します。")
                break
    
    print("スクリーンショットの処理が完了しました。")
    print("PDFへの変換を開始します...")
    
    # screenshot2pdf.pyの処理を実行
    from screenshot2pdf import convert_to_pdf
    convert_to_pdf(book_title)
    
    print("すべての処理が完了しました。")

if __name__ == "__main__":
    main() 