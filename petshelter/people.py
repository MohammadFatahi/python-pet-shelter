import re

from .exceptions import InvalidDataError


DIGIT_TRANSLATION = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")


class Adopter:
    MAX_ANIMALS = 9

    def __init__(self, name, phone, national_id):
        self.name = name.strip()
        if not self.name:
            raise InvalidDataError("نام سرپرست را وارد کنید.")

        self.phone = self.validate_phone(phone)
        self._national_id = self.validate_national_id(national_id)
        self._adopted_animals = []

    @property
    def national_id(self):
        return self._national_id

    @property
    def adopted_animals(self):
        return tuple(self._adopted_animals)

    @staticmethod
    def validate_phone(phone):
        phone = phone.strip().translate(DIGIT_TRANSLATION)
        if not re.fullmatch(r"09[0-9]{9}", phone):
            raise InvalidDataError("شماره موبایل باید ۱۱ رقم باشد و با ۰۹ شروع شود.")
        return phone

    @staticmethod
    def validate_national_id(national_id):
        national_id = national_id.strip().translate(DIGIT_TRANSLATION)
        if not re.fullmatch(r"[0-9]{10}", national_id):
            raise InvalidDataError("کد ملی باید دقیقاً ۱۰ رقم باشد.")
        return national_id
