import os
import tempfile
import unittest
import sqlite3
import importlib.util
from datetime import datetime, timedelta

# Загружаем модуль 1.py динамически (имя файла начинается с цифры, поэтому используем importlib)
MODULE_PATH = os.path.join(os.path.dirname(__file__), '1.py')
spec = importlib.util.spec_from_file_location('library_app', MODULE_PATH)
library_app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(library_app)

LibrarySystem = library_app.LibrarySystem
User = library_app.User
Author = library_app.Author
Book = library_app.Book
Loan = library_app.Loan

class TestLibrarySystem(unittest.TestCase):
    def setUp(self):
        # Создаем временную БД
        fd, path = tempfile.mkstemp(prefix='test_lib_', suffix='.db')
        os.close(fd)
        self.db_path = path
        self.system = LibrarySystem(db_name=self.db_path)
        # Очищаем демо-данные для контролируемого состояния
        cur = self.system._conn.cursor()
        cur.execute('DELETE FROM loans')
        cur.execute('DELETE FROM books')
        cur.execute('DELETE FROM authors')
        cur.execute('DELETE FROM users')
        cur.execute('DELETE FROM librarians')
        self.system._conn.commit()
        # Обновляем списки в памяти
        self.system._books = []
        self.system._users = []
        self.system._authors = []
        self.system._loans = []
        self.system._librarians = []

    def tearDown(self):
        try:
            self.system.close()
        except Exception:
            pass
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    # ---------- Пользователи ----------
    def test_register_edit_delete_user(self):
        # register_user
        user = self.system.register_user('Test User')
        self.assertIsNotNone(user)
        self.assertIn(user.get_id(), [u.get_id() for u in self.system.get_users()])

        # edit_user
        ok = self.system.edit_user(user.get_id(), 'New Name')
        self.assertTrue(ok)
        u = next((x for x in self.system.get_users() if x.get_id() == user.get_id()), None)
        self.assertIsNotNone(u)
        self.assertEqual(u.get_name(), 'New Name')

        # delete_user
        ok = self.system.delete_user(user.get_id())
        self.assertTrue(ok)
        self.assertIsNone(next((x for x in self.system.get_users() if x.get_id() == user.get_id()), None))

    # ---------- Книги ----------
    def test_add_remove_edit_find_book(self):
        title = 'Unique Book Title'
        author_name = 'Author X'
        bio = 'Author Bio'
        year = 2000

        # add_book
        added = self.system.add_book(title, author_name, bio, year)
        self.assertTrue(added)

        # Найдем книгу в БД
        cur = self.system._conn.cursor()
        cur.execute('SELECT id FROM books WHERE title=?', (title,))
        row = cur.fetchone()
        self.assertIsNotNone(row)
        book_id = row[0]

        # find_book_by_title (подстрока)
        found = self.system.find_book_by_title('Unique')
        self.assertTrue(any(b.get_id() == book_id for b in found))

        # edit_book
        new_title = 'Edited Title'
        new_year = 2010
        ok = self.system.edit_book(book_id, title=new_title, year=new_year, author_bio='New bio')
        self.assertTrue(ok)
        # reload book
        cur.execute('SELECT title, year FROM books WHERE id=?', (book_id,))
        r = cur.fetchone()
        self.assertIsNotNone(r)
        self.assertEqual(r[0], new_title)
        self.assertEqual(r[1], new_year)

        # remove_book
        ok = self.system.remove_book(book_id)
        self.assertTrue(ok)
        cur.execute('SELECT id FROM books WHERE id=?', (book_id,))
        self.assertIsNone(cur.fetchone())

    # ---------- Выдача и возврат ----------
    def test_issue_and_return_book(self):
        # создаем пользователя
        user = self.system.register_user('Borrower')
        self.assertIsNotNone(user)
        # создаем книгу
        title = 'Borrowable'
        self.system.add_book(title, 'Some Author', 'bio', 1999)
        cur = self.system._conn.cursor()
        cur.execute('SELECT id FROM books WHERE title=?', (title,))
        book_row = cur.fetchone()
        self.assertIsNotNone(book_row)
        book_id = book_row[0]

        # issue_book
        loan = self.system.issue_book(user.get_id(), book_id)
        self.assertIsNotNone(loan)
        # book status should be 'выдана'
        cur.execute('SELECT status FROM books WHERE id=?', (book_id,))
        status = cur.fetchone()[0]
        self.assertEqual(status, 'выдана')

        # return_book
        ok = self.system.return_book(loan.get_id())
        self.assertTrue(ok)
        cur.execute('SELECT status FROM books WHERE id=?', (book_id,))
        status2 = cur.fetchone()[0]
        self.assertEqual(status2, 'доступна')

    # ---------- User.borrow_book и return_book (локально) ----------
    def test_user_borrow_return_methods(self):
        u = User('Local', 123)
        a = Author(1, 'A')
        b = Book(1, 'B', a, 2001)
        self.assertTrue(u.borrow_book(b))
        self.assertIn(b, u.get_borrowed_books())
        self.assertTrue(u.return_book(b))
        self.assertNotIn(b, u.get_borrowed_books())

    # ---------- Loan.is_overdue ----------
    def test_loan_is_overdue(self):
        a = Author(1, 'A')
        b = Book(1, 'B', a, 2001)
        u = User('U', 1)
        old_date = datetime.now() - timedelta(days=20)
        loan = Loan(1, b, u, old_date)
        self.assertTrue(loan.is_overdue())
        # если вернуть — не просрочено
        loan.return_book(datetime.now())
        self.assertFalse(loan.is_overdue())

    # ---------- Загрузка данных из БД (_load_*) ----------
    def test_load_functions(self):
        # Добавим несколько записей
        u1 = self.system.register_user('L1')
        self.system.add_book('LoadBook1', 'LA', 'bio', 1991)
        self.system.add_book('LoadBook2', 'LB', 'bio2', 1992)

        # выдача
        cur = self.system._conn.cursor()
        cur.execute('SELECT id FROM books WHERE title=?', ('LoadBook1',))
        b1 = cur.fetchone()[0]
        loan = self.system.issue_book(u1.get_id(), b1)
        self.assertIsNotNone(loan)

        # создаем новый экземпляр системы чтобы проверить загрузку из БД
        new_sys = LibrarySystem(db_name=self.db_path)
        # проверяем загрузку
        books = new_sys.get_books()
        users = new_sys.get_users()
        loans = new_sys.get_loans()
        self.assertTrue(any('LoadBook1' in bk.get_title() for bk in books))
        self.assertTrue(any(u.get_name() == 'L1' for u in users))
        self.assertTrue(any(isinstance(l, Loan) for l in loans))
        new_sys.close()

if __name__ == '__main__':
    unittest.main()
