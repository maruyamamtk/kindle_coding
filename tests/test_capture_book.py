"""capture_book() の単体テスト。

Kindle には一切キー操作を送らない。pyautogui.screenshot・osascript（subprocess.run）・
time.sleep・datetime をモックし、仮想の本（ページごとに色の違う画像）で撮影ループを動かす。

実行: python -m unittest discover -s tests -v
"""
import io
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import kindle_screenshot as ks  # noqa: E402
import screenshot2pdf  # noqa: E402

RIGHT_KEY = "key code 124"
LEFT_KEY = "key code 123"


class FakeKindle:
    """ページ位置を持つ仮想の Kindle。

    forward_key で「次のページへ進むキー」を指定する（右開きの本なら LEFT_KEY）。
    端ではそれ以上めくれず、同じページが表示され続ける。
    """

    def __init__(self, num_pages, forward_key=RIGHT_KEY):
        self.num_pages = num_pages
        self.forward_key = forward_key
        self.pos = 0
        self.key_presses = []
        self.screenshot_count = 0

    def screenshot(self):
        self.screenshot_count += 1
        # ページ番号を色にエンコードした小さな画像
        return Image.new("RGB", (4, 4), (self.pos % 256, (self.pos // 256) * 50, 30))

    def run(self, args, *a, **kw):
        script = args[-1] if isinstance(args, (list, tuple)) else str(args)
        for key in (RIGHT_KEY, LEFT_KEY):
            if key in script:
                self.key_presses.append(key)
                step = 1 if key == self.forward_key else -1
                self.pos = min(max(self.pos + step, 0), self.num_pages - 1)
        return mock.Mock(returncode=0, stdout="", stderr="")


class FakeNow:
    def __init__(self, n):
        self.n = n

    def strftime(self, fmt):
        return f"20260101_{self.n:06d}"


class FakeDatetime:
    """ファイル名が衝突しないよう、呼ぶたびに1秒進む datetime"""

    counter = 0

    @classmethod
    def now(cls):
        cls.counter += 1
        return FakeNow(cls.counter)


class CaptureBookTestBase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        FakeDatetime.counter = 0
        self.stdout = io.StringIO()

    def tearDown(self):
        self.tmp.cleanup()

    def run_capture(self, kindle, **kwargs):
        kwargs.setdefault("output_root", self.root)
        with mock.patch.object(ks.pyautogui, "screenshot", side_effect=kindle.screenshot), \
                mock.patch.object(ks.subprocess, "run", side_effect=kindle.run), \
                mock.patch.object(ks.time, "sleep") as sleep, \
                mock.patch.object(ks, "datetime", FakeDatetime), \
                mock.patch("sys.stdout", self.stdout):
            result = ks.capture_book("テスト 本", **kwargs)
        self.sleep = sleep
        return result

    def pngs(self, book_dir):
        return sorted(p.name for p in Path(book_dir).glob("*.png"))

    def pdfs(self, book_dir):
        return sorted(p.name for p in Path(book_dir).glob("*.pdf"))


class TestCaptureLoop(CaptureBookTestBase):
    def test_ends_on_same_page_and_removes_duplicate(self):
        kindle = FakeKindle(12)
        pages = []
        book_dir = self.run_capture(kindle, on_page=pages.append)

        self.assertEqual(book_dir, self.root / "テスト_本")
        # 12ページ + 最後の重複1枚を撮影し、重複は削除される
        self.assertEqual(kindle.screenshot_count, 13)
        self.assertEqual(len(self.pngs(book_dir)), 12)
        # on_page は残った画像ごとに1回、残った画像そのものを渡す
        self.assertEqual(len(pages), 12)
        self.assertTrue(all(isinstance(p, Path) and p.exists() for p in pages))
        self.assertEqual(sorted(p.name for p in pages), self.pngs(book_dir))
        # 方向反転は起きない
        self.assertEqual(set(kindle.key_presses), {RIGHT_KEY})
        # PDF が作られる
        self.assertEqual(self.pdfs(book_dir), ["テスト_本_part1.pdf"])
        # 開始前の待機（start_delay=5 → sleep(1) を5回）
        self.assertEqual(self.sleep.call_args_list[:5], [mock.call(1)] * 5)

    def test_reverses_direction_when_first_pages_are_same(self):
        # 右矢印で戻る本（冒頭で右に押しても同じページのまま）
        kindle = FakeKindle(12, forward_key=LEFT_KEY)
        pages = []
        book_dir = self.run_capture(kindle, on_page=pages.append)

        # 1枚目と同じ2枚目は削除され、以降は左方向にめくる
        self.assertEqual(kindle.key_presses[0], RIGHT_KEY)
        self.assertEqual(kindle.key_presses[1], LEFT_KEY)
        self.assertEqual(set(kindle.key_presses[1:]), {LEFT_KEY})
        # 撮影: p0, p0(重複・削除), p1..p11, p11(重複・削除) = 14枚
        self.assertEqual(kindle.screenshot_count, 14)
        self.assertEqual(len(self.pngs(book_dir)), 12)
        self.assertEqual(len(pages), 12)
        self.assertTrue(all(p.exists() for p in pages))

    def test_should_stop_ends_loop_and_makes_pdf(self):
        kindle = FakeKindle(50)
        pages = []
        book_dir = self.run_capture(
            kindle, on_page=pages.append, should_stop=lambda: len(pages) >= 3)

        self.assertEqual(len(pages), 3)
        self.assertEqual(len(self.pngs(book_dir)), 3)
        self.assertEqual(kindle.screenshot_count, 3)
        # 止めた後はページをめくらない（2回めくって3ページ目で停止）
        self.assertEqual(len(kindle.key_presses), 2)
        self.assertEqual(self.pdfs(book_dir), ["テスト_本_part1.pdf"])

    def test_should_stop_true_from_start(self):
        kindle = FakeKindle(5)
        book_dir = self.run_capture(kindle, should_stop=lambda: True, make_pdf=False)
        self.assertEqual(kindle.screenshot_count, 0)
        self.assertEqual(kindle.key_presses, [])
        self.assertTrue(book_dir.is_dir())

    def test_make_pdf_false_does_not_create_pdf(self):
        kindle = FakeKindle(12)
        with mock.patch.object(ks, "convert_to_pdf") as convert:
            book_dir = self.run_capture(kindle, make_pdf=False)
        convert.assert_not_called()
        self.assertEqual(self.pdfs(book_dir), [])
        self.assertEqual(len(self.pngs(book_dir)), 12)

    def test_start_delay(self):
        kindle = FakeKindle(12)
        self.run_capture(kindle, start_delay=0, make_pdf=False)
        ones_without_delay = self.sleep.call_args_list.count(mock.call(1))
        FakeDatetime.counter = 0
        self.run_capture(FakeKindle(12), output_root=self.root / "x", start_delay=3, make_pdf=False)
        # 待機秒数ぶんだけ sleep(1) が増える
        self.assertEqual(self.sleep.call_args_list.count(mock.call(1)), ones_without_delay + 3)

    def test_max_5000_pages(self):
        kindle = FakeKindle(6000)
        pages = []
        book_dir = self.run_capture(kindle, on_page=pages.append, make_pdf=False)
        self.assertEqual(kindle.screenshot_count, 5000)
        # 5000枚目は削除され、on_page も呼ばれない
        self.assertEqual(len(self.pngs(book_dir)), 4999)
        self.assertEqual(len(pages), 4999)


class TestOutputRoot(CaptureBookTestBase):
    def test_default_root_is_next_to_script(self):
        script_dir = Path(ks.__file__).resolve().parent
        self.assertEqual(screenshot2pdf.resolve_output_root(), script_dir / "screenshots_books")
        self.assertEqual(screenshot2pdf.resolve_output_root("screenshots_books"),
                         script_dir / "screenshots_books")

    def test_absolute_root_is_kept(self):
        self.assertEqual(screenshot2pdf.resolve_output_root(self.root), self.root)

    def test_relative_root_ignores_cwd(self):
        base = self.root / "base"
        other = self.root / "other"
        base.mkdir()
        other.mkdir()
        cwd = os.getcwd()
        os.chdir(other)
        try:
            with mock.patch.object(screenshot2pdf, "BASE_DIR", base):
                book_dir = self.run_capture(FakeKindle(12), output_root="rel")
        finally:
            os.chdir(cwd)
        self.assertEqual(book_dir, base / "rel" / "テスト_本")
        self.assertEqual(len(self.pngs(book_dir)), 12)
        self.assertEqual(self.pdfs(book_dir), ["テスト_本_part1.pdf"])
        self.assertEqual(list(other.iterdir()), [])

    def test_convert_to_pdf_keeps_positional_call(self):
        book = self.root / "screenshots_books" / "本"
        book.mkdir(parents=True)
        Image.new("RGB", (4, 4), (1, 2, 3)).save(book / "a.png")
        with mock.patch.object(screenshot2pdf, "BASE_DIR", self.root), \
                mock.patch("sys.stdout", self.stdout):
            screenshot2pdf.convert_to_pdf("本")
        self.assertTrue((book / "本_part1.pdf").exists())


class TestMain(unittest.TestCase):
    def test_main_reads_title_from_stdin(self):
        # echo "書名" | python kindle_screenshot.py 相当
        with mock.patch.object(ks, "open_kindle", return_value=True) as open_kindle, \
                mock.patch.object(ks, "maximize_kindle_window"), \
                mock.patch.object(ks, "focus_kindle_window"), \
                mock.patch.object(ks, "capture_book") as capture, \
                mock.patch("sys.stdin", io.StringIO("テスト 本\n")), \
                mock.patch("sys.stdout", io.StringIO()):
            ks.main()
        open_kindle.assert_called_once()
        capture.assert_called_once_with("テスト 本")

    def test_main_stops_if_kindle_not_opened(self):
        with mock.patch.object(ks, "open_kindle", return_value=False), \
                mock.patch.object(ks, "capture_book") as capture, \
                mock.patch("builtins.input") as inp:
            ks.main()
        inp.assert_not_called()
        capture.assert_not_called()


if __name__ == "__main__":
    unittest.main()
