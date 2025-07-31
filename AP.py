import sqlalchemy as db
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Dict, Optional, Tuple, Any
from sqlalchemy import select, update, delete, insert


class BookDatabase:
    def __init__(self, database_url: str = 'sqlite:///myDatabase.db') -> None:
        """Инициализация подключения к базе данных и создание таблицы"""
        self.engine = db.create_engine(database_url)
        self.connection = self.engine.connect()
        self.metadata = db.MetaData()

        # Определяем структуру таблицы books
        self.books = db.Table(
            'books',
            self.metadata,
            db.Column('book_id', db.Integer, primary_key=True),
            db.Column('book_name', db.Text, nullable=False),
            db.Column('book_author', db.Text, nullable=False),
            db.Column('book_year', db.Integer),
            db.Column('book_is_taken', db.Boolean, default=False)
        )

        # Создаем таблицу, если она не существует
        self.metadata.create_all(self.engine)

    def __enter__(self):
        """Поддержка контекстного менеджера"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Автоматическое закрытие соединения при выходе из контекста"""
        self.close_connection()

    def add_book(self, name: str, author: str, year: int, is_taken: bool = False) -> bool:
        """Добавление новой книги в базу данных"""
        try:
            if not name or not author:
                raise ValueError("Название и автор книги не могут быть пустыми")

            stmt = insert(self.books).values(
                book_name=name,
                book_author=author,
                book_year=year,
                book_is_taken=is_taken
            )
            self.connection.execute(stmt)
            self.connection.commit()
            print(f"Книга '{name}' успешно добавлена.")
            return True
        except (SQLAlchemyError, ValueError) as e:
            print(f"Ошибка при добавлении книги: {e}")
            return False

    def add_multiple_books(self, books_list: List[Dict[str, Any]]) -> bool:
        """Добавление нескольких книг за один раз"""
        try:
            if not books_list:
                raise ValueError("Список книг пуст")

            stmt = insert(self.books).values(books_list)
            self.connection.execute(stmt)
            self.connection.commit()
            print(f"Добавлено {len(books_list)} книг.")
            return True
        except (SQLAlchemyError, ValueError) as e:
            print(f"Ошибка при добавлении книг: {e}")
            return False

    def delete_book(self, book_id: int) -> bool:
        """Удаление книги по ID"""
        try:
            stmt = delete(self.books).where(self.books.c.book_id == book_id)
            result = self.connection.execute(stmt)
            self.connection.commit()

            if result.rowcount > 0:
                print(f"Книга с ID {book_id} удалена.")
                return True
            else:
                print(f"Книга с ID {book_id} не найдена.")
                return False
        except SQLAlchemyError as e:
            print(f"Ошибка при удалении книги: {e}")
            return False

    def get_all_books(self) -> List[Tuple]:
        """Получение списка всех книг"""
        try:
            stmt = select(self.books)
            result = self.connection.execute(stmt)
            return result.fetchall()
        except SQLAlchemyError as e:
            print(f"Ошибка при получении списка книг: {e}")
            return []

    def get_book_by_id(self, book_id: int) -> Optional[Tuple]:
        """Получение книги по ID"""
        try:
            stmt = select(self.books).where(self.books.c.book_id == book_id)
            result = self.connection.execute(stmt)
            return result.fetchone()
        except SQLAlchemyError as e:
            print(f"Ошибка при получении книги: {e}")
            return None

    def search_books(self, name: Optional[str] = None, author: Optional[str] = None, year: Optional[int] = None) -> List[Tuple]:
        """Поиск книг по названию, автору или году"""
        try:
            stmt = select(self.books)

            if name:
                stmt = stmt.where(self.books.c.book_name.ilike(f'%{name}%'))
            if author:
                stmt = stmt.where(self.books.c.book_author.ilike(f'%{author}%'))
            if year:
                stmt = stmt.where(self.books.c.book_year == year)

            result = self.connection.execute(stmt)
            return result.fetchall()
        except SQLAlchemyError as e:
            print(f"Ошибка при поиске книг: {e}")
            return []

    def update_book_status(self, book_id: int, is_taken: bool) -> bool:
        """Обновление статуса книги (взята/не взята)"""
        try:
            stmt = (
                update(self.books)
                .where(self.books.c.book_id == book_id)
                .values(book_is_taken=is_taken)
            )
            result = self.connection.execute(stmt)
            self.connection.commit()

            if result.rowcount > 0:
                status = "взята" if is_taken else "не взята"
                print(f"Статус книги с ID {book_id} изменен на '{status}'.")
                return True
            else:
                print(f"Книга с ID {book_id} не найдена.")
                return False
        except SQLAlchemyError as e:
            print(f"Ошибка при обновлении статуса: {e}")
            return False

    def close_connection(self) -> None:
        """Закрытие соединения с базой данных"""
        try:
            self.connection.close()
            self.engine.dispose()
            print("Соединение закрыто.")
        except SQLAlchemyError as e:
            print(f"Ошибка при закрытии соединения: {e}")


# Пример использования
if __name__ == "__main__":
    with BookDatabase() as db:
        # Добавляем книги
        db.add_book("Преступление и наказание", "Фёдор Достоевский", 1866)
        db.add_book("Война и мир", "Лев Толстой", 1869)

        # Получаем все книги
        print("\nВсе книги в базе:")
        for book in db.get_all_books():
            print(book)

        # Поиск книг Толстого
        print("\nКниги Толстого:")
        for book in db.search_books(author="Толстой"):
            print(book)