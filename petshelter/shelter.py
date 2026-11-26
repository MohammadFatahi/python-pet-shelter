from .decorators import log_operation
from .exceptions import (
    AnimalAlreadyAdoptedError,
    AnimalNotAdoptedError,
    AnimalNotFoundError,
    DuplicateAnimalError,
    InvalidDataError,
    MaximumAdoptionReachedError,
)
from .people import Adopter


class Shelter:
    def __init__(self):
        self._animals = {}
        self._adopters = {}

    @log_operation("ثبت حیوان")
    def add_animal(self, animal):
        key = animal.name.casefold()
        if key in self._animals:
            raise DuplicateAnimalError(f"حیوانی با نام «{animal.name}» قبلاً ثبت شده است.")
        if animal.adopted:
            raise AnimalAlreadyAdoptedError("این حیوان از قبل سرپرست دارد.")
        self._animals[key] = animal
        return animal

    def get_animal(self, name):
        try:
            return self._animals[name.strip().casefold()]
        except KeyError:
            raise AnimalNotFoundError(f"حیوانی با نام «{name.strip()}» پیدا نشد.") from None

    @log_operation("حذف حیوان")
    def remove_animal(self, name):
        animal = self.get_animal(name)
        if animal.adopted:
            raise AnimalAlreadyAdoptedError("برای حذف حیوان، ابتدا بازگشتش را ثبت کنید.")
        del self._animals[animal.name.casefold()]
        return animal

    def show_animals(self, adopted=None):
        return [
            animal for animal in self._animals.values()
            if adopted is None or animal.adopted == adopted
        ]

    def search_animals(self, query, by="name"):
        query = query.strip().casefold()
        if not query:
            raise InvalidDataError("عبارت جست‌وجو را وارد کنید.")
        if by == "name":
            return [animal for animal in self._animals.values() if query in animal.name.casefold()]
        if by == "species":
            return [
                animal for animal in self._animals.values()
                if query in (animal.species.casefold(), type(animal).__name__.casefold())
            ]
        raise InvalidDataError("جست‌وجو باید بر اساس نام یا گونه باشد.")

    def find_adopter(self, national_id):
        return self._adopters.get(Adopter.validate_national_id(national_id))

    @log_operation("واگذاری حیوان")
    def adopt_animal(self, animal_name, adopter):
        animal = self.get_animal(animal_name)
        if animal.adopted:
            raise AnimalAlreadyAdoptedError(f"«{animal.name}» قبلاً واگذار شده است.")

        national_id = adopter.national_id
        adopter = self._adopters.get(national_id, adopter)
        if len(adopter.adopted_animals) >= Adopter.MAX_ANIMALS:
            raise MaximumAdoptionReachedError("هر نفر می‌تواند حداکثر ۹ حیوان را به سرپرستی بگیرد.")

        self._adopters[national_id] = adopter
        adopter._adopted_animals.append(animal)
        animal._adopter = adopter
        return animal

    @log_operation("بازگرداندن حیوان")
    def return_animal(self, name):
        animal = self.get_animal(name)
        if not animal.adopted:
            raise AnimalNotAdoptedError(f"«{animal.name}» هنوز واگذار نشده است.")

        animal._adopter._adopted_animals.remove(animal)
        animal._adopter = None
        return animal
