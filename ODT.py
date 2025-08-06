from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy.orm import Session
from bs4 import BeautifulSoup
import requests
from odf.opendocument import OpenDocumentText
from odf.text import P

# Создаем базовый класс для моделей
Base = declarative_base()


## Классы таблиц с зависимостями
class Supplier(Base):
    __tablename__ = 'suppliers'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    contact = Column(String)
    website = Column(String)

    # Связь один-ко-многим с товарами
    products = relationship("Product", back_populates="supplier")


class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    price = Column(Float)
    category = Column(String)
    supplier_id = Column(Integer, ForeignKey('suppliers.id'))

    # Связи
    supplier = relationship("Supplier", back_populates="products")
    orders = relationship("Order", back_populates="product")


class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'))
    quantity = Column(Integer)
    order_date = Column(String)  # Для простоты используем строку
    customer_name = Column(String)

    # Связи
    product = relationship("Product", back_populates="orders")


## Класс для работы с ODT документами
class ODTExporter:
    def __init__(self, filename):
        self.filename = filename
        self.doc = OpenDocumentText()

    def add_heading(self, text, level=1):
        h = P(text=text, stylename=f"Heading {level}")
        self.doc.text.addElement(h)

    def add_paragraph(self, text):
        p = P(text=text)
        self.doc.text.addElement(p)

    def save(self):
        self.doc.save(self.filename)


# Создаем подключение к БД (SQLite)
engine = create_engine('sqlite:///store.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


def populate_from_litres(session):
    """Заполнение таблицы товаров данными с litres.ru"""
    url = "https://www.litres.ru/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Создаем поставщика
        supplier = Supplier(
            name="ЛитРес",
            contact="info@litres.ru",
            website=url
        )
        session.add(supplier)
        session.commit()

        # Парсим книги (упрощенный пример)
        books = soup.select('.ArtV2Default-module__container')[:5]  # Берем первые 5 книг

        for book in books:
            try:
                title = book.select_one('.ArtInfoTitle-module__title').text.strip()
                price = float(book.select_one('.Price-module__price').text.replace('₽', '').strip())

                product = Product(
                    name=title,
                    price=price,
                    category="Книги",
                    supplier_id=supplier.id
                )
                session.add(product)
            except Exception as e:
                print(f"Ошибка при парсинге книги: {e}")

        session.commit()
        print("Данные с litres.ru успешно добавлены")
    except Exception as e:
        session.rollback()
        print(f"Ошибка при парсинге: {e}")


def create_sample_orders(session):
    """Создание тестовых заказов"""
    products = session.query(Product).all()

    if not products:
        print("Нет товаров для создания заказов")
        return

    orders = [
        Order(product_id=products[0].id, quantity=2, order_date="2023-01-15", customer_name="Иванов И.И."),
        Order(product_id=products[1].id, quantity=1, order_date="2023-01-16", customer_name="Петров П.П."),
        Order(product_id=products[2].id, quantity=3, order_date="2023-01-17", customer_name="Сидоров С.С.")
    ]

    session.add_all(orders)
    session.commit()
    print("Тестовые заказы созданы")


def display_orders(session):
    """Вывод заказов на экран"""
    orders = session.query(Order).join(Product).join(Supplier).all()

    if not orders:
        print("Нет заказов для отображения")
        return

    print("\nСписок заказов:")
    print("-" * 60)
    print(f"{'ID':<5}{'Товар':<30}{'Цена':<10}{'Кол-во':<8}{'Дата':<12}{'Клиент':<20}{'Поставщик':<20}")
    print("-" * 60)

    for order in orders:
        print(
            f"{order.id:<5}{order.product.name[:28]:<30}{order.product.price:<10.2f}{order.quantity:<8}{order.order_date:<12}{order.customer_name[:18]:<20}{order.product.supplier.name[:18]:<20}")

    print("-" * 60)
    print(f"Всего заказов: {len(orders)}")


def export_orders_to_odt(session, filename="orders.odt"):
    """Экспорт заказов в ODT файл"""
    orders = session.query(Order).join(Product).join(Supplier).all()

    exporter = ODTExporter(filename)
    exporter.add_heading("Отчет по заказам", level=1)

    if not orders:
        exporter.add_paragraph("Нет заказов для экспорта")
        exporter.save()
        return

    exporter.add_paragraph(f"Всего заказов: {len(orders)}")
    exporter.add_paragraph("Список заказов:")

    for order in orders:
        text = (f"Заказ #{order.id}: {order.product.name} (Цена: {order.product.price} руб.) "
                f"Количество: {order.quantity} Дата: {order.order_date} "
                f"Клиент: {order.customer_name} Поставщик: {order.product.supplier.name}")
        exporter.add_paragraph(text)

    exporter.save()
    print(f"\nДанные успешно экспортированы в {filename}")


# Основная программа
if __name__ == "__main__":
    session = Session()

    # Заполнение базы данных
    populate_from_litres(session)
    create_sample_orders(session)

    # Вывод данных на экран
    display_orders(session)

    # Экспорт в ODT
    export_orders_to_odt(session)

    session.close()