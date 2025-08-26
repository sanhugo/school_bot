import re

def validate_num(phone_number):
    # Регулярное выражение для проверки номера телефона
    phone_regex = re.compile(r'^\+7\s?\d{10}$')
    
    # Проверка соответствия номера телефона формату +7XXXXXXXXXX
    if phone_regex.search(phone_number):
        return True
    else:
        return False

def validate_class(class_number):
    pattern=re.compile(r'^[1-5][0-1]\d$')
    
    # Проверяем соответствие строки регулярному выражению
    if pattern.search(class_number):
        return True
    else:
        return False