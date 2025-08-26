from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def main():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Создать заявку")],
            [KeyboardButton(text="История заявок")],
            [KeyboardButton(text="Изменить данные")]
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите пункт меню"
    )

def start_reg():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Регистрация")]
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите пункт меню"
    )

def registration_start():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text='Отменить')
            ]
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите пункт меню"
    )

def registration():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text='Назад'),
                KeyboardButton(text='Отменить')
            ]
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите пункт меню"
    )



def create_order_start():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='Отменить')]
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите пункт меню"
    )

def create_order():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text='Назад'),
                KeyboardButton(text='Отменить')
            ]
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите пункт меню"
    ) 

def update_data_start():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='Отменить')]
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите пункт меню"
    )

def update_data():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text='Назад'),
                KeyboardButton(text='Отменить')
            ]
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите пункт меню"
    )



def history_category():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='Невыполненные заявки')],
            [KeyboardButton(text='Выполненные заявки')],
            [KeyboardButton(text='Все заявки')],
            [KeyboardButton(text='В главное меню')]
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите пункт меню"
    )

def history(orders):
    buttons = []
    
    for order in orders:
        button = KeyboardButton(text=f'#{order.id} {order.title}')
        buttons.append([button])
    
    buttons.append([KeyboardButton(text='Назад'), KeyboardButton(text='Вперед')])
    buttons.append([KeyboardButton(text='В главное меню')])
    
    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        input_field_placeholder="Выберите пункт меню"
    )

def order():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='В главное меню')]
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите пункт меню"
    )

def admin_panel_start():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='Пользователи'),KeyboardButton(text='Новые заявки')],
            [KeyboardButton(text='Заявки в работе'), KeyboardButton(text='Выполненные заявки')],
            [KeyboardButton(text='Excel')],
            [KeyboardButton(text='В главное меню')]
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите пункт меню"
    )

def admin_panel_users(users):
    buttons = []
    
    for user in users:
        button = KeyboardButton(text=f'#{user.id} {user.first_name} {user.second_name} {user.last_name}')
        buttons.append([button])
    
    buttons.append([KeyboardButton(text='Назад'), KeyboardButton(text='Вперед')])
    buttons.append([KeyboardButton(text='В меню')])
    
    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        input_field_placeholder="Выберите пункт меню"
    )

def admin_panel_new_orders(orders):
    buttons = []
    
    for order in orders:
        button = KeyboardButton(text=f'#{order.id} {order.title}')
        buttons.append([button])
    
    buttons.append([KeyboardButton(text='Назад'), KeyboardButton(text='Вперед')])
    buttons.append([KeyboardButton(text='В меню')])
    
    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        input_field_placeholder="Выберите пункт меню"
    )

def excel_start():
     return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='Месяц')],
            [KeyboardButton(text='Отчеты')],
            [KeyboardButton(text='В главное меню')]
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите пункт меню"
    )

def excel_calendar():
    return ReplyKeyboardMarkup(
        keyboard=[
             [KeyboardButton(text='Янв'), KeyboardButton(text='Фев'), KeyboardButton(text='Мар')],
             [KeyboardButton(text='Апр'), KeyboardButton(text='Май'), KeyboardButton(text='Июн')],
             [KeyboardButton(text='Июл'), KeyboardButton(text='Авг'), KeyboardButton(text='Сен')],
             [KeyboardButton(text='Окт'), KeyboardButton(text='Ноя'), KeyboardButton(text='Дек')],
             [KeyboardButton(text='В главное меню')]
        ],
        resize_keyboard=True,
        input_field_placeholder='Выберите пункт меню'
    )

def excel_reports(files):
    buttons = []
    
    for file in files:
        button = KeyboardButton(text=f'# {file}')
        buttons.append([button])
    
    buttons.append([KeyboardButton(text='В главное меню')])
    
    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        input_field_placeholder="Выберите пункт меню"
    )    

def file_name():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='Создать отчет')],
            [KeyboardButton(text='В главное меню')]
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите пункт меню"
    )

def change_status_new_order():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='Взять в работу')],
            [KeyboardButton(text='В главное меню')]
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите пункт меню"
    )

def change_status_cur_order():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='Выполнена')],
            [KeyboardButton(text='В главное меню')]
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите пункт меню"
    )

def set_user():
     return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='Заблокировать')],
            [KeyboardButton(text='Назначить администратором')],
            [KeyboardButton(text='В главное меню')]
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите пункт меню"
    )