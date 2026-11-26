import unittest

from petshelter.animals import Bird, Cat, Dog, Rabbit
from petshelter.exceptions import (
    AnimalAlreadyAdoptedError,
    AnimalNotAdoptedError,
    AnimalNotFoundError,
    DuplicateAnimalError,
    InvalidDataError,
    MaximumAdoptionReachedError,
)
from petshelter.people import Adopter
from petshelter.shelter import Shelter


class ShelterTests(unittest.TestCase):
    def setUp(self):
        self.shelter = Shelter()
        self.cat = self.shelter.add_animal(Cat(" Pashmak ", 2, "ماده", "پرشین"))
        self.dog = self.shelter.add_animal(Dog("هاپو", 0, "نر", "میکس"))
        self.adopter = Adopter("سارا", "۰۹۱۲۱۲۳۴۵۶۷", "۰۰۱۲۳۴۵۶۷۸")

    def test_four_animal_types(self):
        for animal_type, species, sound in [
            (Dog, "سگ", "واق‌واق"),
            (Cat, "گربه", "میو"),
            (Bird, "پرنده", "جیک‌جیک"),
            (Rabbit, "خرگوش", "خرخر آرام"),
        ]:
            with self.subTest(animal_type=animal_type):
                animal = animal_type("برفی", 1, "ماده", "میکس")
                self.assertEqual(animal.species, species)
                self.assertEqual(animal.make_sound(), sound)
                self.assertIn(sound, animal.show_info())

    def test_invalid_animal_details(self):
        for name, age, gender, breed in [
            (" ", 1, "نر", "میکس"),
            ("برفی", -1, "نر", "میکس"),
            ("برفی", 1.5, "نر", "میکس"),
            ("برفی", 1, " ", "میکس"),
            ("برفی", 1, "نر", " "),
        ]:
            with self.subTest(name=name, age=age, gender=gender, breed=breed):
                with self.assertRaises(InvalidDataError):
                    Cat(name, age, gender, breed)

    def test_search_by_name_and_species(self):
        self.assertEqual(self.shelter.search_animals(" ASH "), [self.cat])
        self.assertEqual(self.shelter.search_animals("گربه", by="species"), [self.cat])
        self.assertEqual(self.shelter.search_animals(" DOG ", by="species"), [self.dog])
        self.assertEqual(self.shelter.search_animals("دیده‌نشده"), [])
        with self.assertRaises(InvalidDataError):
            self.shelter.search_animals(" ")
        with self.assertRaises(InvalidDataError):
            self.shelter.search_animals("هاپو", by="color")

    def test_duplicate_name(self):
        with self.assertRaises(DuplicateAnimalError):
            self.shelter.add_animal(Dog("pASHMAK", 1, "نر", "میکس"))
        self.assertEqual(self.shelter.show_animals(), [self.cat, self.dog])

    def test_missing_animal(self):
        for operation, args in [
            (self.shelter.adopt_animal, ("ناموجود", self.adopter)),
            (self.shelter.return_animal, ("ناموجود",)),
            (self.shelter.remove_animal, ("ناموجود",)),
        ]:
            with self.subTest(operation=operation.__name__):
                with self.assertRaises(AnimalNotFoundError):
                    operation(*args)
        self.assertIsNone(self.shelter.find_adopter(self.adopter.national_id))

    def test_adoption_and_return_update_both_sides(self):
        self.shelter.adopt_animal("pashmak", self.adopter)
        self.assertTrue(self.cat.adopted)
        self.assertEqual(self.shelter.show_animals(adopted=True), [self.cat])
        self.assertEqual(self.shelter.show_animals(adopted=False), [self.dog])
        self.assertEqual(self.adopter.adopted_animals, (self.cat,))
        self.assertIs(self.shelter.find_adopter("٠٠١٢٣٤٥٦٧٨"), self.adopter)

        self.shelter.return_animal(" PASHMAK ")
        self.assertFalse(self.cat.adopted)
        self.assertEqual(self.shelter.show_animals(adopted=True), [])
        self.assertEqual(self.shelter.show_animals(adopted=False), [self.cat, self.dog])
        self.assertEqual(self.adopter.adopted_animals, ())

    def test_double_adoption_and_return(self):
        with self.assertRaises(AnimalNotAdoptedError):
            self.shelter.return_animal(self.cat.name)

        self.shelter.adopt_animal(self.cat.name, self.adopter)
        other = Adopter("رضا", "09351234567", "0023456789")
        with self.assertRaises(AnimalAlreadyAdoptedError):
            self.shelter.adopt_animal(self.cat.name, other)
        self.assertEqual(self.adopter.adopted_animals, (self.cat,))
        self.assertIsNone(self.shelter.find_adopter(other.national_id))

    def test_limit_uses_national_id_and_return_frees_a_slot(self):
        birds = [
            self.shelter.add_animal(Bird(f"پرنده {number}", 1, "نر", "قناری"))
            for number in range(10)
        ]
        for bird in birds[:9]:
            self.shelter.adopt_animal(bird.name, self.adopter)

        same_person = Adopter("سارا", "09121234567", "0012345678")
        with self.assertRaises(MaximumAdoptionReachedError):
            self.shelter.adopt_animal(birds[9].name, same_person)
        self.assertFalse(birds[9].adopted)
        self.assertEqual(len(self.adopter.adopted_animals), 9)

        self.shelter.return_animal(birds[0].name)
        self.shelter.adopt_animal(birds[9].name, same_person)
        self.assertEqual(self.adopter.adopted_animals, tuple(birds[1:]))
        self.assertEqual(same_person.adopted_animals, ())

        other = Adopter("رضا", "09351234567", "0023456789")
        self.shelter.adopt_animal(birds[0].name, other)
        self.assertEqual(other.adopted_animals, (birds[0],))

    def test_remove_available_animal_only(self):
        self.shelter.adopt_animal(self.cat.name, self.adopter)
        with self.assertRaises(AnimalAlreadyAdoptedError):
            self.shelter.remove_animal(self.cat.name)

        self.shelter.return_animal(self.cat.name)
        self.assertIs(self.shelter.remove_animal(self.cat.name), self.cat)
        self.assertEqual(self.shelter.show_animals(), [self.dog])

    def test_decorator_preserves_method_name_and_logs_result(self):
        self.assertEqual(Shelter.add_animal.__name__, "add_animal")
        with self.assertLogs("petshelter.decorators", level="INFO") as records:
            self.shelter.adopt_animal(self.cat.name, self.adopter)
            with self.assertRaises(AnimalAlreadyAdoptedError):
                self.shelter.adopt_animal(self.cat.name, self.adopter)
        self.assertEqual(len(records.output), 2)
        self.assertIn("واگذاری حیوان | موفق", records.output[0])
        self.assertIn("ناموفق | AnimalAlreadyAdoptedError", records.output[1])
        for entry in records.output:
            self.assertNotIn(self.adopter.national_id, entry)
            self.assertNotIn(self.adopter.phone, entry)


class AdopterTests(unittest.TestCase):
    def test_preserves_leading_zero_and_normalizes_digits(self):
        adopter = Adopter(" سارا ", " ۰۹۱۲۱۲۳۴۵۶۷ ", "٠٠١٢٣٤٥٦٧٨")
        self.assertEqual(adopter.name, "سارا")
        self.assertEqual(adopter.phone, "09121234567")
        self.assertEqual(adopter.national_id, "0012345678")

    def test_rejects_invalid_details(self):
        for name, phone, national_id in [
            (" ", "09121234567", "0012345678"),
            ("سارا", "0912aaa23451", "0012345678"),
            ("سارا", "02121234567", "0012345678"),
            ("سارا", "0912123456", "0012345678"),
            ("سارا", "09121234567", "001234567"),
            ("سارا", "09121234567", "00123456789"),
            ("سارا", "09121234567", "001234567a"),
        ]:
            with self.subTest(name=name, phone=phone, national_id=national_id):
                with self.assertRaises(InvalidDataError):
                    Adopter(name, phone, national_id)


if __name__ == "__main__":
    unittest.main()
