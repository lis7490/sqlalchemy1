from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

# Определяем модель данных
Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    age = Column(Integer)

    def __repr__(self):
        return f"<User(name='{self.name}', age={self.age})>"


# Создаем подключение к БД (SQLite в памяти для примера)
engine = create_engine('sqlite:///:memory:')

# Создаем таблицы
Base.metadata.create_all(engine)

# Создаем фабрику сессий
Session = sessionmaker(bind=engine)


# Пример 1: Добавление новых записей
def add_users():
    # Создаем сессию
    session = Session()

    try:
        # Создаем объекты пользователей
        user1 = User(name='Alice', age=25)
        user2 = User(name='Bob', age=30)

        # Добавляем в сессию
        session.add(user1)
        session.add(user2)

        # Можно добавить сразу несколько
        # session.add_all([user1, user2])

        # Фиксируем изменения (сохраняем в БД)
        session.commit()
        print("Пользователи добавлены")
    except:
        # В случае ошибки откатываем изменения
        session.rollback()
        raise
    finally:
        # Всегда закрываем сессию
        session.close()


# Пример 2: Запрос данных
def query_users():
    session = Session()
    try:
        # Получаем всех пользователей
        users = session.query(User).all()
        print("Все пользователи:", users)

        # Фильтрация
        alice = session.query(User).filter_by(name='Alice').first()
        print("Алиса:", alice)

        # Более сложный запрос
        young_users = session.query(User).filter(User.age < 30).all()
        print("Молодые пользователи:", young_users)
    finally:
        session.close()


# Пример 3: Обновление данных
def update_user():
    session = Session()
    try:
        # Находим пользователя
        user = session.query(User).filter_by(name='Alice').first()

        if user:
            # Изменяем возраст
            user.age = 26
            session.commit()
            print("Данные пользователя обновлены")
    except:
        session.rollback()
        raise
    finally:
        session.close()


# Пример 4: Удаление данных
def delete_user():
    session = Session()
    try:
        user = session.query(User).filter_by(name='Bob').first()

        if user:
            session.delete(user)
            session.commit()
            print("Пользователь удален")
    except:
        session.rollback()
        raise
    finally:
        session.close()


# Выполняем примеры
add_users()
query_users()
update_user()
query_users()
delete_user()
query_users()