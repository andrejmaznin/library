import sys
import sqlite3
import pymysql
import hashlib
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QGridLayout, QWidget, QTableWidget, QTableWidgetItem
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QRadioButton
from PyQt5.QtWidgets import QMainWindow, QLabel, QLineEdit


def test():
    pass


class Librarian(QMainWindow):  # основное окно
    def __init__(self):
        super().__init__()

        uic.loadUi('Librarian.ui', self)
        self.initUI()

    def initUI(self):
        self.btn_client_search.clicked.connect(self.open_client_search)
        self.btn_book_search.clicked.connect(self.open_book_search)
        self.btn_new_client.clicked.connect(self.open_new_client)
        self.btn_new_book.clicked.connect(self.open_new_book)
        self.btn_give_book.clicked.connect(self.open_give_book)
        self.btn_return_book.clicked.connect(self.open_return_book)

    # функции открытия остальных форм
    def open_client_search(self):
        self.client_search = ClientSearch()
        self.client_search.show()

    def open_book_search(self):
        self.book_search = BookSearch()
        self.book_search.show()

    def open_new_client(self):
        self.new_client = NewClient()
        self.new_client.show()

    def open_new_book(self):
        self.new_book = NewBook()
        self.new_book.show()

    def open_give_book(self):
        self.give_book = GiveBook()
        self.give_book.show()

    def open_return_book(self):
        self.return_book = ReturnBook()
        self.return_book.show()


class ClientSearch(QWidget):  # поиск читателя по базе
    def __init__(self):
        super().__init__()
        uic.loadUi('ClientSearch.ui', self)
        self.initUI()

    def initUI(self):
        self.lb_nothing.hide()
        self.btn_cancel.clicked.connect(self.closer)
        self.btn_search.clicked.connect(self.show_found)

    def show_found(self):
        self.name = self.lineEdit_name.text()
        self.found = cur.execute(f"""SELECT * FROM reader where name like '%{self.name}%'""").fetchall()
        for self.i in self.found:
            rowPosition = self.table_clients.rowCount()
            self.table_clients.insertRow(rowPosition)
            self.table_clients.setItem(rowPosition, 0, QTableWidgetItem(self.i[0]))
            self.table_clients.setItem(rowPosition, 1, QTableWidgetItem(self.i[1]))
            self.table_clients.setItem(rowPosition, 2, QTableWidgetItem(self.i[4]))
            self.table_clients.setItem(rowPosition, 3, QTableWidgetItem(str(self.i[3])))

    def closer(self):
        self.close()


class BookSearch(QWidget):  # поиск книги по базе
    def __init__(self):
        super().__init__()
        uic.loadUi('BookSearch.ui', self)
        self.initUI()

    def initUI(self):
        self.widgets = [self.btn_id, self.lab_id, self.btn_name, self.lab_name, self.le_name,
                        self.btn_author, self.lab_author, self.lab_type, self.btn_type, self.ch_1,
                        self.ch_2, self.ch_3, self.ch_4, self.ch_5, self.ch_6, self.ch_7, self.ch_8, self.ch_9,
                        self.ch_10, self.lb_nothing, self.lab_all, self.lb_perc, self.lb_no_g,
                        self.lb_empty]  # прятанье "лишних" элементов при открытии
        self.genres = [self.ch_1, self.ch_2, self.ch_3, self.ch_4, self.ch_5, self.ch_6, self.ch_7, self.ch_8,
                       self.ch_9, self.ch_10, ]
        for el in self.widgets:
            if 'id' not in el.accessibleName():
                el.hide()
        self.rb_id.setChecked(True)

        self.rb_id.clicked.connect(self.hider)
        self.rb_name.clicked.connect(self.hider)
        self.rb_author.clicked.connect(self.hider)
        self.rb_type.clicked.connect(self.hider)
        self.rb_all.clicked.connect(self.hider)
        self.btn_author.clicked.connect(self.show_found)
        self.btn_id.clicked.connect(self.show_found)
        self.btn_name.clicked.connect(self.show_found)
        self.btn_type.clicked.connect(self.show_found)
        self.rb_all.clicked.connect(self.show_found)
        self.btn_cancel.clicked.connect(self.closer)

        self.tableWidget.itemClicked.connect(self.open_give_book)

    def open_give_book(self):
        print(self.sender().currentRow(), self.sender().currentColumn())
        self.give_book = GiveBook()
        # self.give_book.le_book_id.setText(self.tableWidget(self.sender().currentRow(), self.sender().currentColumn()).text())
        self.give_book.show()

    def hider(self):  # функция показа и прятанье элементов в соответствии с режимом поиска
        self.le_name.setText("")
        for el in self.widgets:
            if self.sender().accessibleName() in el.accessibleName():
                el.show()
            else:
                el.hide()

    def show_found(self):  # работа с базой
        self.lb_perc.hide()
        self.lb_no_g.hide()
        self.lb_empty.hide()
        for i in range(self.tableWidget.rowCount()):  # чистка таблицы перед отображением новых данных
            self.tableWidget.removeRow(i + 1)
            self.tableWidget.removeRow(i)
            self.tableWidget.removeRow(i - 1)

        requirement = self.le_name.text()
        info = 0
        if self.rb_all.isChecked():
            info = cur.execute("select * from books").fetchall()
        if self.rb_id.isChecked() and self.check_le(requirement):
            info = cur.execute(f"""select * from books where ids = {requirement}""").fetchall()
        if self.rb_name.isChecked() and self.check_le(requirement):
            info = cur.execute(f"""select * from books where name like '%{requirement}%'""").fetchall()
        if self.rb_author.isChecked() and self.check_le(requirement):
            info = cur.execute(f"""select * from books where author like '%{requirement}%'""").fetchall()
        if self.rb_type.isChecked() and self.check_genre():
            genres = []
            for i in self.genres:
                if i.isChecked():
                    genres.append(i.text().lower())
            requirement = ""
            if genres:
                for i in genres[:-1]:
                    requirement += "'%" + i + "%' and genre like"
                requirement += "'%" + genres[-1] + "%'"
                info = cur.execute(f"select * from books where genre like {requirement}").fetchall()
            else:
                info = cur.execute("select * from books").fetchall()
        if info != 0:
            for i in range(len(info)):
                self.tableWidget.insertRow(i)
            for i in range(len(info)):
                if info[i][0]:
                    book_is = "1"
                else:
                    book_is = "Нет в наличии"
                # отображение найденного в таблице
                self.tableWidget.setItem(i, 0, QTableWidgetItem(info[i][1]))
                self.tableWidget.setItem(i, 1, QTableWidgetItem(info[i][2]))
                self.tableWidget.setItem(i, 2, QTableWidgetItem(str(info[i][3])))
                self.tableWidget.setItem(i, 3, QTableWidgetItem(info[i][4]))
                self.tableWidget.setItem(i, 4, QTableWidgetItem(str(info[i][5])))
                self.tableWidget.setItem(i, 5, QTableWidgetItem(book_is))
                self.tableWidget.setItem(i, 6, QTableWidgetItem(str(info[i][0]) if info[i][6] != "TRUE" else "Выдана"))

    def check_le(self, text):
        try:
            if text.strip() != '':
                if '%' not in text:
                    return True
                else:
                    raise PercIn
            else:
                raise EmptyLE
        except PercIn:
            self.lb_perc.show()
            return False
        except EmptyLE:
            self.lb_empty.show()
            return False

    def check_genre(self):
        try:
            not_ok = True
            for el in self.genres:
                if el.isChecked():
                    not_ok = False
            if not_ok:
                raise NoTypes
            else:
                return True
        except NoTypes:
            self.lb_no_g.show()
            return False

    def closer(self):
        self.close()


class NewClient(QWidget):  # окно добавления нового читателя
    def __init__(self):
        super().__init__()
        uic.loadUi('NewClient.ui', self)
        self.initUI()

    def initUI(self):
        self.btn_input.clicked.connect(self.new_input)
        self.btn_cancel.clicked.connect(self.closer)

    def new_input(self):
        name_ok = self.check_name(self.le_name.text())  # вызов проверок соответствия ввода с необходимыми форматами
        date_ok = self.check_birthday(self.le_bday.text())
        address_ok = self.check_address(self.le_address.text())
        contact_ok = self.check_contact(self.le_contact.text())
        if name_ok and date_ok and address_ok and contact_ok:
            # Работы с базой, если проверки пройдены
            cur.execute(f"""INSERT INTO reader(name, date, address, info)
                        VALUES('{self.le_name.text()}',
                        '{self.le_bday.text()}', '{self.le_address.text()}', '{self.le_contact.text()}')""")
            self.lb_success.setText('Читатель успешно добавлен.')
            con.commit()
            self.le_name.clear()
            self.le_bday.clear()
            self.le_address.clear()
            self.le_contact.clear()

    def check_name(self, name):  # проверка имени:
        try:
            self.lb_success.setText('')
            if name.strip() != '':  # на пусткую строку
                if ''.join(name.split()).isalpha():  # на наличие символов кроме букв и пробелом
                    self.lb_wrong_name.setText('')
                    return True
                else:
                    raise WrongNameFormat
            else:
                raise EmptyLE
        except EmptyLE:
            self.lb_wrong_name.setText('Обязтельное поле.')
            return False
        except WrongNameFormat:
            self.lb_wrong_name.setText('Неверный формат имени.')
            return False

    def check_birthday(self, bday):  # проверка даты рождения:
        try:
            self.lb_success.setText('')
            if bday.strip() != '':  # на пустую строку
                if len(bday) == 10:  # на соответствие указаному формату по длине
                    if bday[0:2].isdigit() and bday[3:5].isdigit() and bday[6:].isdigit() and bday[2] == '.' and bday[
                        5] == '.':  # на соответствие в целом указаному формату
                        self.lb_wrong_bday.setText('')
                        return True
                    else:
                        raise WrongBirthDateFormat
                else:
                    raise WrongBirthDateFormat
            else:
                raise EmptyLE
        except EmptyLE:
            self.lb_wrong_bday.setText('Обязтельное поле.')
            return False
        except WrongBirthDateFormat:
            self.lb_wrong_bday.setText('Неверный формат даты.')
            return False

    def check_address(self, address):  # проверка адреса:
        try:
            self.lb_wrong_address.setText('')
            if address.strip() != '':  # на пустую строку
                return True
            else:
                raise EmptyLE
        except EmptyLE:
            self.lb_wrong_address.setText('Обязтельное поле.')
            return False

    def check_contact(self, contact):  # проверка контактов:
        try:
            self.lb_wrong_contact.setText('')
            if contact.strip() != '':  # на пустую строку
                return True
            else:
                raise EmptyLE
        except EmptyLE:
            self.lb_wrong_contact.setText('Обязтельное поле.')
            return False

    def closer(self):
        self.close()


class NewBook(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('NewBook.ui', self)
        self.initUI()

    def initUI(self):
        self.widgets = [self.btn_file_input, self.btn_form_input, self.ch_1, self.ch_2, self.ch_3, self.ch_4, self.ch_5,
                        self.ch_6, self.ch_7, self.ch_8, self.ch_9, self.ch_10, self.lb_author, self.lb_directory,
                        self.lb_name, self.lb_number, self.lb_shelf, self.lb_type,
                        self.lb_wrong_year, self.lb_year, self.le_author, self.le_directory, self.le_name,
                        self.le_number, self.le_shelf, self.le_year]  # сбор элемнтов для "прятанья"

        self.types = [self.ch_1, self.ch_2, self.ch_3, self.ch_4, self.ch_5, self.ch_6, self.ch_7, self.ch_8, self.ch_9,
                      self.ch_10]  # сбор элемнтов для удобного считывания жанров

        self.errors = [self.lb_wrong_author, self.lb_wrong_name, self.lb_wrong_number, self.lb_error,
                       self.lb_wrong_number, self.lb_wrong_shelf, self.lb_wrong_type, self.lb_wrong_year]

        for el in self.widgets:  # прятанье элементов
            if 'form' not in el.accessibleName():
                el.hide()
        self.lb_wrong_type.hide()
        self.lb_success.hide()

        self.rb_form.setChecked(True)
        self.rb_form.clicked.connect(self.hider)
        self.rb_file.clicked.connect(self.hider)

        self.btn_cancel.clicked.connect(self.closer)
        self.btn_file_input.clicked.connect(self.input_file)
        self.btn_form_input.clicked.connect(self.input_form)

    def hider(self):  # функция прятанья и показа в соответсвии с выбранным режимом
        for el in self.widgets:
            if self.sender().accessibleName() == el.accessibleName():
                el.show()
            else:
                el.hide()
        for el in self.errors:
            el.setText('')

    def input_file(self):  # добавление книг через уже готовый документ
        self.lb_success.hide()
        self.lb_error.setText('')
        if self.check_directory(self.le_directory.text()):
            path = self.le_directory.text()
            con_input = sqlite3.connect(path)
            cur_input = con_input.cursor()
            info = cur_input.execute("select * from books").fetchall()

            for i in range(len(info)):
                cur.execute(f"""insert into books(ids, name, author, year, genre, position)
                                                VALUES('{info[i][0]}', '{info[i][1]}',
                                                '{info[i][2]}', '{info[i][3]}', '{info[i][4]}', '{str(info[i][5])}')""")
                con.commit()
            self.lb_success.show()

    def input_form(self):  # добавление книг вручную
        self.lb_success.hide()

        ok_name = self.check_name(self.le_name.text())  # вызов проверок полей
        ok_author = self.check_author(self.le_author.text())
        ok_year = self.check_year(self.le_year.text())
        ok_type = self.check_type()
        ok_number = self.check_number(self.le_number.text())
        ok_shelf = self.check_shelf(self.le_shelf.text())

        if ok_name and ok_author and ok_year and ok_type and ok_number and ok_shelf:  # добавление в базу, если проверки пройдены
            name = self.le_name.text()
            author = self.le_author.text()
            year = self.le_year.text()

            genres = [i.text().lower() if i.isChecked() else '' for i in self.widgets[2:12]]
            genres = ";".join(list(set(genres)))

            number = int(self.le_number.text())
            shelf = self.le_shelf.text()
            for i in range(number):
                cur.execute(f"""INSERT INTO books(name, author, year, genre, position)
                                                VALUES('{name}',
                                                '{author}', '{year}', '{genres}', '{str(shelf)}')""")
                con.commit()
        self.lb_success.show()

    def check_directory(self, text):
        try:
            if text.strip() != '':
                if text.split('.')[-1] == 'sqlite':
                    return True
                else:
                    raise WrongDataFormat
            else:
                raise EmptyLE
        except EmptyLE:
            self.lb_error.setText('Введите путь.')
            return False
        except WrongDataFormat:
            self.lb_error.setText('Неподдерживаемый формат базы.')
            return False

    def check_name(self, name):  # проверка названия книги:
        try:
            self.lb_wrong_name.setText('')
            if name.strip() != '':  # на пустую строку
                return True
            else:
                raise EmptyLE
        except EmptyLE:
            self.lb_wrong_name.setText('Обязательное поле.')
            return False

    def check_author(self, author):  # проверка имени автора книги:
        try:
            self.lb_wrong_author.setText('')
            if author.strip() != '':  # на пустую строку
                return True
            else:
                raise EmptyLE
        except EmptyLE:
            self.lb_wrong_author.setText('Обязательное поле.')
            return False

    def check_year(self, year):  # проверка года издания книги:
        try:
            if year.strip() != '':  # на пустую строку
                if year.isdigit() or year[1:].isdigit() and year[0] == '-':  # на наличие символов кроме цифр
                    year = int(year)
                    if year <= 0:  # на реальность года
                        raise UnrealYear
                    else:
                        self.lb_wrong_year.setText('')
                        return True
                else:
                    raise WrongYearFormat
            else:
                raise EmptyLE
        except EmptyLE:
            self.lb_wrong_year.setText('Обязательное поле.')
            return False
        except UnrealYear:
            self.lb_wrong_year.setText('Несуществующий год.')
            return False
        except WrongYearFormat:
            self.lb_wrong_year.setText('Допускаются только цифры.')
            return False

    def check_type(self):  # проверка жанром книги:
        try:
            ok = False  # на выбор хотя бы одного
            for el in self.types:
                if el.isChecked():
                    ok = True
            if ok:
                self.lb_wrong_type.hide()
                return True
            else:
                raise NoTypes
        except NoTypes:
            self.lb_wrong_type.show()
            return False

    def check_number(self, number):  # проверка количества добавляемых одинаковых книг:
        try:
            if number.strip() != '':  # на пустую строку
                if number.isdigit() or number[1:].isdigit() and number[0] == '-':  # на наличие посторонних символов
                    number = int(number)
                    if number <= 0:  # на натуральность числа
                        raise NotNaturalNumber
                    else:
                        self.lb_wrong_number.setText('')
                        return True
                else:
                    pass
                    raise WrongNumberFormat
            else:
                raise EmptyLE
        except EmptyLE:
            self.lb_wrong_number.setText('Обязтельное поле.')
            return False
        except NotNaturalNumber:
            self.lb_wrong_number.setText('Не натуральное число.')
            return False
        except WrongNumberFormat:
            self.lb_wrong_number.setText('Допускаются только цифры.')
            return False

    def check_shelf(self, shelf):  # проверка номера стеллажа, где книги будут расположены
        try:
            self.lb_wrong_shelf.setText('')
            if shelf.strip() != '':  # на пустую строку
                return True
            else:
                raise EmptyLE
        except EmptyLE:
            self.lb_wrong_shelf.setText('Обязательное поле.')
            return False

    def closer(self):
        self.close()


class GiveBook(QWidget):  # выдача книг
    def __init__(self):
        super().__init__()
        uic.loadUi('GiveBook.ui', self)
        self.initUI()

    def initUI(self):
        self.btn_give.clicked.connect(self.give)
        self.btn_cancel.clicked.connect(self.closer)

    def give(self):
        ok_book = self.check_book_id(self.le_book_id.text())  # вызов проверок
        ok_client = self.check_client_id(self.le_client_id.text())
        if ok_book and ok_client:
            # происходит добавление в таблицу, что книга выдана
            id_to_give = self.le_book_id.text()

            client_to_give = self.le_client_id.text()
            cur_ids = str(cur.execute(f"select ids from books where ids like '%{id_to_give}%'").fetchall()[0][0]).split(
                ";")
            if type(cur_ids) != list:
                cur_ids = [cur_ids]

            position = cur_ids.index(id_to_give)
            cur_ids[position] += "/given/"
            cur_ids = ";".join(cur_ids)

            cur.execute(f"update books set ids='{cur_ids}' where ids like '%{id_to_give}%'")
            con.commit()
            client_name = cur.execute(f"select name from reader where id='{client_to_give}'").fetchall()[0][0]
            cur.execute(f"insert into given(id, name) values('{id_to_give}', '{client_name}')")
            con.commit()
            self.lb_output.setText('Книга выдана читателю.')

    def check_book_id(self, id):  # проверка id книги
        try:
            self.lb_wrong_book_id.setText('')
            if id.strip() != '':  # на пустую строку

                if cur.execute(
                        f"select ids from books where ids like '%{id}%'").fetchall():
                    return True
                else:
                    raise NoSuchID
            else:
                raise EmptyLE
        except EmptyLE:
            self.lb_wrong_book_id.setText('Обязательное поле.')
            return False
        except NoSuchID:
            self.lb_wrong_book_id.setText('Такого id нет')
            return False

    def check_client_id(self, id):  # проверка id читателя
        try:
            self.lb_wrong_client_id.setText('')
            if id.strip() != '':  # на пустую строку
                return True
            else:
                raise EmptyLE
        except EmptyLE:
            self.lb_wrong_client_id.setText('Обязательное поле.')
            return False

    def closer(self):
        self.close()


class ReturnBook(QWidget):  # сдача книг
    def __init__(self):
        super().__init__()
        uic.loadUi('ReturnBook.ui', self)
        self.initUI()

    def initUI(self):
        self.btn_return.clicked.connect(self.returner)
        self.btn_cancel.clicked.connect(self.closer)

    def returner(self):
        ok_book = self.check_book_id(self.le_book_id.text())  # вызов проверок
        ok_client = self.check_client_id(self.le_client_id.text())
        if ok_book and ok_client:
            # происходит удаление из таблицы вадачи
            id_return = self.le_book_id.text()
            reader_return = self.le_client_id.text()
            cur_ids = cur.execute(f"select ids from books where ids like '%{id_return}/given/%'").fetchall()[0][
                0].split(";")

            if cur_ids:
                position = cur_ids.index(id_return + "/given/")
                cur_ids[position] = id_return
                cur_ids = ";".join(cur_ids)
                cur.execute(f"update books set ids='{cur_ids}' where ids like '%{id_return}/given/%'")
                con.commit()
                cur.execute(f"delete from given where id='{id_return}'")
                con.commit()
            self.lb_output.setText('Сдача произведена успешно, книга может быть помещена на полку.')

    def check_book_id(self, id):  # проверка id книги
        try:
            self.lb_wrong_book_id.setText('')
            if id.strip() != '':

                if cur.execute(f"select ids from books where ids like '%{id.strip()}/given/%'").fetchall():
                    return True
                else:
                    raise NoSuchID
                # на пустую строку
            else:
                raise EmptyLE
        except EmptyLE:
            self.lb_wrong_book_id.setText('Обязательное поле.')
            return False
        except NoSuchID:
            self.lb_wrong_book_id.setText('Такого id нет')
            return False

    def check_client_id(self, id):  # проверка id читателя
        try:
            self.lb_wrong_client_id.setText('')
            if id.strip() != '':  # на пустую строку
                return True
            else:
                raise EmptyLE
        except EmptyLE:
            self.lb_wrong_client_id.setText('Обязательное поле.')
            return False

    def closer(self):
        self.close()


# исключения используемые при проверках
class WrongBirthDateFormat(Exception):
    pass


class WrongNameFormat(Exception):
    pass


class UnrealYear(Exception):
    pass


class WrongYearFormat(Exception):
    pass


class WrongNumberFormat(Exception):
    pass


class NotNaturalNumber(Exception):
    pass


class EmptyLE(Exception):  # ошибка: пустое поле ввода
    pass


class NoSuchID(Exception):
    pass


class NoTypes(Exception):
    pass


class PercIn(Exception):
    pass


class WrongDataFormat(Exception):
    pass


if __name__ == '__main__':
    con = sqlite3.connect("books_db.sqlite")
    cur = con.cursor()

    app = QApplication(sys.argv)
    ex = Librarian()
    ex.show()
    sys.exit(app.exec_())
