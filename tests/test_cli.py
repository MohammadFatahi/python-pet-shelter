import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class CliTests(unittest.TestCase):
    def run_program(self, inputs):
        with TemporaryDirectory() as directory:
            result = subprocess.run(
                [sys.executable, "-B", "-m", "petshelter.main"],
                cwd=directory,
                env={**os.environ, "PYTHONPATH": str(PROJECT_ROOT)},
                input=inputs,
                text=True,
                encoding="utf-8",
                capture_output=True,
                timeout=10,
                check=True,
            )
            log = Path(directory, "shelter.log").read_text(encoding="utf-8")
        self.assertEqual(result.stderr, "")
        return result.stdout, log

    def test_full_menu_session(self):
        inputs = "\n".join([
            "۲",
            "۱", "۲", "پشمک", "۲", "ماده", "پرشین",
            "۲",
            "۳", "۱", "پشم",
            "۳", "۲", "گربه",
            "۴", "پشمک", "۰۰۱۲۳۴۵۶۷۸", "سارا", "۰۹۱۲۱۲۳۴۵۶۷",
            "۷",
            "۵", "پشمک",
            "۶",
            "۴", "پشمک", "0012345678",
            "۵", "پشمک",
            "۹", "پشمک",
            "۲", "۸", "",
        ])
        output, log = self.run_program(inputs)
        self.assertEqual(output.count("حیوانی برای نمایش وجود ندارد."), 2)
        self.assertEqual(output.count("پشمک | گونه: گربه"), 5)
        self.assertEqual(output.count("«پشمک» به سارا واگذار شد."), 2)
        self.assertIn("«پشمک» ثبت شد.", output)
        self.assertIn("«پشمک» حذف شد.", output)
        self.assertIn("واگذار شده | صدا: میو", output)
        self.assertIn("قابل واگذاری | صدا: میو", output)
        self.assertIn("خدانگهدار!", output)
        self.assertEqual(log.count("موفق | پشمک"), 6)
        self.assertNotIn("خطا:", output)
        self.assertNotIn("0012345678", log)
        self.assertNotIn("09121234567", log)

    def test_menu_recovers_from_errors(self):
        inputs = "\n".join([
            "۰",
            "۱", "۲", "پشمک", "abc",
            "۱", "۲", "پشمک", "۲", "ماده", "پرشین",
            "۳", "۵",
            "۴", "ناموجود",
            "۴", "پشمک", "123",
            "۴", "پشمک", "0012345678", "سارا", "0912aaa23451",
            "۵", "پشمک",
            "۸", "",
        ])
        output, log = self.run_program(inputs)
        for message in (
            "یک شماره از ۱ تا ۹ انتخاب کنید.",
            "سن باید یک عدد صحیح نامنفی باشد.",
            "برای جست‌وجو ۱ یا ۲ را انتخاب کنید.",
            "پیدا نشد.",
            "کد ملی باید دقیقاً ۱۰ رقم باشد.",
            "شماره موبایل باید ۱۱ رقم باشد",
            "هنوز واگذار نشده است.",
            "خدانگهدار!",
        ):
            with self.subTest(message=message):
                self.assertIn(message, output)
        self.assertIn("ناموفق | AnimalNotAdoptedError", log)

    def test_input_can_end_mid_operation(self):
        output, log = self.run_program("۱\n۴\n")
        self.assertIn("خدانگهدار!", output)
        self.assertEqual(log, "")


if __name__ == "__main__":
    unittest.main()
