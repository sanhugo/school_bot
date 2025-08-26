from aiogram import F, Router
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import CommandStart, Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from app.models import User, Order, Admin, fn
import app.keyboards as kb
import datetime
import calendar
import os
import time
from app.excel import create_report
import app.regex as reg

router = Router()

import os

# Получаем все файлы в папке с отчетами 
def get_subdirectories(directory):
    return [name for name in os.listdir(directory) if os.path.isfile(os.path.join(directory, name))]


# Состояния регистрации
class Register(StatesGroup):
    first_name = State()
    second_name = State()
    last_name = State()
    phone = State()

# Состояния создания заявки
class Creater(StatesGroup):
    title = State()
    discription = State()
    office_number = State()

# Состояния обновления данных пользователя
class Updater(StatesGroup):
    first_name = State()
    second_name = State()
    last_name = State()
    phone = State()

# Состояния истории заявок
class History(StatesGroup):
    history_category = State()
    history = State()
    order = State()
    changes = State()

# Состояния панели администратора
class Panel(StatesGroup):
    # level 1
    changes = State()
    # level 2
    users = State()
    new_orders = State()
    current_orders = State()
    completed_orders = State()
    excel = State()
    excel_month = State()
    excel_reports = State()
    report = State()
    # level 3
    new_to_current = State()
    current_to_completed = State()
    # level 4
    set_user = State()

@router.message(CommandStart())
async def cmd_start(message: Message): 
    if User.get_or_none(User.tg_id == message.from_user.id) == None:
        await message.answer('Вы не зарегистрированы. Необходима регистрация', reply_markup=kb.start_reg())
    else:
        await message.answer('Бот для создания заявок', reply_markup=kb.main())



# Регистрация
@router.message(F.text == 'Регистрация')
async def registration(message: Message, state: FSMContext):
    if User.get_or_none(User.tg_id == message.from_user.id) == None:
        await state.set_state(Register.first_name)
        await message.answer('Введите ваше имя', reply_markup=kb.registration())
    else:
        await message.answer('Вы уже зарегистрированы')

@router.message(Register.first_name)
async def register_name(message: Message, state: FSMContext):
    if message.text == 'Отменить' or message.text == 'Назад':
        await state.clear()
        await message.answer('Регистрация отменена', reply_markup=kb.start_reg())
    elif len(message.text) > 3:
        await state.update_data(first_name=message.text)
        await state.set_state(Register.second_name)
        await message.answer('Введите ваше отчество', reply_markup=kb.registration())
    else:
        await state.set_state(Register.first_name)
        await message.answer('Слишком короткое имя. Введите имя заново', reply_markup=kb.registration())

@router.message(Register.second_name)
async def register_name(message: Message, state: FSMContext):
    if message.text == 'Отменить':
        await state.clear()
        await message.answer('Регистрация отменена', reply_markup=kb.start_reg())
    elif message.text == 'Назад':
        await state.set_state(Register.first_name)
        await message.answer('Введите ваше имя', reply_markup=kb.registration())
    elif len(message.text) > 3:
        await state.update_data(second_name=message.text)
        await state.set_state(Register.last_name)
        await message.answer('Введите вашу фамилию', reply_markup=kb.registration())
    else:
        await state.set_state(Register.second_name)
        await message.answer('Слишком короткое отчество. Введите отчество заново', reply_markup=kb.registration())

@router.message(Register.last_name)
async def register_name(message: Message, state: FSMContext):
    if message.text == 'Отменить':
        await state.clear()
        await message.answer('Регистрация отменена', reply_markup=kb.start_reg())
    elif message.text == 'Назад':
        await state.set_state(Register.second_name)
        await message.answer('Введите ваше отчество', reply_markup=kb.registration())
    elif len(message.text) > 3:
        await state.update_data(last_name=message.text)
        await state.set_state(Register.phone)
        await message.answer('Введите номер телефона начиная с формате +7', reply_markup=kb.registration())
    else:
        await state.set_state(Register.last_name)
        await message.answer('Слишком короткая фамилия. Введите фамилию заново', reply_markup=kb.registration())

@router.message(Register.phone)
async def register_name(message: Message, state: FSMContext):
    if message.text == 'Отменить':
        await state.clear()
        await message.answer('Регистрация отменена', reply_markup=kb.start_reg())
    elif message.text == 'Назад':
        await state.set_state(Register.last_name)
        await message.answer('Введите вашу фамилию', reply_markup=kb.registration())
    elif reg.validate_num(message.text):
        await state.update_data(phone=message.text)
        data = await state.get_data()
        try:
            user = User.create(
                first_name = data['first_name'],
                second_name = data['second_name'],
                last_name = data['last_name'],
                phone_number = data['phone'],
                tg_id = message.from_user.id
            )
            user.save()
            await state.clear()
            await message.answer('Вы были успешно зарегистрированы', reply_markup=kb.main())
        except Exception as e:
            print(e)
            await message.answer('Что-то пошло не так... Устраняем неполадки')
    else:
        await state.set_state(Register.phone)
        await message.answer('Неверно указан номер телефона. Введите номер телефона начиная с +7', reply_markup=kb.registration())



# Создание заявки
@router.message(F.text == 'Создать заявку')
async def create_order(message: Message, state: FSMContext):
    user = User.get_or_none(User.tg_id == message.from_user.id)
    if user != None and not user.banned:
        await state.set_state(Creater.title)
        await message.answer('Введите тему заявки', reply_markup=kb.create_order())
    elif user.banned:
         await message.answer('Создание заявки недоступно, т.к. вы были заблокированы администратором')
    else:
        await message.answer('Вы не можете использовать данную функцию. Необходима регистрация', reply_markup=kb.start_reg())

@router.message(Creater.title)
async def create_order_title(message: Message, state: FSMContext):
    if message.text == 'Назад' or message.text == 'Отменить':
        await state.clear()
        await message.answer('Процесс создания заявки был отменен', reply_markup=kb.main())
    elif len(message.text) > 5:
        await state.update_data(title=message.text)
        await state.set_state(Creater.discription)
        await message.answer('Введите описание заявки', reply_markup=kb.create_order())
    else:
        await state.set_state(Creater.title)
        await message.answer('Слишком коротко. Напишите тему более развернуто', reply_markup=kb.create_order())

@router.message(Creater.discription)
async def create_order_discription(message: Message, state: FSMContext):
    if message.text == 'Отменить':
        await state.clear()
        await message.answer('Процесс создания заявки был отменен', reply_markup=kb.main())
    elif message.text == 'Назад':
        await state.set_state(Creater.title)
        await message.answer('Введите тему заявки', reply_markup=kb.create_order())
    elif len(message.text) > 5:
        await state.update_data(discription=message.text)
        await state.set_state(Creater.office_number)
        await message.answer('Введите номер кабинета', reply_markup=kb.create_order())
    else:
        await state.set_state(Creater.discription)
        await message.answer('Слишком коротко. Напишите более развернутое описание', reply_markup=kb.create_order())

@router.message(Creater.office_number)
async def create_order_office(message: Message, state: FSMContext):
    if message.text == 'Отменить':
        await state.clear()
        await message.answer('Процесс создания заявки был отменен', reply_markup=kb.main())
    elif message.text == 'Назад':
        await state.set_state(Creater.discription)
        await message.answer('Введите описание заявки', reply_markup=kb.create_order())
    elif reg.validate_class(message.text.strip())==False:
        await state.set_state(Creater.office_number)
        await message.answer('Неверный номер кабинета. Введите трехзначный номер кабинета', reply_markup=kb.create_order()) 
    else:
        await state.update_data(office_number=message.text)
        data = await state.get_data()
        try:
            user = User.get_or_none(User.tg_id == message.from_user.id)
            if user != None:
                order = Order.create(
                    title = data['title'],
                    discription = data['discription'],
                    office_number = data['office_number'],
                    status = 'Получена',
                    date = datetime.date.today().isoformat(),
                    author = user.id
                )
                order.save()
                await state.clear()
                await message.answer('Заявка создана успешно. Ожидайте ответа', reply_markup=kb.main())
        except Exception as e:
            print(e)
            await state.clear()
            await message.answer('Не удалось создать заявку... Устраняем неполадки', reply_markup=kb.main())


# Обновление данных пользователя
@router.message(F.text == 'Изменить данные')
async def update_user_data(message: Message, state: FSMContext):
    user = User.get_or_none(User.tg_id == message.from_user.id)
    if user != None and not user.banned:
        await state.set_state(Updater.first_name)
        await message.answer('Введите ваше имя', reply_markup=kb.update_data_start())
    elif user.banned:
        await message.answer('Обновление данных недоступно, т.к. вы были заблокированы администратором')
    else:
        await message.answer('Вы не можете использовать данную функцию. Необходима регистрация', reply_markup=kb.start_reg())

@router.message(Updater.first_name)
async def update_first_name(message: Message, state: FSMContext):
    if message.text == 'Отменить':
        await state.clear()
        await message.answer('Процесс изменения данных был отменен', reply_markup=kb.main())
    elif len(message.text) > 3:
        await state.update_data(first_name=message.text)
        await state.set_state(Updater.second_name)
        await message.answer('Введите отчество', reply_markup=kb.update_data())
    else:
        await state.set_state(Updater.first_name)
        await message.answer('Слишком короткое имя. Введите имя заново', reply_markup=kb.update_data())

@router.message(Updater.second_name)
async def update_second_name(message: Message, state: FSMContext):
    if message.text == 'Отменить':
        await state.clear()
        await message.answer('Процесс изменения данных был отменен', reply_markup=kb.main())
    elif message.text == 'Назад':
        await state.set_state(Updater.first_name)
        await message.answer('Введите ваше имя', reply_markup=kb.update_data_start())
    elif len(message.text) > 3:
        await state.update_data(second_name=message.text)
        await state.set_state(Updater.last_name)
        await message.answer('Введите вашу фамилию', reply_markup=kb.update_data())
    else:
        await state.set_state(Updater.first_name)
        await message.answer('Слишком короткое отчество. Введите отчество заново', reply_markup=kb.update_data())

@router.message(Updater.last_name)
async def update_last_name(message: Message, state: FSMContext):
    if message.text == 'Отменить':
        await state.clear()
        await message.answer('Процесс изменения данных был отменен', reply_markup=kb.main())
    elif message.text == 'Назад':
        await state.set_state(Updater.second_name)
        await message.answer('Введите ваше отчество', reply_markup=kb.update_data())
    elif len(message.text) > 3:
        await state.update_data(last_name=message.text)
        await state.set_state(Updater.phone)
        await message.answer('Введите номер телефона', reply_markup=kb.update_data())
    else:
        await state.set_state(Updater.last_name)
        await message.answer('Слишком короткая фамилия. Введите фамилию заново', reply_markup=kb.update_data())

@router.message(Updater.phone)
async def update_phone(message: Message, state: FSMContext):
    if message.text == 'Отменить':
        await state.clear()
        await message.answer('Процесс изменения данных был отменен', reply_markup=kb.start_reg())
    elif message.text == 'Назад':
        await state.set_state(Updater.last_name)
        await message.answer('Введите вашу фамилию', reply_markup=kb.update_data)
    elif reg.validate_num(message.text):
        await state.update_data(phone=message.text)
        data = await state.get_data()
        try:
            user = User.update(
                first_name = data['first_name'],
                second_name = data['second_name'],
                last_name = data['last_name'],
                phone_number = data['phone']
            ).where(User.tg_id == message.from_user.id)
            user.execute()
            
            await state.clear()
            await message.answer('Ваши данные были успешно обновлены', reply_markup=kb.main())
        except Exception as e:
            print(e)
            await message.answer('Что-то пошло не так... Устраняем неполадки', reply_markup=kb.main())
    else:
        await state.set_state(Updater.phone)
        await message.answer('Неверно указан номер телефона. Введите номер телефона начиная с +7', reply_markup=kb.update_data())

# Получение истории заявок
@router.message(F.text == 'История заявок')
async def get_user_history(message: Message, state: FSMContext):
    user = User.get_or_none(User.tg_id == message.from_user.id)
    if user != None and not user.banned:
        await state.set_state(History.history_category)
        await message.answer('Выберите категорию заявок', reply_markup=kb.history_category())
    elif user.banned:
        await message.answer('Вы не можете получить историю заявок, т.к. были заблокированы администратором')
    else:
        await message.answer('Вы не можете использовать данную функцию. Необходима регистрация', reply_markup=kb.start_reg())    

@router.message(History.history_category)
async def get_orders(message: Message, state: FSMContext):
    user = User.get_or_none(User.tg_id == message.from_user.id)
    if user != None:
        if message.text == 'Невыполненные заявки':
            orders = Order.select().where((Order.author == user) & (Order.status == 'Получена')).limit(3).order_by(Order.date.desc())
            keyboard = kb.history(orders)
            await state.set_state(History.history)
            await state.update_data(order_type = 'received')
            await state.update_data(keyboard=keyboard)
            await state.update_data(page_number = 1)
            await state.update_data(user = user)
            await message.answer('Выберите интересующую вас заявку', reply_markup=keyboard)
        
        elif message.text == 'Выполненные заявки':
            orders = Order.select().where((Order.author == user) & (Order.status == 'Выполнена')).limit(3).order_by(Order.date.desc())
            keyboard = kb.history(orders)
            await state.set_state(History.history)
            await state.update_data(order_type = 'completed')
            await state.update_data(keyboard=keyboard)
            await state.update_data(page_number=1)
            await state.update_data(user = user)
            await message.answer('Выберите интересующую вас заявку', reply_markup=keyboard)
        
        elif message.text == 'Все заявки':
            orders = Order.select().where(Order.author == user).limit(3).order_by(Order.date.desc())
            keyboard = kb.history(orders)
            await state.set_state(History.history)
            await state.update_data(order_type = 'all')
            await state.update_data(keyboard=keyboard)
            await state.update_data(page_number=1)
            await state.update_data(user = user)
            await message.answer('Выберите интересующую вас заявку', reply_markup=keyboard)
        
        elif message.text == 'В главное меню':
            await state.clear()
            await message.answer('Процесс история заявок был завершен', reply_markup=kb.main())
        
        else:
            await state.set_state(History.history_category)
            await message.answer('Я вас не понимаю. Выберите пункт меню', reply_markup=kb.history_category())
    else:
        await message.answer('Не удалось найти вашу учетную запись. Необходима регистрация', reply_markup=kb.start_reg())

@router.message(History.history)
async def get_order_info(message: Message, state: FSMContext):
    if message.text == 'В главное меню':
        await state.clear()
        await message.answer('Процесс история заявок был завершен', reply_markup=kb.main())
    
    elif message.text == 'Вперед':
        data = await state.get_data()
        order_type = data['order_type']
        user = data['user']
        page = int(data['page_number'])
        page += 1
        
        orders = None

        if order_type == 'received':
            orders = Order.select().where((Order.author == user) & (Order.status == 'Получена')).paginate(page, 3).order_by(Order.date.desc())
        elif order_type == 'completed':
            orders = Order.select().where((Order.author == user) & (Order.status == 'Выполнена')).paginate(page, 3).order_by(Order.date.desc())
        elif order_type == 'all':
            orders = Order.select().where(Order.author == user).paginate(page, 3).order_by(Order.date.desc())


        if len(orders) > 0:
            keyboard = kb.history(orders)
            await state.set_state(History.history)
            await state.update_data(page_number = page)
            await state.update_data(user = user)
            await state.update_data(order_type = order_type)
            await message.answer('Вперед', reply_markup=keyboard)
        else:
            if order_type == 'received':
                orders = Order.select().where((Order.author == user) & (Order.status == 'Получена')).paginate(1, 3).order_by(Order.date.desc())
            elif order_type == 'completed':
                orders = Order.select().where((Order.author == user) & (Order.status == 'Выполнена')).paginate(1, 3).order_by(Order.date.desc())
            elif order_type == 'all':
                orders = Order.select().where(Order.author == user).paginate(1, 3).order_by(Order.date.desc())

            keyboard = kb.history(orders)
            await state.set_state(History.history)
            await state.update_data(order_type = order_type)
            await state.update_data(user = user)
            await state.update_data(page_number = 1)
            await message.answer('Заявок больше нет. Создайте новую или Выберите из предложенных', reply_markup=keyboard)
    
    elif message.text == 'Назад':
        data = await state.get_data()
        user = data['user']
        order_type = data['order_type']
        page = int(data['page_number'])
        page -= 1
        
        orders = None   

        if page > 0:
            if order_type == 'received':
                orders = Order.select().where((Order.author == user) & (Order.status == 'Получена')).paginate(page, 3).order_by(Order.date.desc())
            elif order_type == 'completed':
                orders = Order.select().where((Order.author == user) & (Order.status == 'Выполнена')).paginate(page, 3).order_by(Order.date.desc())
            elif order_type == 'all':
                orders = Order.select().where(Order.author == user).paginate(page, 3).order_by(Order.date.desc())
            
            keyboard = kb.history(orders)      
            await state.set_state(History.history)
            await state.update_data(page_number = page)
            await state.update_data(user = user)
            await state.update_data(order_type = order_type)
            await message.answer('Назад', reply_markup=keyboard)
        else:
            if order_type == 'received':
                orders = Order.select().where((Order.author == user) & (Order.status == 'Получена')).paginate(1, 3).order_by(Order.date.desc())
            elif order_type == 'completed':
                orders = Order.select().where((Order.author == user) & (Order.status == 'Выполнена')).paginate(1, 3).order_by(Order.date.desc())
            elif order_type == 'all':
                orders = Order.select().where(Order.author == user).paginate(1, 3).order_by(Order.date.desc())
            
            keyboard = kb.history(orders)
            await state.set_state(History.history)
            await state.update_data(order_type = order_type)
            await state.update_data(page_number=1)
            await state.update_data(user = user)
            await message.answer('Создайте новую заявку или Выберите из предложенных', reply_markup=keyboard)

   
    elif message.text.startswith('#'):
        order_id = int(message.text.split()[0][1:])
        data = await state.get_data()
        keyboard = data['keyboard']

        order = Order.get_or_none(Order.id == order_id)
        user = User.get_or_none(User.tg_id == message.from_user.id)

        if order.author == user:
            await state.set_state(History.changes)
            await state.update_data(order_id = order_id)
            await message.answer(f'Тема заявки: {order.title}\nОписание заявки: {order.discription}\nДата создания: {order.date}\nНомер кабинета: {order.office_number}\nСтатус: {order.status}', 
                                reply_markup=kb.order())
        else:
            await state.set_state(History.history)
            await message.answer('Данная заявка вам не пренадлежит. Выберите заявку из меню', reply_markup=keyboard)
   
    else:
        await state.set_state(History.changes)
        await message.answer('Я вас не понимаю. Выберите пункт меню', reply_markup=keyboard)

@router.message(History.changes)
async def changes(message: Message, state: FSMContext):
    if message.text == 'В главное меню':
        await state.clear()
        await message.answer('Процесс история заявок был завершен', reply_markup=kb.main())
    else:
        await state.set_state(History.changes)
        await message.answer('Я вас не понимаю. Выберите пункт меню', reply_markup=kb.order())


# Панель администратора
@router.message(Command('admin'))
async def cmd_admin(message: Message, state: FSMContext):
    if User.get_or_none(User.tg_id == message.from_user.id) == None:
        await message.answer('Вы не зарегистрированы. Необходима регистрация', reply_markup=kb.start_reg())
    else:
        if Admin.get_or_none(Admin.tg_id == message.from_user.id) == None:
            await message.answer('У вас недостаточно прав. Пожалуйста, обратитесь к администратору', reply_markup=kb.main())
        else:
            await state.set_state(Panel.changes)
            await message.answer('Панель администратора бота', reply_markup=kb.admin_panel_start())

@router.message(Panel.changes)
async def admin_change(message: Message, state: FSMContext):
    if message.text == 'В главное меню':
        await state.clear()
        await message.answer('Вы вышли из панели администратора', reply_markup=kb.main())
    
    elif message.text == 'Пользователи':
        users = User.select().limit(5)
        keyboard = kb.admin_panel_users(users)

        await state.update_data(page_number = 1)
        await state.update_data(keyboard = keyboard)

        await state.set_state(Panel.users)
        await message.answer('Пользователи', reply_markup=keyboard)
    
    elif message.text == 'Новые заявки':
        orders = Order.select().where(Order.status == 'Получена').limit(5).order_by(Order.date)
        keyboard = kb.admin_panel_new_orders(orders)

        await state.update_data(page_number = 1)
        await state.update_data(keyboard = keyboard)

        await state.set_state(Panel.new_orders)
        await message.answer('Новые заявки', reply_markup=keyboard)
    
    elif message.text == 'Заявки в работе':
        orders = Order.select().where(Order.status == 'В работе').limit(5).order_by(Order.date)
        keyboard = kb.admin_panel_new_orders(orders)

        await state.update_data(keyboard = keyboard)
        await state.update_data(page_number = 1)

        await state.set_state(Panel.current_orders)
        await message.answer('Заявки в работе', reply_markup=keyboard)
   
    elif message.text == 'Выполненные заявки':
        orders = Order.select().where(Order.status == 'Выполнена').limit(5).order_by(Order.date)
        keyboard = kb.admin_panel_new_orders(orders)

        await state.update_data(keyboard = keyboard)
        await state.update_data(page_number = 1)

        await state.set_state(Panel.completed_orders)
        await message.answer('Выполненные заявки', reply_markup=keyboard)
    
    elif message.text == 'Excel':
        await state.set_state(Panel.excel)
        await message.answer('Выберите пункт меню', reply_markup=kb.excel_start())
    
    else:
        await state.set_state(Panel.changes)
        await message.answer('Я вас не понимаю. Выберите пункт меню', reply_markup=kb.admin_panel_start())

@router.message(Panel.excel)
async def excel_start(message: Message, state: FSMContext):
    if message.text == 'В главное меню':
        await state.set_state(Panel.changes)
        await message.answer('Панель администратора бота', reply_markup=kb.admin_panel_start())
    elif message.text == 'Месяц':
        await state.set_state(Panel.excel_month)
        await message.answer('Выберите месяц для отчета', reply_markup=kb.excel_calendar())
    elif message.text == 'Отчеты':

        files = get_subdirectories('./reports')

        await state.update_data(keyboard=kb.excel_reports(files))
        await state.set_state(Panel.excel_reports)
        await message.answer('Выберите нужный отчет', reply_markup=kb.excel_reports(files))
    else:
        await state.set_state(Panel.changes)
        await message.answer('Я вас не понимаю. Выберите пункт меню', reply_markup=kb.excel_start())

@router.message(Panel.excel_reports)
async def excel_reports(message: Message, state: FSMContext):
    if message.text == 'В главное меню':
        await state.clear()
        await state.set_state(Panel.changes)
        await message.answer('Панель администратора бота', reply_markup=kb.admin_panel_start())
    
    elif message.text.startswith('#'):
        data = await state.get_data()
        keyboard = data['keyboard']
        
        file_name = message.text.split()[1]
        try:
            doc = FSInputFile('./reports/' + file_name)
            await state.set_state(Panel.changes)
            await message.answer_document(doc) 
            await message.answer('Отчет', reply_markup=kb.admin_panel_start())
        except Exception as e:
            print(e)
            await state.set_state(Panel.excel_reports)
            await message.answer('Файл не найден', reply_markup=keyboard)

    else:
        await state.set_state(Panel.users)
        await message.answer('Я вас не понимаю. Выберите пункт меню', reply_markup=kb.admin_panel_start())

@router.message(Panel.excel_month)
async def excel_month(message: Message, state: FSMContext):
    months = ['Янв', 'Фев', 'Мар', 'Апр', 'Май', 'Июн', 'Июл', 'Авг', 'Сен', 'Окт', 'Ноя', 'Дек']
    
    if message.text == 'В главное меню':
        await state.set_state(Panel.changes)
        await message.answer('Панель администратора бота', reply_markup=kb.admin_panel_start())
    
    elif message.text in months:
        month = message.text
        number_month = months.index(month) + 1
        
        orders = Order.select(Order.author, fn.Count(Order.id).alias('count')).where(
            Order.date.month == number_month
        ).group_by(Order.author)

        orders1 = Order.select(Order.status, fn.Count(Order.id).alias('count')).where(
            Order.date.month == number_month
        ).group_by(Order.status)

        cur_time = datetime.datetime.now().strftime("%Y-%m-%d-date-%H-%M-%S-time")
        
        create_report(orders, orders1, cur_time)
        await state.set_state(Panel.changes)
        await state.update_data(orders = orders)
        await message.answer('Отчет формируется... Пожалуйста, подождите', reply_markup= kb.admin_panel_start())
        
@router.message(Panel.users)
async def change_user(message: Message, state: FSMContext):
    
    if message.text == 'В меню':
        await state.set_state(Panel.changes)
        await message.answer('Панель администратора бота', reply_markup=kb.admin_panel_start())
    
    elif message.text == 'Вперед':
        data = await state.get_data()
        page = data['page_number']
        page += 1

        users = User.select().paginate(page, 5)

        if len(users) > 0:
            keyboard = kb.admin_panel_users(users)
            await state.set_state(Panel.users)
            await state.update_data(page_number = page)
            await message.answer('Выберите пользователя', reply_markup=keyboard)
        else:
            users = User.select().paginate(1, 5)
            keyboard = kb.admin_panel_users(users)
            await state.set_state(Panel.users)
            await state.update_data(page_number = 1)
            await message.answer('Выберите пользователя', reply_markup=keyboard)


    elif message.text == 'Назад':
        data = await state.get_data()
        page = data['page_number']
        page -= 1

        if page > 0:
            users = User.select().paginate(page, 5)
            keyboard = kb.admin_panel_users(users)
            await state.set_state(Panel.users)
            await state.update_data(page_number = page)
            await message.answer('Выберите пользователя', reply_markup=keyboard)
        else:
            users = User.select().paginate(1, 5)
            keyboard = kb.admin_panel_users(users)
            await state.set_state(Panel.users)
            await state.update_data(page_number = 1)
            await message.answer('Выберите пользователя', reply_markup=keyboard)

    
    elif message.text.startswith('#'):
        data = await state.get_data()
        keyboard = data['keyboard']
        
        user_id = int(message.text.split()[0][1:])
        user = User.get_or_none(User.id == user_id)
        
        await state.set_state(Panel.set_user)
        await state.update_data(user=user)
        await message.answer(f'ФИО: {user.last_name} {user.first_name} {user.second_name}\nНомер телефона: {user.phone_number}', 
                             reply_markup=kb.set_user())
    
    else:
        await state.set_state(Panel.users)
        await message.answer('Я вас не понимаю. Выберите пункт меню', reply_markup=kb.admin_panel_start())

@router.message(Panel.set_user)
async def change_user(message: Message, state: FSMContext):
    if message.text == 'В главное меню':
        await state.set_state(Panel.changes)
        await message.answer('Панель администратора бота', reply_markup=kb.admin_panel_start())
    elif message.text == 'Заблокировать':
        data = await state.get_data()
        user = data['user']
        
        try:
            user_update = User.update(
                banned = True
            ).where(User.tg_id == user.tg_id)
            user_update.execute()
            
            
            
            await state.set_state(Panel.changes)
            await message.answer('Пользователь успешно заблокирован', reply_markup=kb.admin_panel_start())
        except Exception as e:
            print(e)
            await message.answer('Что-то пошло не так... Устраняем неполадки', reply_markup=kb.admin_panel_start())
    
    elif message.text == 'Назначить администратором':
        try:
            data = await state.get_data()
            user = data['user']
            admin = Admin.create(
                tg_id = user.tg_id
            )
            admin.save()
            await state.clear()
            await state.set_state(Panel.changes)
            await message.answer('Администратор успешно добавлен', reply_markup=kb.admin_panel_start())
        except Exception as e:
            print(e)
            await state.clear()
            await state.set_state(Panel.changes)
            await message.answer('Что-то пошло не так... Устраняем неполадки', reply_markup=kb.admin_panel_start())
    else:
        await state.clear()
        await state.set_state(Panel.changes)
        await message.answer('Я вас не понимаю. Выберите нужный пункт меню', kb.admin_panel_start())

@router.message(Panel.new_orders)
async def change_new_orders(message: Message, state: FSMContext):
    
    if message.text == 'В меню':
        await state.set_state(Panel.changes)
        await message.answer('Панель администратора бота', reply_markup=kb.admin_panel_start())
    
    elif message.text == 'Вперед':
        data = await state.get_data()
        page = data['page_number']
        page += 1

        orders = Order.select().where(Order.status == 'Получена').paginate(page, 5)

        if len(orders) > 0:
            keyboard = kb.admin_panel_new_orders(orders)
            await state.set_state(Panel.new_orders)
            await state.update_data(page_number = page)
            await message.answer('Выберите заявку', reply_markup=keyboard)
        else:
            orders = Order.select().where(Order.status == 'Получена').paginate(1, 5)
            keyboard = kb.admin_panel_new_orders(orders)
            await state.set_state(Panel.new_orders)
            await state.update_data(page_number = 1)
            await message.answer('Выберите заявку', reply_markup=keyboard)


    elif message.text == 'Назад':
        data = await state.get_data()
        page = data['page_number']
        page -= 1

        if page > 0:
            orders = Order.select().where(Order.status == 'Получена').paginate(page, 5)
            keyboard = kb.admin_panel_new_orders(orders)
            await state.set_state(Panel.new_orders)
            await state.update_data(page_number = page)
            await message.answer('Выберите заявку', reply_markup=keyboard)
        else:
            orders = Order.select().where(Order.status == 'Получена').paginate(1, 5)
            keyboard = kb.admin_panel_new_orders(orders)
            await state.set_state(Panel.new_orders)
            await state.update_data(page_number = 1)
            await message.answer('Выберите заявку', reply_markup=keyboard)

    
    elif message.text.startswith('#'):
        data = await state.get_data()
        
        order_id = int(message.text.split()[0][1:])
        order = Order.get_or_none(Order.id == order_id)
        
        await state.set_state(Panel.new_to_current)
        await state.update_data(order=order)
        await message.answer(f'Тема заявки: {order.title}\nОписание заявки: {order.discription}\nДата создания: {order.date}\nНомер кабинета: {order.office_number}', 
                             reply_markup=kb.change_status_new_order())
    
    else:
        await state.set_state(Panel.new_orders)
        await message.answer('Я вас не понимаю. Выберите пункт меню', reply_markup=kb.admin_panel_start())    

@router.message(Panel.current_orders)
async def change_cur_orders(message: Message, state: FSMContext):
    if message.text == 'В меню':
        await state.set_state(Panel.changes)
        await message.answer('Панель администратора бота', reply_markup=kb.admin_panel_start())
    
    elif message.text == 'Вперед':
        data = await state.get_data()
        page = data['page_number']
        page += 1

        orders = Order.select().where(Order.status == 'В работе').paginate(page, 5)

        if len(orders) > 0:
            keyboard = kb.admin_panel_new_orders(orders)
            await state.set_state(Panel.current_orders)
            await state.update_data(page_number = page)
            await message.answer('Выберите заявку', reply_markup=keyboard)
        else:
            orders = Order.select().where(Order.status == 'В работе').paginate(1, 5)
            keyboard = kb.admin_panel_new_orders(orders)
            await state.set_state(Panel.current_orders)
            await state.update_data(page_number = 1)
            await message.answer('Выберите заявку', reply_markup=keyboard)


    elif message.text == 'Назад':
        data = await state.get_data()
        page = data['page_number']
        page -= 1

        if page > 0:
            orders = Order.select().where(Order.status == 'В работе').paginate(page, 5)
            keyboard = kb.admin_panel_new_orders(orders)
            await state.set_state(Panel.current_orders)
            await state.update_data(page_number = page)
            await message.answer('Выберите заявку', reply_markup=keyboard)
        else:
            orders = Order.select().where(Order.status == 'В работе').paginate(1, 5)
            keyboard = kb.admin_panel_new_orders(orders)
            await state.set_state(Panel.current_orders)
            await state.update_data(page_number = 1)
            await message.answer('Выберите заявку', reply_markup=keyboard)

    
    elif message.text.startswith('#'):
        data = await state.get_data()
        keyboard = data['keyboard']
        
        order_id = int(message.text.split()[0][1:])
        order = Order.get_or_none(Order.id == order_id)     
        await state.set_state(Panel.current_to_completed)
        await state.update_data(order=order)
        await message.answer(f'Тема заявки: {order.title}\nОписание заявки: {order.discription}\nДата создания: {order.date}\nНомер кабинета: {order.office_number}', 
                             reply_markup=kb.change_status_cur_order())
    
    else:
        await state.set_state(Panel.current_orders)
        await message.answer('Я вас не понимаю. Выберите пункт меню', reply_markup=kb.admin_panel_start())    

@router.message(Panel.completed_orders)
async def change_completed_orders(message: Message, state: FSMContext):
    if message.text == 'В меню':
        await state.set_state(Panel.changes)
        await message.answer('Панель администратора бота', reply_markup=kb.admin_panel_start())
    
    elif message.text == 'Вперед':
        data = await state.get_data()
        page = data['page_number']
        page += 1

        orders = Order.select().where(Order.status == 'Выполнена').paginate(page, 5)

        if len(orders) > 0:
            keyboard = kb.admin_panel_new_orders(orders)
            await state.set_state(Panel.completed_orders)
            await state.update_data(page_number = page)
            await message.answer('Выберите заявку', reply_markup=keyboard)
        else:
            orders = Order.select().where(Order.status == 'Выполнена').paginate(1, 5)
            keyboard = kb.admin_panel_new_orders(orders)
            await state.set_state(Panel.completed_orders)
            await state.update_data(page_number = 1)
            await message.answer('Выберите заявку', reply_markup=keyboard)


    elif message.text == 'Назад':
        data = await state.get_data()
        page = data['page_number']
        page -= 1

        if page > 0:
            orders = Order.select().where(Order.status == 'Выполнена').paginate(page, 5)
            keyboard = kb.admin_panel_new_orders(orders)
            await state.set_state(Panel.completed_orders)
            await state.update_data(page_number = page)
            await message.answer('Выберите заявку', reply_markup=keyboard)
        else:
            orders = Order.select().where(Order.status == 'Выполнена').paginate(1, 5)
            keyboard = kb.admin_panel_new_orders(orders)
            await state.set_state(Panel.completed_orders)
            await state.update_data(page_number = 1)
            await message.answer('Выберите заявку', reply_markup=keyboard)

    
    elif message.text.startswith('#'):
        data = await state.get_data()
        keyboard = data['keyboard']
        
        order_id = int(message.text.split()[0][1:])
        order = Order.get_or_none(Order.id == order_id)
        
        await state.update_data(order=order)
        await state.set_state(Panel.completed_orders)
        await message.answer(f'Тема заявки: {order.title}\nОписание заявки: {order.discription}\nДата создания: {order.date}\nНомер кабинета: {order.office_number}', 
                             reply_markup=keyboard)
    
    else:
        await state.set_state(Panel.changes)
        await message.answer('Я вас не понимаю. Выберите пункт меню', reply_markup=kb.admin_panel_start())    

@router.message(Panel.new_to_current)
async def change_status_new_order(message: Message, state: FSMContext):
    if message.text == 'В главное меню':
        await state.set_state(Panel.changes)
        await message.answer('Панель администратора бота', reply_markup=kb.admin_panel_start())
    elif message.text == 'Взять в работу':
        data = await state.get_data()
    
        order = data['order']
        try:
            order_update = Order.update(
                status = 'В работе'
            ).where(Order.id == order.id)
            order_update.execute()

            await state.set_state(Panel.changes)
            await message.answer('Заявка взята в работу', reply_markup=kb.admin_panel_start())
        except Exception as e:
            print(e)
            await state.clear()
            await state.set_state(Panel.changes)
            await message.answer('Что-то пошло не так... Устраняем неполадки', reply_markup=kb.admin_panel_start())

@router.message(Panel.current_to_completed)
async def change_status_cur_order(message: Message, state: FSMContext):
    if message.text == 'В главное меню':
        await state.set_state(Panel.changes)
        await message.answer('Панель администратора бота', reply_markup=kb.admin_panel_start())
    elif message.text == 'Выполнена':
        data = await state.get_data()
        order = data['order']
        try:
            order_update = Order.update(
                status = 'Выполнена'
            ).where(Order.id == order.id)
            order_update.execute()

            await state.set_state(Panel.changes)
            await message.answer('Заявка успешно выполнена', reply_markup=kb.admin_panel_start())
        except Exception as e:
            print(e)
            await state.clear()
            await state.set_state(Panel.changes)
            await message.answer('Что-то пошло не так... Устраняем неполадки', reply_markup=kb.admin_panel_start())
