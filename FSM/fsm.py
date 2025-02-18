from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage


storage = MemoryStorage()


class AddCategoryFSM(StatesGroup):
    category = State()


class RegistrationFSM(StatesGroup):
    name = State()
    soname = State()
    age = State()


class AddProductFSM(StatesGroup):
    name = State()
    description = State()
    category = State()
    price = State()
    image = State()

    product_for_change = None

    texts = {
        "AddProductFSM:name": "Введите название заново:",
        "AddProductFSM:description": "Введите описание заново:",
        "AddProductFSM:category": "Выберите категорию  заново ⬆️",
        "AddProductFSM:price": "Введите стоимость заново:",
        "AddProductFSM:image": "Этот стейт последний, поэтому...",
    }


class AddBannerFSM(StatesGroup):
    image = State()
