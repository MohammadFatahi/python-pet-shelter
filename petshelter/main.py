import logging
import sys

from .animals import Bird, Cat, Dog, Rabbit
from .exceptions import AnimalAlreadyAdoptedError, InvalidDataError, ShelterError
from .people import Adopter, DIGIT_TRANSLATION
from .shelter import Shelter


ANIMAL_TYPES = {"1": Dog, "2": Cat, "3": Bird, "4": Rabbit}

MENU = """
پناهگاه حیوانات
۱. ثبت حیوان
۲. نمایش همهٔ حیوانات
۳. جست‌وجوی حیوان
۴. واگذاری حیوان
۵. بازگرداندن حیوان
۶. نمایش حیوانات قابل واگذاری
۷. نمایش حیوانات واگذارشده
۸. خروج
۹. حذف حیوان
"""


def read_option(prompt):
    return input(prompt).strip().translate(DIGIT_TRANSLATION)


def add_animal(shelter):
    choice = read_option("گونه (۱. سگ، ۲. گربه، ۳. پرنده، ۴. خرگوش): ")
    animal_type = ANIMAL_TYPES.get(choice)
    if animal_type is None:
        raise InvalidDataError("شمارهٔ گونه را از ۱ تا ۴ انتخاب کنید.")

    name = input("نام حیوان: ")
    try:
        age = int(input("سن به سال: "))
    except ValueError:
        raise InvalidDataError("سن باید یک عدد صحیح نامنفی باشد.") from None
    gender = input("جنسیت: ")
    breed = input("نژاد: ")

    animal = shelter.add_animal(animal_type(name, age, gender, breed))
    print(f"«{animal.name}» ثبت شد.")


def print_animals(animals):
    if not animals:
        print("حیوانی برای نمایش وجود ندارد.")
        return

    for animal in animals:
        print(animal.show_info())


def search_animals(shelter):
    choice = read_option("جست‌وجو بر اساس (۱. نام، ۲. گونه): ")
    fields = {"1": "name", "2": "species"}
    if choice not in fields:
        raise InvalidDataError("برای جست‌وجو ۱ یا ۲ را انتخاب کنید.")

    query = input("عبارت جست‌وجو: ")
    print_animals(shelter.search_animals(query, by=fields[choice]))


def adopt_animal(shelter):
    animal = shelter.get_animal(input("نام حیوان: "))
    if animal.adopted:
        raise AnimalAlreadyAdoptedError(f"«{animal.name}» قبلاً واگذار شده است.")

    national_id = input("کد ملی سرپرست: ")
    adopter = shelter.find_adopter(national_id)
    if adopter is None:
        name = input("نام سرپرست: ")
        phone = input("شماره موبایل: ")
        adopter = Adopter(name, phone, national_id)

    shelter.adopt_animal(animal.name, adopter)
    print(f"«{animal.name}» به {adopter.name} واگذار شد.")


def return_animal(shelter):
    animal = shelter.return_animal(input("نام حیوان: "))
    print(f"«{animal.name}» به پناهگاه برگشت.")


def remove_animal(shelter):
    animal = shelter.remove_animal(input("نام حیوان: "))
    print(f"«{animal.name}» حذف شد.")


def main():
    shelter = Shelter()
    while True:
        print(MENU)
        try:
            choice = read_option("شمارهٔ گزینه: ")
            if choice == "1":
                add_animal(shelter)
            elif choice == "2":
                print_animals(shelter.show_animals())
            elif choice == "3":
                search_animals(shelter)
            elif choice == "4":
                adopt_animal(shelter)
            elif choice == "5":
                return_animal(shelter)
            elif choice == "6":
                print_animals(shelter.show_animals(adopted=False))
            elif choice == "7":
                print_animals(shelter.show_animals(adopted=True))
            elif choice == "8":
                print("خدانگهدار!")
                break
            elif choice == "9":
                remove_animal(shelter)
            else:
                print("یک شماره از ۱ تا ۹ انتخاب کنید.")
        except ShelterError as error:
            print(f"خطا: {error}")
        except (EOFError, KeyboardInterrupt):
            print("\nخدانگهدار!")
            break


if __name__ == "__main__":
    for stream in (sys.stdin, sys.stdout, sys.stderr):
        stream.reconfigure(encoding="utf-8", errors=stream.errors)

    try:
        logging.basicConfig(
            filename="shelter.log",
            encoding="utf-8",
            level=logging.INFO,
            format="%(asctime)s | %(message)s",
        )
    except OSError:
        print("فایل گزارش در این پوشه باز نشد. گزارش در ترمینال نمایش داده می‌شود.", file=sys.stderr)
        logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(message)s")
    main()
