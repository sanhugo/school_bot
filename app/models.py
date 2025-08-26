from peewee import *

try:
    db = SqliteDatabase('database.db')
    print('Database connected successfully')
except Exception as e:
    print(e)



class BaseModel(Model):
    id = PrimaryKeyField(unique=True)
    class Meta:
        database = db

class User(BaseModel):
    first_name = CharField()
    second_name = CharField()
    last_name = CharField()
    banned = BooleanField(default=False)
    phone_number = CharField()
    tg_id = CharField()

    class Meta:
        db_table = 'users'

class Order(BaseModel):
    title = CharField()
    discription = CharField()
    office_number = CharField()
    status = CharField()
    author = ForeignKeyField(User)
    date = DateField()

    class Meta:
        db_table = 'orders'

class Admin(BaseModel):
    tg_id = CharField()



db.create_tables([User, Order, Admin])