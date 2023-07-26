import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher.filters import state
from aiogram.types import InputFile
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

# Токен полученный у бота BotFather
TOKEN = "6630939709:AAFDowHc87fyQsP4X-f13zfxPYf-w13oBMY"


# Определяем класс состояний для FSM
class OrderStates(StatesGroup):
    choose_arcan = State()


# Инициализируем бота и диспетчер
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)

# Список аркан
arcans_list = [
    {
        "name": "Shadow Fiend arcana",
        "price": 700,
        "description": "При покупке данного товара вы получите на свой аккаунт аркану",
        "photo": "https://e0.pxfuel.com/wallpapers/905/14/desktop-wallpaper-shadow-fiend-dota-2-arcana-dota-2-shadow-fiend.jpg"
    },
    {
        "name": "Crystal Maiden",
        "price": 700,
        "description": "При покупке данного товара вы получите на свой аккаунт аркану",
        "photo": "https://e0.pxfuel.com/wallpapers/184/352/desktop-wallpaper-crystal-maiden-dota-crystal-maiden-thumbnail.jpg"
    },
    {
        "name": "Monkey King",
        "price": 700,
        "description": "При покупке данного товара вы получите на свой аккаунт аркану",
        "photo": "https://hawk.live/storage/post-images/great-sages-reckoning-third-style-2316.png"
    },
]


# Обработчик команды /start
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    user = message.from_user
    await message.reply(f"Привет, {user.first_name}! Добро пожаловать в магазин аркан из Dota 2. Чтобы узнать, что у нас есть, используй команду /arcanas.")


# Обработчик команды /arcanas
@dp.message_handler(commands=['arcanas'])
async def arcanas(message: types.Message):
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    for arcan in arcans_list:
        keyboard.add(types.InlineKeyboardButton(text=arcan["name"], callback_data=arcan["name"]))

    await message.reply("Доступные арканы:", reply_markup=keyboard)


# Определяем класс состояний для FSM
class OrderStates(StatesGroup):
    choose_arcan = State()


# Обработчик команды /pay
@dp.message_handler(commands=["pay"], state=OrderStates.choose_arcan)
async def pay_arcan(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        chosen_arcan = data.get("chosen_arcan")

    if chosen_arcan:
        # Создаем платежное сообщение с определенной суммой и валютой
        await bot.send_invoice(
            chat_id=message.chat.id,
            title=chosen_arcan["name"],
            description=chosen_arcan["description"],
            payload='custom_payload',
            provider_token="1744374395:TEST:fe45e0ad1fd8aa01b6b9",
            currency='UAH',
            prices=[types.LabeledPrice(label='Arkan', amount=chosen_arcan['price'] * 100)],
            start_parameter='test_payment'
        )
    else:
        await message.answer("Пожалуйста, выберите аркану с помощью команды /arcanas")

    # Сбрасываем состояние FSM
    await state.finish()


@dp.message_handler(content_types=types.ContentType.SUCCESSFUL_PAYMENT, state=OrderStates.choose_arcan)
async def process_successful_payment(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        chosen_arcan = data.get("chosen_arcan")

    if chosen_arcan:
        await message.answer(f"Вы успешно оплатили аркану: {chosen_arcan['name']} за {chosen_arcan['price']} грн.")
    else:
        await message.answer("Пожалуйста, выберите аркану с помощью команды /arcanas")

        await state.finish()


# Обработчик выбора арканы
@dp.callback_query_handler(lambda callback_query: True)
async def process_arcan(callback_query: types.CallbackQuery):
    arcan_name = callback_query.data
    arcan = next((arkan for arkan in arcans_list if arkan["name"] == arcan_name), None)

    if arcan:
        async with state.proxy() as data:
            data["chosen_arcan"] = arcan


        arkan_photo = arcan["photo"]
        arkan_description = arcan["description"]
        await bot.send_photo(callback_query.from_user.id, photo=InputFile(arkan_photo), caption=f"{arkan_description}\n\nЦена: {arcan['price']} грн.\n\nДля оплаты введите команду /pay")
        await callback_query.answer(f"Вы выбрали аркан: {arcan['name']}")
        await OrderStates.choose_arcan.set()  # Переходим в состояние выбора оплаты
    else:
        await callback_query.answer("Упс, произошла ошибка. Пожалуйста, попробуйте еще раз.")



def main():
    dp.middleware.setup(LoggingMiddleware())

    executor.start_polling(dp, skip_updates=True)





if __name__ == '__main__':
    main()

