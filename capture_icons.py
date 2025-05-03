import pyautogui
import time

def capture_icons():
    print("本のアイコンのスクリーンショットを撮影します...")
    print("5秒後にスクリーンショットを撮影します。")
    print("その間に本のアイコンが表示されている画面に移動してください。")
    
    time.sleep(5)
    
    # 本のアイコンのスクリーンショットを撮影
    screenshot = pyautogui.screenshot()
    screenshot.save('book_icon.png')
    print("本のアイコンのスクリーンショットを保存しました: book_icon.png")

if __name__ == "__main__":
    capture_icons() 