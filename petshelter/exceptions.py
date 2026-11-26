class ShelterError(Exception):
    """خطاهایی که می‌شود در منوی برنامه به کاربر نشان داد."""


class InvalidDataError(ShelterError):
    pass


class AnimalNotFoundError(ShelterError):
    pass


class DuplicateAnimalError(ShelterError):
    pass


class AnimalAlreadyAdoptedError(ShelterError):
    pass


class AnimalNotAdoptedError(ShelterError):
    pass


class MaximumAdoptionReachedError(ShelterError):
    pass
