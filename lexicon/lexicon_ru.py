bot_message = {
    "starting_bot": "Добро пожаловать в бот-магазин!",
    "starting_admin": "Добро пожаловать админ!",
    "starting_registration": "Начинается регистрация",
    "nessesary_regestration": "Для использования бота необходимо зарегестрироваться",
    "enter_name": "Введите имя",
    "enter_soname": "Введите фамилию",
    "enter_age": "Введите возраст",
    "registration_successful": "Регистрация прошла успешно",
    "error_enter_name": "Имя может содержать только кириллицу (до 50 символов)",
    "error_enter_soname": "Фамилия может содержать только кириллицу (до 50 символов)",
    "error_enter_age": "Возраст может содержать только цифры (0-100)",
    "add_categories": "Для начала работы магазина необходимо добавить категории",
    "enter_category": "Введите категории через запятую, как в примере: Овощи, фрукты, молочные изделия",
    "add_categories_successful": "Категории успешно добавлены! \n\nСправа на спрочке ввода появилась клавиатура с возможностями админа. Для успешной работы бота так же необходимо добавить баннеры. Для этого пожалуйста воспользуйтесь клавиатурой.",
    "change_category": "Выберите категорию",
    "successful_payment": "Платеж успещно завершен! Спасибо, что пользуетесь услугами нашего бота. Напишите старт, чтобы попасть на главное меню"
}


button = {
    "reg_button": {
        "Регистрация": "registration"
    },
    "main_menu": {
        "Профиль": "profile",
        "Корзина": "cart",
        "Каталог": "catalog",
        "О нас": "about",
        "Оплата": "payment"
    },
    "menu_add_product": {
        "Отмена": "cancel",
        "Назад": "back_step"
    },
    "add_categories": {
        "Добавить категории": "add_categories"
    }
}


description_for_info_pages = {
    "main": "Добро пожаловать!",
    "about": "Интернет магазин для покупки картинок.",
    "payment": "Вы можете оплатить картой в боте",
    'catalog': 'Категории:',
    'cart': 'В корзине ничего нет!',
    'profile': "Ваши данные: "
}


btns_menu_add_product = {
    "Отмена": "cancel",
    "Назад": "back_step"
}


class Format:
    def format_profile(name: str, soname: str, age: str):
        return f"Имя: {name}, \nФамилия: {soname}, \nВозраст: {age}"

    def format_product(product_name: str, description: str, price: str):
        return f"Название: {product_name} \n Описание товара: {description}, \n Цена: {price}"
