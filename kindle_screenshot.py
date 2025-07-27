import pyautogui
import time
import os
import random
import re
from datetime import datetime
from dotenv import load_dotenv
from PIL import Image
import numpy as np
import win32gui
import win32con
from screenshot2pdf import convert_to_pdf
from screenshot2audio import convert_to_audio
import pygetwindow as gw

# 環境変数の読み込み
load_dotenv()

def sanitize_folder_name(book_title):
    """書籍名を安全なフォルダ名に変換する"""
    # Windowsで使用できない文字を除去または置換
    # 使用できない文字: < > : " | ? * \ /
    invalid_chars = r'[<>:"|?*\\/]'
    
    # 使用できない文字を除去
    safe_name = re.sub(invalid_chars, '', book_title)
    
    # 先頭と末尾の空白、ドットを除去
    safe_name = safe_name.strip(' .')
    
    # 連続する空白を単一の空白に置換
    safe_name = re.sub(r'\s+', ' ', safe_name)
    
    # 空白をアンダースコアに置換（オプション）
    safe_name = safe_name.replace(' ', '_')
    
    # 空文字列の場合はデフォルト名を使用
    if not safe_name:
        safe_name = "unknown_book"
    
    # 長すぎる場合は短縮
    if len(safe_name) > 100:
        safe_name = safe_name[:100]
    
    return safe_name

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

# Kindleウィンドウを最大化
def maximize_kindle_window():
    windows = gw.getWindowsWithTitle('Kindle')
    if windows:
        win = windows[0]
        if not win.isMaximized:
            win.maximize()
            time.sleep(1)  # 最大化の反映待ち

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

def take_screenshot(safe_book_title):
    """現在表示されているページのスクリーンショットを撮影する"""
    try:
        # Kindleウィンドウにフォーカスを当てる
        if not focus_kindle_window():
            print("Kindleウィンドウが見つかりません。")
            return None
        
        # フォーカスが確実に移るまで少し待機
        time.sleep(0.5)
            
        # タイムスタンプ付きのファイル名を生成(書籍名のフォルダを作成して格納)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'screenshots_books/{safe_book_title}/kindle_page_{timestamp}.png'
        
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
        # 右矢印キーでページをめくる（最も確実な方法）
        pyautogui.press('right')
        time.sleep(1.5)  # ページ切り替えの待機時間を延長
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
        # 差分の閾値を緩和（より多くの違いを許容）
        threshold = diff / (img1_array.size * 255) * 100  # 差分の割合を計算
        return threshold < 0.1  # 0.1%以下の差分なら同じ画像とみなす
        
    except Exception as e:
        print(f"画像比較中にエラーが発生しました: {e}")
        return False

def main():    
    # Kindleを開く
    if not open_kindle():
        return

    # ここでKindleウィンドウを最大化＆フォーカス（最初だけ）
    maximize_kindle_window()
    focus_kindle_window()

    # 検索する本のタイトルを入力
    print("スクリーンショットを開始します。")
    book_title = input("検索する本のタイトルを入力してください: ")

    # スクリーンショットを保存するディレクトリを作成
    safe_book_title = sanitize_folder_name(book_title)
    print(f"フォルダ名: {safe_book_title}")
    if not os.path.exists(f'screenshots_books/{safe_book_title}'):
        os.makedirs(f'screenshots_books/{safe_book_title}')

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
    
    direction = 'right'  # 最初は右方向
    reversed_once = False
    while True:
        # スクリーンショットを撮影
        current_screenshot = take_screenshot(safe_book_title)
        if current_screenshot:
            screenshot_history.append(current_screenshot)
            screenshot_count += 1

            # 終了条件のチェック
            if screenshot_count >= 2:
                # 直近の2枚の画像を比較
                if compare_images(screenshot_history[-1], screenshot_history[-2]):
                    if not reversed_once:
                        print("同じページが検出されました。逆方向にページをめくります。")
                        os.remove(screenshot_history[-1])
                        direction = 'left'  # 方向を逆に
                        reversed_once = True
                        pyautogui.press(direction)
                        time.sleep(1.5)
                        continue  # 逆方向で再度撮影
                    else:
                        print("同じページが検出されたため、処理を終了します。")
                        os.remove(screenshot_history[-1])
                        break
            if screenshot_count >= 1000:
                print("最大撮影枚数に達しました。処理を終了します。")
                os.remove(screenshot_history[-1])
                break
            # ページをめくる前に少し待機
            time.sleep(0.5)
            # directionに従ってページをめくる
            pyautogui.press(direction)
            time.sleep(1.5)
    
    print("スクリーンショットの処理が完了しました。")
    # screenshot2pdf.pyの処理を実行しpdfに変換
    print("PDFへの変換を開始します...")
    convert_to_pdf(safe_book_title)

    # screenshot2audio.pyの処理を実行し音声に変換
    # print("音声ファイルへの変換を開始します...")
    # convert_to_audio(book_title) 
    
    print("すべての処理が完了しました。")

if __name__ == "__main__":
    main()