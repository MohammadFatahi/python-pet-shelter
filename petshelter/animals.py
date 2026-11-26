from .exceptions import InvalidDataError


class Animal:
    species = "حیوان"

    def __init__(self, name, age, gender, breed):
        if type(age) is not int or age < 0:
            raise InvalidDataError("سن باید یک عدد صحیح نامنفی باشد.")

        self._name = name.strip()
        self.age = age
        self.gender = gender.strip()
        self.breed = breed.strip()
        if not all((self.name, self.gender, self.breed)):
            raise InvalidDataError("نام، جنسیت و نژاد حیوان را وارد کنید.")

        self._adopter = None

    @property
    def name(self):
        return self._name

    @property
    def adopted(self):
        return self._adopter is not None

    def show_info(self):
        status = "واگذار شده" if self.adopted else "قابل واگذاری"
        return (
            f"{self.name} | گونه: {self.species} | سن: {self.age} سال | "
            f"جنسیت: {self.gender} | نژاد: {self.breed} | "
            f"{status} | صدا: {self.make_sound()}"
        )

    def make_sound(self):
        return "نامشخص"


class Dog(Animal):
    species = "سگ"

    def make_sound(self):
        return "واق‌واق"


class Cat(Animal):
    species = "گربه"

    def make_sound(self):
        return "میو"


class Bird(Animal):
    species = "پرنده"

    def make_sound(self):
        return "جیک‌جیک"


class Rabbit(Animal):
    species = "خرگوش"

    def make_sound(self):
        return "خرخر آرام"
