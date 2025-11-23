import tkinter as tk
from tkinter import messagebox, ttk
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
import sqlite3
import logging
from pathlib import Path

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('library.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Абстрактный класс Person (наследование)
class Person(ABC):
    """Абстрактный базовый класс для пользователей системы."""
    
    def __init__(self, name, person_id):
        """
        Инициализирует пользователя.
        
        Args:
            name (str): Имя пользователя
            person_id (int): Уникальный ID пользователя
        """
        self._name = name  # Инкапсуляция
        self._id = person_id

    def get_name(self):
        """Возвращает имя пользователя."""
        return self._name

    def get_id(self):
        """Возвращает ID пользователя."""
        return self._id
    
    def set_name(self, name):
        """Устанавливает новое имя пользователя."""
        self._name = name

    @abstractmethod
    def borrow_book(self, book):
        """Абстрактный метод для заимствования книги."""
        pass

# Класс User (наследует от Person)
class User(Person):
    """Класс обычного пользователя библиотеки."""
    
    MAX_BOOKS = 3  # Максимум книг для пользователя
    
    def __init__(self, name, user_id):
        """Инициализирует пользователя.
        
        Args:
            name (str): Имя пользователя
            user_id (int): Уникальный ID пользователя
        """
        super().__init__(name, user_id)
        self._borrowed_books = []  # Инкапсуляция

    def borrow_book(self, book):
        """Пользователь берет книгу (полиморфизм).
        
        Returns:
            bool: True если успешно, False если достигнут лимит
        """
        if len(self._borrowed_books) < self.MAX_BOOKS: 
            self._borrowed_books.append(book)
            return True
        return False

    def return_book(self, book):
        """Пользователь возвращает книгу.
        
        Returns:
            bool: True если успешно, False если книги нет
        """
        if book in self._borrowed_books:
            self._borrowed_books.remove(book)
            return True
        return False

    def get_borrowed_books(self):
        """Возвращает список взятых книг."""
        return self._borrowed_books
    
    def get_borrowed_count(self):
        """Возвращает количество взятых книг."""
        return len(self._borrowed_books)

# Класс Librarian (наследует от Person)
class Librarian(Person):
    """Класс библиотекаря с разными уровнями доступа."""
    
    MAX_BOOKS_LIBRARIAN = 5  # Максимум книг для библиотекаря
    
    def __init__(self, name, librarian_id, access_level=1):
        """Инициализирует библиотекаря.
        
        Args:
            name (str): Имя библиотекаря
            librarian_id (int): Уникальный ID
            access_level (int): Уровень доступа (1 - полный)
        """
        super().__init__(name, librarian_id)
        self._access_level = access_level  # Инкапсуляция
        self._borrowed_books = []

    def get_access_level(self):
        """Возвращает уровень доступа."""
        return self._access_level
    
    def set_access_level(self, level):
        """Устанавливает уровень доступа."""
        self._access_level = level

    def borrow_book(self, book):
        """Библиотекарь может брать книги (до 5).
        
        Returns:
            bool: True если успешно
        """
        if len(self._borrowed_books) < self.MAX_BOOKS_LIBRARIAN:
            self._borrowed_books.append(book)
            return True
        return False

    def add_book(self, library_system, book):
        """Добавляет книгу в систему.
        
        Returns:
            bool: True если у библиотекаря есть доступ
        """
        if self._access_level >= 1:
            library_system.add_book(book)
            return True
        return False

    def remove_book(self, library_system, book_id):
        """Удаляет книгу из системы по ID.
        
        Returns:
            bool: True если у библиотекаря есть доступ
        """
        if self._access_level >= 1:
            library_system.remove_book(book_id)
            return True
        return False
    
    def edit_book(self, library_system, book_id, title=None, author_id=None, year=None):
        """Редактирует данные книги."""
        if self._access_level >= 1:
            library_system.edit_book(book_id, title, author_id, year)
            return True
        return False

class Author:
    """Класс для представления автора книги."""
    
    def __init__(self, author_id, name, bio=""):
        """Инициализирует автора.
        
        Args:
            author_id (int): Уникальный ID автора из БД
            name (str): Имя автора
            bio (str): Биография автора
        """
        self._id = author_id
        self._name = name
        self._bio = bio

    def get_id(self):
        """Возвращает ID автора."""
        return self._id

    def get_name(self):
        """Возвращает имя автора."""
        return self._name

    def get_bio(self):
        """Возвращает биографию автора."""
        return self._bio
    
    def set_bio(self, bio):
        """Устанавливает биографию автора."""
        self._bio = bio

class Book:
    """Класс для представления книги."""
    
    def __init__(self, book_id, title, author, year, status="доступна"):
        """Инициализирует книгу.
        
        Args:
            book_id (int): Уникальный ID книги из БД
            title (str): Название книги
            author (Author): Объект автора (композиция)
            year (int): Год издания
            status (str): Статус доступности
        """
        self._id = book_id
        self._title = title
        self._author = author  # Композиция
        self._year = year
        self._status = status  # Инкапсуляция

    def get_id(self):
        """Возвращает ID книги."""
        return self._id

    def get_title(self):
        """Возвращает название книги."""
        return self._title
    
    def set_title(self, title):
        """Устанавливает название книги."""
        self._title = title

    def get_author(self):
        """Возвращает автора книги."""
        return self._author

    def get_year(self):
        """Возвращает год издания."""
        return self._year
    
    def set_year(self, year):
        """Устанавливает год издания."""
        if year > 0:
            self._year = year
        else:
            raise ValueError("Год должен быть положительным числом")

    def is_available(self):
        """Проверяет, доступна ли книга."""
        return self._status == "доступна"

    def get_status(self):
        """Возвращает статус книги."""
        return self._status

    def set_status(self, status):
        """Устанавливает статус книги."""
        self._status = status


class Loan:
    """Класс для представления выдачи/возврата книги."""
    
    LOAN_DAYS = 14  # Срок выдачи книги
    
    def __init__(self, loan_id, book, user, issue_date, return_date=None):
        """Инициализирует выдачу.
        
        Args:
            loan_id (int): ID выдачи из БД
            book (Book): Книга
            user (User): Пользователь
            issue_date (datetime): Дата выдачи
            return_date (datetime): Дата возврата (None если не возвращена)
        """
        self._id = loan_id
        self._book = book
        self._user = user
        self._issue_date = issue_date
        self._return_date = return_date  # Инкапсуляция

    def get_id(self):
        """Возвращает ID выдачи."""
        return self._id

    def return_book(self, return_date):
        """Регистрирует возврат книги."""
        self._return_date = return_date

    def is_overdue(self):
        """Проверяет, просрочена ли книга.
        
        Returns:
            bool: True если книга просрочена
        """
        if self._return_date is None:
            due_date = self._issue_date + timedelta(days=self.LOAN_DAYS)
            return datetime.now() > due_date
        return False

    def get_details(self):
        """Возвращает подробную информацию о выдаче."""
        status = "Просрочено ⚠️" if self.is_overdue() else "OK"
        return f"Книга: {self._book.get_title()}, Пользователь: {self._user.get_name()}, Выдана: {self._issue_date.strftime('%Y-%m-%d')}, Статус: {status}"
    
    def get_book(self):
        """Возвращает книгу."""
        return self._book
    
    def get_user(self):
        """Возвращает пользователя."""
        return self._user
    
    def get_issue_date(self):
        """Возвращает дату выдачи."""
        return self._issue_date
    
    def get_return_date(self):
        """Возвращает дату возврата."""
        return self._return_date

# Класс LibrarySystem с БД
class LibrarySystem:
    """Главный класс системы управления библиотекой."""
    
    def __init__(self, db_name="library.db"):
        """Инициализирует систему и подключается к БД."""
        self._db_name = db_name
        try:
            self._conn = sqlite3.connect(db_name)
            self._conn.row_factory = sqlite3.Row
            self._create_tables()
            self._books = self._load_books()
            self._users = self._load_users()
            self._librarians = self._load_librarians()
            self._loans = self._load_loans()
            self._authors = self._load_authors()
            logger.info("Система инициализирована успешно")

            if not self._books:
                self._init_demo_data()
        except sqlite3.Error as e:
            logger.error(f"Ошибка подключения к БД: {e}")
            raise

    def _init_demo_data(self):
        """Инициализирует демо-данные."""
        try:
            cursor = self._conn.cursor()
            cursor.execute("INSERT INTO authors (name, bio) VALUES (?, ?)", 
                         ("Лев Толстой", "Великий русский писатель"))
            author1_id = cursor.lastrowid
            
            cursor.execute("INSERT INTO authors (name, bio) VALUES (?, ?)", 
                         ("Фёдор Достоевский", "Классик русской литературы"))
            author2_id = cursor.lastrowid
            
            cursor.execute("INSERT INTO books (title, author_id, year, status) VALUES (?, ?, ?, ?)", 
                         ("Война и мир", author1_id, 1869, "доступна"))
            cursor.execute("INSERT INTO books (title, author_id, year, status) VALUES (?, ?, ?, ?)", 
                         ("Преступление и наказание", author2_id, 1866, "доступна"))
            
            cursor.execute("INSERT INTO users (name) VALUES (?)", ("Иван Иванов",))
            cursor.execute("INSERT INTO users (name) VALUES (?)", ("Мария Петрова",))
            
            self._conn.commit()
            self._books = self._load_books()
            self._users = self._load_users()
            self._authors = self._load_authors()
            logger.info("Демо-данные добавлены")
        except sqlite3.Error as e:
            logger.error(f"Ошибка при добавлении демо-данных: {e}")
            self._conn.rollback()

    def _create_tables(self):
        """Создает таблицы БД с улучшениями (UNIQUE, CHECK, индексы)."""
        try:
            cursor = self._conn.cursor()
            
            # Таблица авторов с UNIQUE на name
            cursor.execute('''CREATE TABLE IF NOT EXISTS authors (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                name TEXT NOT NULL UNIQUE,
                                bio TEXT
                              )''')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_authors_name ON authors(name)')
            
            # Таблица книг с CHECK и индексами
            cursor.execute('''CREATE TABLE IF NOT EXISTS books (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                title TEXT NOT NULL,
                                author_id INTEGER,
                                year INTEGER CHECK(year > 0),
                                status TEXT,
                                FOREIGN KEY (author_id) REFERENCES authors(id)
                              )''')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_books_title ON books(title)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_books_author_id ON books(author_id)')
            
            # Таблица пользователей с AUTOINCREMENT
            cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                name TEXT NOT NULL
                              )''')
            
            # Таблица библиотекарей
            cursor.execute('''CREATE TABLE IF NOT EXISTS librarians (
                                id INTEGER PRIMARY KEY,
                                name TEXT NOT NULL,
                                access_level INTEGER CHECK(access_level > 0)
                              )''')
            
            # Таблица выдач с индексами
            cursor.execute('''CREATE TABLE IF NOT EXISTS loans (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                book_id INTEGER,
                                user_id INTEGER,
                                issue_date TEXT,
                                return_date TEXT,
                                FOREIGN KEY (book_id) REFERENCES books(id),
                                FOREIGN KEY (user_id) REFERENCES users(id)
                              )''')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_loans_user_id ON loans(user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_loans_book_id ON loans(book_id)')
            
            self._conn.commit()
            logger.info("Таблицы БД созданы/проверены")
        except sqlite3.Error as e:
            logger.error(f"Ошибка при создании таблиц: {e}")
            raise

    def _load_authors(self):
        """Загружает авторов из БД."""
        try:
            cursor = self._conn.cursor()
            cursor.execute("SELECT id, name, bio FROM authors")
            return [Author(id, name, bio) for id, name, bio in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Ошибка загрузки авторов: {e}")
            return []

    def _load_books(self):
        """Загружает книги из БД."""
        try:
            cursor = self._conn.cursor()
            cursor.execute("SELECT id, title, author_id, year, status FROM books")
            books = []
            for book_id, title, author_id, year, status in cursor.fetchall():
                author = self._get_author_by_id(author_id)
                if author:
                    books.append(Book(book_id, title, author, year, status))
            return books
        except sqlite3.Error as e:
            logger.error(f"Ошибка загрузки книг: {e}")
            return []

    def _load_users(self):
        """Загружает пользователей из БД."""
        try:
            cursor = self._conn.cursor()
            cursor.execute("SELECT id, name FROM users")
            return [User(name, id) for id, name in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Ошибка загрузки пользователей: {e}")
            return []

    def _load_librarians(self):
        """Загружает библиотекарей из БД."""
        try:
            cursor = self._conn.cursor()
            cursor.execute("SELECT id, name, access_level FROM librarians")
            return [Librarian(name, id, access_level) for id, name, access_level in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Ошибка загрузки библиотекарей: {e}")
            return []

    def _load_loans(self):
        """Загружает выдачи из БД."""
        try:
            cursor = self._conn.cursor()
            cursor.execute("SELECT id, book_id, user_id, issue_date, return_date FROM loans")
            loans = []
            for loan_id, book_id, user_id, issue_date_str, return_date_str in cursor.fetchall():
                book = self._get_book_by_id(book_id)
                user = self._get_user_by_id(user_id)
                if book and user:
                    issue_date = datetime.fromisoformat(issue_date_str)
                    return_date = datetime.fromisoformat(return_date_str) if return_date_str else None
                    loan = Loan(loan_id, book, user, issue_date, return_date)
                    loans.append(loan)
            return loans
        except sqlite3.Error as e:
            logger.error(f"Ошибка загрузки выдач: {e}")
            return []

    def _get_author_by_id(self, author_id):
        """Получает автора по ID."""
        try:
            cursor = self._conn.cursor()
            cursor.execute("SELECT id, name, bio FROM authors WHERE id=?", (author_id,))
            row = cursor.fetchone()
            return Author(row[0], row[1], row[2]) if row else None
        except sqlite3.Error as e:
            logger.error(f"Ошибка получения автора: {e}")
            return None

    def _get_book_by_id(self, book_id):
        """Получает книгу по ID."""
        try:
            cursor = self._conn.cursor()
            cursor.execute("SELECT id, title, author_id, year, status FROM books WHERE id=?", (book_id,))
            row = cursor.fetchone()
            if row:
                author = self._get_author_by_id(row[2])
                return Book(row[0], row[1], author, row[3], row[4]) if author else None
            return None
        except sqlite3.Error as e:
            logger.error(f"Ошибка получения книги: {e}")
            return None

    def _get_user_by_id(self, user_id):
        """Получает пользователя по ID."""
        try:
            cursor = self._conn.cursor()
            cursor.execute("SELECT id, name FROM users WHERE id=?", (user_id,))
            row = cursor.fetchone()
            return User(row[1], row[0]) if row else None
        except sqlite3.Error as e:
            logger.error(f"Ошибка получения пользователя: {e}")
            return None

    def find_book_by_title(self, title):
        """Ищет книги по подстроке названия."""
        return [b for b in self._books if title.lower() in b.get_title().lower()]
    
    def find_user_by_name(self, name):
        """Ищет пользователей по подстроке имени."""
        return [u for u in self._users if name.lower() in u.get_name().lower()]
    
    def find_author_by_name(self, name):
        """Ищет авторов по подстроке имени."""
        return [a for a in self._authors if name.lower() in a.get_name().lower()]

    def add_book(self, title, author_name, author_bio, year):
        """Добавляет книгу в систему.
        
        Args:
            title (str): Название книги
            author_name (str): Имя автора
            author_bio (str): Биография автора
            year (int): Год издания
            
        Returns:
            bool: True если успешно добавлена
        """
        try:
            cursor = self._conn.cursor()
            
            # Проверяем/добавляем автора
            cursor.execute("SELECT id FROM authors WHERE name=?", (author_name,))
            author_row = cursor.fetchone()
            
            if author_row:
                author_id = author_row[0]
            else:
                cursor.execute("INSERT INTO authors (name, bio) VALUES (?, ?)", 
                             (author_name, author_bio))
                author_id = cursor.lastrowid
            
            # Добавляем книгу
            cursor.execute("INSERT INTO books (title, author_id, year, status) VALUES (?, ?, ?, ?)", 
                         (title, author_id, year, "доступна"))
            self._conn.commit()
            
            # Перезагружаем данные
            self._books = self._load_books()
            self._authors = self._load_authors()
            logger.info(f"Книга '{title}' добавлена")
            return True
        except sqlite3.IntegrityError as e:
            logger.warning(f"Ошибка целостности при добавлении книги: {e}")
            self._conn.rollback()
            return False
        except sqlite3.Error as e:
            logger.error(f"Ошибка добавления книги: {e}")
            self._conn.rollback()
            return False

    def remove_book(self, book_id):
        """Удаляет книгу из системы по ID.
        
        Returns:
            bool: True если успешно удалена
        """
        try:
            cursor = self._conn.cursor()
            cursor.execute("DELETE FROM books WHERE id=?", (book_id,))
            self._conn.commit()
            self._books = self._load_books()
            logger.info(f"Книга с ID {book_id} удалена")
            return True
        except sqlite3.Error as e:
            logger.error(f"Ошибка удаления книги: {e}")
            self._conn.rollback()
            return False

    def edit_book(self, book_id, title=None, year=None, author_bio=None):
        """Редактирует данные книги.
        
        Returns:
            bool: True если успешно отредактирована
        """
        try:
            cursor = self._conn.cursor()
            
            if title is not None:
                cursor.execute("UPDATE books SET title=? WHERE id=?", (title, book_id))
            
            if year is not None:
                if year > 0:
                    cursor.execute("UPDATE books SET year=? WHERE id=?", (year, book_id))
                else:
                    raise ValueError("Год должен быть положительным числом")
            
            if author_bio is not None:
                cursor.execute("""UPDATE authors SET bio=? 
                               WHERE id=(SELECT author_id FROM books WHERE id=?)""", 
                             (author_bio, book_id))
            
            self._conn.commit()
            self._books = self._load_books()
            logger.info(f"Книга с ID {book_id} отредактирована")
            return True
        except sqlite3.Error as e:
            logger.error(f"Ошибка редактирования книги: {e}")
            self._conn.rollback()
            return False

    def register_user(self, name):
        """Регистрирует нового пользователя.
        
        Returns:
            User: Новый пользователь или None при ошибке
        """
        try:
            cursor = self._conn.cursor()
            cursor.execute("INSERT INTO users (name) VALUES (?)", (name,))
            self._conn.commit()
            user_id = cursor.lastrowid
            user = User(name, user_id)
            self._users.append(user)
            logger.info(f"Пользователь '{name}' зарегистрирован")
            return user
        except sqlite3.Error as e:
            logger.error(f"Ошибка регистрации пользователя: {e}")
            self._conn.rollback()
            return None

    def edit_user(self, user_id, name):
        """Редактирует данные пользователя.
        
        Returns:
            bool: True если успешно отредактирован
        """
        try:
            cursor = self._conn.cursor()
            cursor.execute("UPDATE users SET name=? WHERE id=?", (name, user_id))
            self._conn.commit()
            
            # Обновляем объект в памяти
            user = next((u for u in self._users if u.get_id() == user_id), None)
            if user:
                user.set_name(name)
            logger.info(f"Пользователь с ID {user_id} отредактирован")
            return True
        except sqlite3.Error as e:
            logger.error(f"Ошибка редактирования пользователя: {e}")
            self._conn.rollback()
            return False

    def delete_user(self, user_id):
        """Удаляет пользователя.
        
        Returns:
            bool: True если успешно удален
        """
        try:
            cursor = self._conn.cursor()
            cursor.execute("DELETE FROM users WHERE id=?", (user_id,))
            self._conn.commit()
            self._users = [u for u in self._users if u.get_id() != user_id]
            logger.info(f"Пользователь с ID {user_id} удален")
            return True
        except sqlite3.Error as e:
            logger.error(f"Ошибка удаления пользователя: {e}")
            self._conn.rollback()
            return False

    def register_librarian(self, librarian):
        """Регистрирует библиотекаря."""
        try:
            cursor = self._conn.cursor()
            cursor.execute("INSERT OR IGNORE INTO librarians (id, name, access_level) VALUES (?, ?, ?)", 
                         (librarian.get_id(), librarian.get_name(), librarian._access_level))
            self._conn.commit()
            if librarian not in self._librarians:
                self._librarians.append(librarian)
            logger.info(f"Библиотекарь '{librarian.get_name()}' зарегистрирован")
        except sqlite3.Error as e:
            logger.error(f"Ошибка регистрации библиотекаря: {e}")

    def issue_book(self, user_id, book_id):
        """Выдает книгу пользователю.
        
        Returns:
            Loan: Выдача или None при ошибке
        """
        try:
            user = next((u for u in self._users if u.get_id() == user_id), None)
            book = next((b for b in self._books if b.get_id() == book_id), None)
            
            if not user:
                logger.warning(f"Пользователь {user_id} не найден")
                return None
            
            if not book:
                logger.warning(f"Книга {book_id} не найдена")
                return None
            
            if not book.is_available():
                logger.warning(f"Книга '{book.get_title()}' недоступна")
                return None
            
            if len(user.get_borrowed_books()) >= User.MAX_BOOKS:
                logger.warning(f"Пользователь {user.get_name()} достиг лимита книг")
                return None
            
            cursor = self._conn.cursor()
            now = datetime.now()
            cursor.execute("INSERT INTO loans (book_id, user_id, issue_date) VALUES (?, ?, ?)", 
                         (book_id, user_id, now.isoformat()))
            # Обновляем статус книги в БД и в памяти
            cursor.execute("UPDATE books SET status=? WHERE id=?", ("выдана", book_id))
            self._conn.commit()

            loan_id = cursor.lastrowid
            loan = Loan(loan_id, book, user, now)
            book.set_status("выдана")
            user.borrow_book(book)
            self._loans.append(loan)
            logger.info(f"Книга '{book.get_title()}' выдана {user.get_name()}")
            return loan
        except sqlite3.Error as e:
            logger.error(f"Ошибка выдачи книги: {e}")
            return None

    def return_book(self, loan_id):
        """Возвращает книгу.
        
        Returns:
            bool: True если успешно возвращена
        """
        try:
            loan = next((l for l in self._loans if l.get_id() == loan_id), None)
            if not loan or loan.get_return_date() is not None:
                logger.warning(f"Выдача {loan_id} не найдена или уже возвращена")
                return False
            
            cursor = self._conn.cursor()
            now = datetime.now()
            cursor.execute("UPDATE loans SET return_date=? WHERE id=?", (now.isoformat(), loan_id))
            # Обновляем статус книги в БД
            cursor.execute("UPDATE books SET status=? WHERE id=?", ("доступна", loan.get_book().get_id()))
            self._conn.commit()

            loan.return_book(now)
            loan.get_book().set_status("доступна")
            loan.get_user().return_book(loan.get_book())
            logger.info(f"Книга '{loan.get_book().get_title()}' возвращена {loan.get_user().get_name()}")
            return True
        except sqlite3.Error as e:
            logger.error(f"Ошибка возврата книги: {e}")
            return False

    def get_books(self):
        """Возвращает список всех книг."""
        return self._books

    def get_users(self):
        """Возвращает список всех пользователей."""
        return self._users

    def get_loans(self):
        """Возвращает список всех выдач."""
        return self._loans

    def get_librarians(self):
        """Возвращает список всех библиотекарей."""
        return self._librarians
    
    def get_active_loans(self):
        """Возвращает список активных (невозвращенных) выдач."""
        return [l for l in self._loans if l.get_return_date() is None]
    
    def authenticate_librarian(self, librarian_id):
        """Проверяет, существует ли библиотекарь.
        
        Returns:
            Librarian: Объект библиотекаря или None
        """
        try:
            cursor = self._conn.cursor()
            cursor.execute("SELECT id, name, access_level FROM librarians WHERE id=?", (librarian_id,))
            row = cursor.fetchone()
            if row:
                return Librarian(row[1], row[0], row[2])
            return None
        except sqlite3.Error as e:
            logger.error(f"Ошибка проверки библиотекаря: {e}")
            return None

    def close(self):
        """Закрывает подключение к БД."""
        try:
            self._conn.close()
            logger.info("Подключение к БД закрыто")
        except sqlite3.Error as e:
            logger.error(f"Ошибка закрытия БД: {e}")

class LibraryApp:
    """Главное приложение с GUI на Tkinter."""
    
    def __init__(self, root):
        """Инициализирует приложение.
        
        Args:
            root (tk.Tk): Корневое окно
        """
        self.system = LibrarySystem()
        self.root = root
        self.root.title("Система управления библиотекой")
        self.root.geometry("1100x750")
        self.root.minsize(800, 600)
        self.root.configure(bg="#f5f5f5")
        
        # Переменная для хранения текущего библиотекаря
        self.current_librarian = None
        
        # Стиль
        self._configure_style()
        
        # Начальный экран с логином
        self._show_login_screen()

    def _configure_style(self):
        """Настраивает стиль приложения."""
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TButton", padding=10, relief="flat", background="#607d8b", 
                       foreground="white", font=("Helvetica", 11))
        style.map("TButton", background=[('active', '#546e7a')])
        style.configure("TLabel", font=("Helvetica", 11), background="#f5f5f5", 
                       foreground="#333333")
        style.configure("TEntry", font=("Helvetica", 11), fieldbackground="#ffffff")
        style.configure("TCombobox", font=("Helvetica", 11), fieldbackground="#ffffff")
        style.configure("Treeview", font=("Helvetica", 10), rowheight=25, 
                       background="#ffffff", foreground="#333333")
        style.configure("Treeview.Heading", font=("Helvetica", 11, "bold"), 
                       background="#e0e0e0", foreground="#333333")
        style.map("Treeview", background=[('selected', '#cfd8dc')])
        style.configure("Title.TLabel", font=("Helvetica", 14, "bold"), 
                       background="#f5f5f5", foreground="#1a1a1a")

    def _show_login_screen(self):
        """Показывает экран входа."""
        self.root.geometry("400x300")
        
        # Очищаем окно
        for widget in self.root.winfo_children():
            widget.destroy()
        
        main_frame = ttk.Frame(self.root, padding="30")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="Вход в систему", style="Title.TLabel").pack(pady=20)
        ttk.Label(main_frame, text="ID библиотекаря:").pack(anchor="w", pady=(10, 5))
        
        id_entry = ttk.Entry(main_frame, width=20)
        id_entry.pack(fill=tk.X, pady=(0, 20))
        id_entry.focus()
        
        def login():
            try:
                librarian_id = int(id_entry.get())
                librarian = self.system.authenticate_librarian(librarian_id)
                
                if librarian:
                    self.current_librarian = librarian
                    logger.info(f"Вход библиотекаря {librarian.get_name()}")
                    self._show_main_screen()
                else:
                    messagebox.showerror("Ошибка", "Библиотекарь не найден!")
                    id_entry.delete(0, tk.END)
            except ValueError:
                messagebox.showerror("Ошибка", "ID должен быть числом!")
                id_entry.delete(0, tk.END)
        
        ttk.Button(main_frame, text="Войти", command=login).pack(pady=10)
        
        # Подсказка для демо
        ttk.Label(main_frame, text="Подсказка: используйте ID 1", 
                 font=("Helvetica", 9), foreground="gray").pack(pady=(30, 0))

    def _show_main_screen(self):
        """Показывает основной экран приложения."""
        self.root.geometry("1100x750")
        
        # Очищаем окно
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Главное окно с меню и содержимым
        self.main_pane = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, bg="#f5f5f5")
        self.main_pane.pack(fill=tk.BOTH, expand=True)
        
        # Левое меню
        self.menu_frame = ttk.Frame(self.main_pane, padding="10", width=200)
        self.main_pane.add(self.menu_frame, minsize=200)
        
        ttk.Label(self.menu_frame, text=f"Библиотекарь:\n{self.current_librarian.get_name()}", 
                 font=("Helvetica", 10, "bold")).pack(pady=10)
        ttk.Separator(self.menu_frame, orient='horizontal').pack(fill=tk.X, pady=10)
        
        buttons = [
            ("📚 Добавить книгу", self.show_add_book),
            ("👤 Зарегистрировать пользователя", self.show_register_user),
            ("📤 Выдать книгу", self.show_issue_book),
            ("📥 Вернуть книгу", self.show_return_book),
            ("📖 Список книг", self.show_list_books),
            ("📋 Список выдач", self.show_list_loans),
            ("👥 Список пользователей", self.show_list_users),
            ("✏️ Редактировать книгу", self.show_edit_book),
            ("✏️ Редактировать пользователя", self.show_edit_user),
            ("🚪 Выход", self._logout)
        ]
        
        for text, command in buttons:
            ttk.Button(self.menu_frame, text=text, command=command).pack(fill=tk.X, pady=4)
        
        # Правое содержимое
        self.content_frame = ttk.Frame(self.main_pane, padding="20")
        self.main_pane.add(self.content_frame, minsize=400)
        
        self.clear_content()
        ttk.Label(self.content_frame, text="Добро пожаловать!", style="Title.TLabel").pack(pady=20)
        ttk.Label(self.content_frame, 
                 text="Выберите действие из меню слева для начала работы.").pack(pady=10)

    def clear_content(self):
        """Очищает содержимое контент-панели."""
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def _logout(self):
        """Выход из аккаунта."""
        self.current_librarian = None
        logger.info("Пользователь вышел")
        self._show_login_screen()

    def show_add_book(self):
        """Показывает форму добавления книги."""
        self.clear_content()
        ttk.Label(self.content_frame, text="Добавить книгу", style="Title.TLabel").pack(pady=10)
        
        frame = ttk.Frame(self.content_frame)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(frame, text="Название книги:").pack(anchor="w", pady=(10, 0))
        title_entry = ttk.Entry(frame, width=40)
        title_entry.pack(fill=tk.X, pady=5)
        
        ttk.Label(frame, text="Имя автора:").pack(anchor="w", pady=(10, 0))
        author_entry = ttk.Entry(frame, width=40)
        author_entry.pack(fill=tk.X, pady=5)
        
        ttk.Label(frame, text="Биография автора:").pack(anchor="w", pady=(10, 0))
        bio_text = tk.Text(frame, height=4, width=40, font=("Helvetica", 10))
        bio_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        ttk.Label(frame, text="Год издания:").pack(anchor="w", pady=(10, 0))
        year_entry = ttk.Entry(frame, width=40)
        year_entry.pack(fill=tk.X, pady=5)
        
        def add():
            title = title_entry.get().strip()
            author_name = author_entry.get().strip()
            bio = bio_text.get("1.0", tk.END).strip()
            year_str = year_entry.get().strip()
            
            if not title:
                messagebox.showerror("Ошибка", "Введите название книги!")
                return
            
            if not author_name:
                messagebox.showerror("Ошибка", "Введите имя автора!")
                return
            
            try:
                year = int(year_str)
                if year <= 0 or year > 2100:
                    raise ValueError("Год должен быть между 1 и 2100")
                
                if self.system.add_book(title, author_name, bio, year):
                    messagebox.showinfo("Успех", f"Книга '{title}' добавлена успешно!")
                    self.clear_content()
                    ttk.Label(self.content_frame, text="✓ Книга добавлена успешно").pack(pady=20)
                else:
                    messagebox.showerror("Ошибка", "Не удалось добавить книгу (возможно, автор уже существует).")
            except ValueError as e:
                messagebox.showerror("Ошибка", f"Год должен быть числом (1-2100)! {str(e)}")
        
        ttk.Button(frame, text="Добавить", command=add).pack(pady=20)

    def show_register_user(self):
        """Показывает форму регистрации пользователя."""
        self.clear_content()
        ttk.Label(self.content_frame, text="Зарегистрировать пользователя", style="Title.TLabel").pack(pady=10)
        
        frame = ttk.Frame(self.content_frame)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(frame, text="Имя пользователя:").pack(anchor="w", pady=(10, 0))
        name_entry = ttk.Entry(frame, width=40)
        name_entry.pack(fill=tk.X, pady=5)
        name_entry.focus()
        
        def register():
            name = name_entry.get().strip()
            if not name:
                messagebox.showerror("Ошибка", "Введите имя пользователя!")
                return
            
            user = self.system.register_user(name)
            if user:
                messagebox.showinfo("Успех", f"Пользователь '{name}' (ID: {user.get_id()}) зарегистрирован!")
                self.clear_content()
                ttk.Label(self.content_frame, 
                         text=f"✓ Пользователь зарегистрирован\nID: {user.get_id()}").pack(pady=20)
            else:
                messagebox.showerror("Ошибка", "Не удалось зарегистрировать пользователя.")
        
        ttk.Button(frame, text="Зарегистрировать", command=register).pack(pady=20)

    def show_issue_book(self):
        """Показывает форму выдачи книги с Combobox."""
        self.clear_content()
        ttk.Label(self.content_frame, text="Выдать книгу", style="Title.TLabel").pack(pady=10)
        
        frame = ttk.Frame(self.content_frame)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Выбор пользователя
        ttk.Label(frame, text="Выберите пользователя:").pack(anchor="w", pady=(10, 0))
        users = self.system.get_users()
        user_options = [f"{u.get_name()} (ID: {u.get_id()})" for u in users]
        user_combo = ttk.Combobox(frame, values=user_options, state="readonly", width=38)
        user_combo.pack(fill=tk.X, pady=5)
        
        # Выбор книги
        ttk.Label(frame, text="Выберите книгу:").pack(anchor="w", pady=(10, 0))
        books = [b for b in self.system.get_books() if b.is_available()]
        book_options = [f"{b.get_title()} ({b.get_author().get_name()}, {b.get_year()})" for b in books]
        book_combo = ttk.Combobox(frame, values=book_options, state="readonly", width=38)
        book_combo.pack(fill=tk.X, pady=5)
        
        if not books:
            ttk.Label(frame, text="⚠️ Нет доступных книг!", foreground="red").pack(pady=10)
        
        if not users:
            ttk.Label(frame, text="⚠️ Нет зарегистрированных пользователей!", foreground="red").pack(pady=10)
        
        def issue():
            if not user_combo.get():
                messagebox.showerror("Ошибка", "Выберите пользователя!")
                return
            
            if not book_combo.get():
                messagebox.showerror("Ошибка", "Выберите книгу!")
                return
            
            try:
                user_id = int(user_combo.get().split("ID: ")[1].rstrip(")"))
                book_title = book_combo.get().split(" (")[0]
                book = next((b for b in self.system.get_books() if b.get_title() == book_title), None)
                
                if not book:
                    messagebox.showerror("Ошибка", "Книга не найдена.")
                    return
                
                loan = self.system.issue_book(user_id, book.get_id())
                if loan:
                    messagebox.showinfo("Успех", f"Книга выдана!\nВозврат до: {(loan.get_issue_date() + timedelta(days=14)).strftime('%d.%m.%Y')}")
                    self.show_list_loans()  # Автообновление
                else:
                    user = next((u for u in self.system.get_users() if u.get_id() == user_id), None)
                    if user and len(user.get_borrowed_books()) >= User.MAX_BOOKS:
                        messagebox.showerror("Ошибка", f"Пользователь уже взял максимум ({User.MAX_BOOKS}) книг!")
                    else:
                        messagebox.showerror("Ошибка", "Не удалось выдать книгу.")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка: {str(e)}")
        
        ttk.Button(frame, text="Выдать", command=issue).pack(pady=20)

    def show_return_book(self):
        """Показывает форму возврата книги с Combobox."""
        self.clear_content()
        ttk.Label(self.content_frame, text="Вернуть книгу", style="Title.TLabel").pack(pady=10)
        
        frame = ttk.Frame(self.content_frame)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        loans = self.system.get_active_loans()
        if not loans:
            ttk.Label(frame, text="Нет активных выдач!", foreground="red").pack(pady=20)
            ttk.Button(frame, text="Назад", command=lambda: self.show_list_loans()).pack(pady=10)
            return
        
        ttk.Label(frame, text="Выберите выдачу для возврата:").pack(anchor="w", pady=(10, 0))
        
        loan_options = [f"{l.get_book().get_title()} - {l.get_user().get_name()} (Выдана: {l.get_issue_date().strftime('%d.%m.%Y')})" 
                       for l in loans]
        loan_combo = ttk.Combobox(frame, values=loan_options, state="readonly", width=50)
        loan_combo.pack(fill=tk.X, pady=5)
        
        def return_book():
            if not loan_combo.get():
                messagebox.showerror("Ошибка", "Выберите выдачу!")
                return
            
            try:
                index = loan_combo.current()
                loan = loans[index]
                
                if self.system.return_book(loan.get_id()):
                    status = "ПРОСРОЧЕНО" if (datetime.now() - loan.get_issue_date()).days > 14 else "Вовремя"
                    messagebox.showinfo("Успех", f"Книга возвращена! ({status})")
                    self.show_list_loans()  # Автообновление
                else:
                    messagebox.showerror("Ошибка", "Не удалось вернуть книгу.")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка: {str(e)}")
        
        ttk.Button(frame, text="Вернуть", command=return_book).pack(pady=20)

    def show_list_books(self):
        """Показывает список книг с поиском и скроллбаром."""
        self.clear_content()
        ttk.Label(self.content_frame, text="Список книг", style="Title.TLabel").pack(pady=10)
        
        # Поиск
        search_frame = ttk.Frame(self.content_frame)
        search_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(search_frame, text="Поиск:").pack(side=tk.LEFT, padx=5)
        search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Таблица
        tree_frame = ttk.Frame(self.content_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        tree = ttk.Treeview(tree_frame, columns=("ID", "Название", "Автор", "Биография", "Год", "Статус"), 
                           show="headings", yscrollcommand=scrollbar.set)
        scrollbar.config(command=tree.yview)
        
        tree.heading("ID", text="ID")
        tree.heading("Название", text="Название")
        tree.heading("Автор", text="Автор")
        tree.heading("Биография", text="Биография")
        tree.heading("Год", text="Год")
        tree.heading("Статус", text="Статус")
        
        tree.column("ID", width=40)
        tree.column("Название", width=150)
        tree.column("Автор", width=100)
        tree.column("Биография", width=150)
        tree.column("Год", width=60)
        tree.column("Статус", width=80)
        
        tree.pack(fill=tk.BOTH, expand=True)
        
        def display_books(filter_text=""):
            tree.delete(*tree.get_children())
            books = self.system.get_books()
            if filter_text:
                books = self.system.find_book_by_title(filter_text)
            
            for book in books:
                status_tag = "доступна" if book.is_available() else "выдана"
                tree.insert("", "end", values=(
                    book.get_id(),
                    book.get_title(),
                    book.get_author().get_name(),
                    book.get_author().get_bio()[:30] + "..." if len(book.get_author().get_bio()) > 30 else book.get_author().get_bio(),
                    book.get_year(),
                    status_tag
                ), tags=(status_tag,))
            
            tree.tag_configure("доступна", foreground="green")
            tree.tag_configure("выдана", foreground="red")
        
        search_var.trace("w", lambda *args: display_books(search_var.get()))
        display_books()
        
        ttk.Button(self.content_frame, text="🔄 Обновить", command=lambda: display_books(search_var.get())).pack(pady=5)

    def show_list_loans(self):
        """Показывает список выдач с индикатором просрочки."""
        self.clear_content()
        ttk.Label(self.content_frame, text="Список выдач", style="Title.TLabel").pack(pady=10)
        
        tree_frame = ttk.Frame(self.content_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        tree = ttk.Treeview(tree_frame, columns=("ID", "Книга", "Пользователь", "Выдана", "Возврат до", "Статус"), 
                           show="headings", yscrollcommand=scrollbar.set)
        scrollbar.config(command=tree.yview)
        
        tree.heading("ID", text="ID")
        tree.heading("Книга", text="Книга")
        tree.heading("Пользователь", text="Пользователь")
        tree.heading("Выдана", text="Выдана")
        tree.heading("Возврат до", text="Возврат до")
        tree.heading("Статус", text="Статус")
        
        tree.column("ID", width=40)
        tree.column("Книга", width=150)
        tree.column("Пользователь", width=100)
        tree.column("Выдана", width=90)
        tree.column("Возврат до", width=90)
        tree.column("Статус", width=90)
        
        tree.pack(fill=tk.BOTH, expand=True)
        
        for loan in self.system.get_loans():
            if loan.get_return_date() is None:  # Только активные выдачи
                due_date = loan.get_issue_date() + timedelta(days=14)
                is_overdue = loan.is_overdue()
                status = "ПРОСРОЧЕНО ⚠️" if is_overdue else "OK"
                tag = "overdue" if is_overdue else "ok"
                
                tree.insert("", "end", values=(
                    loan.get_id(),
                    loan.get_book().get_title(),
                    loan.get_user().get_name(),
                    loan.get_issue_date().strftime('%d.%m.%Y'),
                    due_date.strftime('%d.%m.%Y'),
                    status
                ), tags=(tag,))
        
        tree.tag_configure("overdue", foreground="red", background="#ffcccc")
        tree.tag_configure("ok", foreground="green")
        
        ttk.Button(self.content_frame, text="🔄 Обновить", command=self.show_list_loans).pack(pady=5)

    def show_list_users(self):
        """Показывает список пользователей с поиском."""
        self.clear_content()
        ttk.Label(self.content_frame, text="Список пользователей", style="Title.TLabel").pack(pady=10)
        
        # Поиск
        search_frame = ttk.Frame(self.content_frame)
        search_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(search_frame, text="Поиск:").pack(side=tk.LEFT, padx=5)
        search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Таблица
        tree_frame = ttk.Frame(self.content_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        tree = ttk.Treeview(tree_frame, columns=("ID", "Имя", "Взятых книг"), 
                           show="headings", yscrollcommand=scrollbar.set)
        scrollbar.config(command=tree.yview)
        
        tree.heading("ID", text="ID")
        tree.heading("Имя", text="Имя")
        tree.heading("Взятых книг", text="Взятых книг")
        
        tree.column("ID", width=80)
        tree.column("Имя", width=200)
        tree.column("Взятых книг", width=100)
        
        tree.pack(fill=tk.BOTH, expand=True)
        
        def display_users(filter_text=""):
            tree.delete(*tree.get_children())
            users = self.system.get_users()
            if filter_text:
                users = self.system.find_user_by_name(filter_text)
            
            for user in users:
                tree.insert("", "end", values=(
                    user.get_id(),
                    user.get_name(),
                    len(user.get_borrowed_books())
                ))
        
        search_var.trace("w", lambda *args: display_users(search_var.get()))
        display_users()
        
        ttk.Button(self.content_frame, text="🔄 Обновить", command=lambda: display_users(search_var.get())).pack(pady=5)

    def show_edit_book(self):
        """Показывает форму редактирования книги."""
        self.clear_content()
        ttk.Label(self.content_frame, text="Редактировать книгу", style="Title.TLabel").pack(pady=10)
        
        frame = ttk.Frame(self.content_frame)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Выбор книги
        ttk.Label(frame, text="Выберите книгу:").pack(anchor="w", pady=(10, 0))
        books = self.system.get_books()
        book_options = [f"{b.get_title()} (ID: {b.get_id()})" for b in books]
        book_combo = ttk.Combobox(frame, values=book_options, state="readonly", width=40)
        book_combo.pack(fill=tk.X, pady=5)
        
        if not books:
            ttk.Label(frame, text="Нет книг для редактирования!", foreground="red").pack(pady=20)
            return
        
        selected_book = [None]
        
        def on_book_select(event=None):
            if not book_combo.get():
                return
            book_id = int(book_combo.get().split("ID: ")[1].rstrip(")"))
            selected_book[0] = next((b for b in books if b.get_id() == book_id), None)
            
            if selected_book[0]:
                title_entry.delete(0, tk.END)
                title_entry.insert(0, selected_book[0].get_title())
                year_entry.delete(0, tk.END)
                year_entry.insert(0, str(selected_book[0].get_year()))
                bio_text.delete("1.0", tk.END)
                bio_text.insert("1.0", selected_book[0].get_author().get_bio())
        
        book_combo.bind("<<ComboboxSelected>>", on_book_select)
        
        # Форма редактирования
        ttk.Label(frame, text="Новое название:").pack(anchor="w", pady=(15, 0))
        title_entry = ttk.Entry(frame, width=40)
        title_entry.pack(fill=tk.X, pady=5)
        
        ttk.Label(frame, text="Год издания:").pack(anchor="w", pady=(10, 0))
        year_entry = ttk.Entry(frame, width=40)
        year_entry.pack(fill=tk.X, pady=5)
        
        ttk.Label(frame, text="Биография автора:").pack(anchor="w", pady=(10, 0))
        bio_text = tk.Text(frame, height=4, width=40, font=("Helvetica", 10))
        bio_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        def save():
            if not selected_book[0]:
                messagebox.showerror("Ошибка", "Выберите книгу!")
                return
            
            title = title_entry.get().strip()
            year_str = year_entry.get().strip()
            bio = bio_text.get("1.0", tk.END).strip()
            
            try:
                year = int(year_str) if year_str else None
                if year and (year <= 0 or year > 2100):
                    raise ValueError("Год должен быть между 1 и 2100")
                
                if self.system.edit_book(selected_book[0].get_id(), title if title else None, 
                                        year, bio if bio else None):
                    messagebox.showinfo("Успех", "Книга отредактирована!")
                    self.show_list_books()
                else:
                    messagebox.showerror("Ошибка", "Не удалось отредактировать книгу.")
            except ValueError as e:
                messagebox.showerror("Ошибка", f"Неверный год: {str(e)}")
        
        ttk.Button(frame, text="Сохранить", command=save).pack(pady=10)
        ttk.Button(frame, text="Удалить", command=lambda: self._confirm_delete_book(selected_book)).pack(pady=5)
    
    def _confirm_delete_book(self, selected_book):
        """Подтверждает удаление книги."""
        if not selected_book[0]:
            messagebox.showerror("Ошибка", "Выберите книгу!")
            return
        
        if messagebox.askyesno("Подтверждение", f"Вы уверены, что хотите удалить '{selected_book[0].get_title()}'?"):
            if self.system.remove_book(selected_book[0].get_id()):
                messagebox.showinfo("Успех", "Книга удалена!")
                self.show_list_books()
            else:
                messagebox.showerror("Ошибка", "Не удалось удалить книгу.")

    def show_edit_user(self):
        """Показывает форму редактирования пользователя."""
        self.clear_content()
        ttk.Label(self.content_frame, text="Редактировать пользователя", style="Title.TLabel").pack(pady=10)
        
        frame = ttk.Frame(self.content_frame)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Выбор пользователя
        ttk.Label(frame, text="Выберите пользователя:").pack(anchor="w", pady=(10, 0))
        users = self.system.get_users()
        user_options = [f"{u.get_name()} (ID: {u.get_id()})" for u in users]
        user_combo = ttk.Combobox(frame, values=user_options, state="readonly", width=40)
        user_combo.pack(fill=tk.X, pady=5)
        
        if not users:
            ttk.Label(frame, text="Нет пользователей для редактирования!", foreground="red").pack(pady=20)
            return
        
        selected_user = [None]
        
        def on_user_select(event=None):
            if not user_combo.get():
                return
            user_id = int(user_combo.get().split("ID: ")[1].rstrip(")"))
            selected_user[0] = next((u for u in users if u.get_id() == user_id), None)
            
            if selected_user[0]:
                name_entry.delete(0, tk.END)
                name_entry.insert(0, selected_user[0].get_name())
        
        user_combo.bind("<<ComboboxSelected>>", on_user_select)
        
        # Форма редактирования
        ttk.Label(frame, text="Новое имя:").pack(anchor="w", pady=(15, 0))
        name_entry = ttk.Entry(frame, width=40)
        name_entry.pack(fill=tk.X, pady=5)
        
        def save():
            if not selected_user[0]:
                messagebox.showerror("Ошибка", "Выберите пользователя!")
                return
            
            name = name_entry.get().strip()
            if not name:
                messagebox.showerror("Ошибка", "Введите имя!")
                return
            
            if self.system.edit_user(selected_user[0].get_id(), name):
                messagebox.showinfo("Успех", "Пользователь отредактирован!")
                self.show_list_users()
            else:
                messagebox.showerror("Ошибка", "Не удалось отредактировать пользователя.")
        
        ttk.Button(frame, text="Сохранить", command=save).pack(pady=10)
        ttk.Button(frame, text="Удалить", command=lambda: self._confirm_delete_user(selected_user)).pack(pady=5)
    
    def _confirm_delete_user(self, selected_user):
        """Подтверждает удаление пользователя."""
        if not selected_user[0]:
            messagebox.showerror("Ошибка", "Выберите пользователя!")
            return
        
        if messagebox.askyesno("Подтверждение", f"Вы уверены, что хотите удалить '{selected_user[0].get_name()}'?"):
            if self.system.delete_user(selected_user[0].get_id()):
                messagebox.showinfo("Успех", "Пользователь удален!")
                self.show_list_users()
            else:
                messagebox.showerror("Ошибка", "Не удалось удалить пользователя.")

    def on_closing(self):
        """Закрывает приложение."""
        self.system.close()
        self.root.destroy()
        logger.info("Приложение закрыто")

if __name__ == "__main__":
    root = tk.Tk()
    app = LibraryApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
    root.mainloop()