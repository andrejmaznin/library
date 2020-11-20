import sys
import sqlite3
import pymysql
import hashlib
import traceback

from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QGridLayout, QWidget, QTableWidget, QTableWidgetItem
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QRadioButton, QListWidgetItem
from PyQt5.QtWidgets import QMainWindow, QLabel, QLineEdit
from datetime import datetime, date, time, timedelta


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
        self.lb_p.hide()
        self.lb_e.hide()

        self.btn_cancel.clicked.connect(self.closer)
        self.btn_search.clicked.connect(self.show_found)
        self.lineEdit_name.editingFinished.connect(self.show_found)
        self.table_clients.itemClicked.connect(self.open_profile)
        self.lb_p.hide()
        self.lb_e.hide()

    def show_found(self):
        self.lb_nothing.hide()
        self.lb_e.hide()
        self.table_clients.setRowCount(0)
        name = self.lineEdit_name.text()
        if self.check_name(name):
            found = cur.execute(f"""SELECT * FROM reader where name like '%{name}%' order by name""").fetchall()
            if found != []:
                self.table_clients.setRowCount(len(found))
                for i in range(len(found)):
                    self.table_clients.setItem(i, 0, QTableWidgetItem(str(found[i][0])))
                    self.table_clients.setItem(i, 1, QTableWidgetItem(found[i][1]))
                    self.table_clients.setItem(i, 2, QTableWidgetItem(found[i][4]))
                    self.table_clients.setItem(i, 3, QTableWidgetItem(str(found[i][3])))
            elif found == []:
                self.lb_nothing.show()

    def check_name(self, text):
        try:
            if text.strip() != '':
                if '%' not in text:
                    return True
                else:
                    raise PercIn
            else:
                raise EmptyLE
        except PercIn:
            self.lb_p.show()
            return False
        except EmptyLE:
            self.lb_e.show()
            return False

    def closer(self):
        self.close()

    def open_profile(self):
        id = self.table_clients.item(self.sender().currentRow(), 1).text()
        self.profile = ClientProfile(id)
        id = self.table_clients.item(self.sender().currentRow(), 0).text()
        self.profile.lb_name.setText(self.table_clients.item(self.sender().currentRow(), 1).text())
        self.profile.lb_id.setText("id: " + id)
        self.profile.lb_date.setText(
            "Дата рождения: " + cur.execute(f"select date from reader where id={id}").fetchall()[0][0])
        self.profile.lb_address.setText("Адрес: " + self.table_clients.item(self.sender().currentRow(), 2).text())
        self.profile.lb_contact.setText(
            "Контактная информация: " + self.table_clients.item(self.sender().currentRow(), 3).text())
        info = cur.execute(f"select * from given where name={id}").fetchall()
        for i in range(len(info)):
            self.profile.table_books.insertRow(i)
        for i in range(len(info)):
            self.profile.table_books.setItem(i, 0, QTableWidgetItem(str(info[i][0])))
            self.profile.table_books.setItem(i, 1,
                                             QTableWidgetItem(cur.execute(
                                                 f"select name from books where ids={info[i][0]}").fetchall()[0][0]))
            self.profile.table_books.setItem(i, 2, QTableWidgetItem(info[i][2]))
            self.profile.table_books.setItem(i, 3, QTableWidgetItem(info[i][3]))
            ret = list(map(int, info[0][3].split(".")))
            given = list(map(int, info[0][2].split(".")))

            if datetime.date(datetime.now()) > date(ret[2], ret[1], ret[0]):
                print(datetime.date(datetime.now()))
                print(date(ret[2], ret[1], ret[0]))
                status = "Просрочена"
            else:
                status = "Выдана"
            self.profile.table_books.setItem(i, 4, QTableWidgetItem(status))

        self.profile.show()


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
                        self.lb_empty, self.lb_id_not_num]  # прятанье "лишних" элементов при открытии
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
        self.le_name.editingFinished.connect(self.show_found)
        self.btn_cancel.clicked.connect(self.closer)

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
        self.lb_id_not_num.hide()
        self.lb_nothing.hide()
        self.tableWidget.setRowCount(0)

        requirement = self.le_name.text()
        info = 0

        if self.rb_all.isChecked():
            info = cur.execute("select * from books").fetchall()
        if self.rb_id.isChecked() and self.check_id(requirement):
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
        if info != 0 and info != []:
            self.tableWidget.setRowCount(len(info))
            for i in range(len(info)):
                if info[i][0]:
                    book_is = "1"
                else:
                    book_is = "Нет в наличии"
                    # отображение найденного в таблице
                self.tableWidget.setItem(i, 0, QTableWidgetItem(str(info[i][0]) if info[i][6] != "TRUE" else "Выдана"))
                self.tableWidget.setItem(i, 1, QTableWidgetItem(info[i][1]))
                self.tableWidget.setItem(i, 2, QTableWidgetItem(info[i][2]))
                self.tableWidget.setItem(i, 3, QTableWidgetItem(str(info[i][3])))
                self.tableWidget.setItem(i, 4, QTableWidgetItem(info[i][4]))
                self.tableWidget.setItem(i, 5, QTableWidgetItem(str(info[i][5])))
                self.tableWidget.setItem(i, 6, QTableWidgetItem(book_is))
        elif info == []:
            self.lb_nothing.show()

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

    def check_id(self, id):
        try:
            if id.strip() != '':
                if id.isdigit():
                    return True
                else:
                    raise IsNotDigit
            else:
                raise EmptyLE
        except IsNotDigit:
            self.lb_id_not_num.show()
            return False
        except EmptyLE:
            print(1)
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
                        day, month, year = int(bday[0:2]), int(bday[3:5]), int(bday[6:])
                        if month > 12:
                            raise UnrealDate
                        elif (month == 2 and year % 4 != 0 and day > 28) or (
                                month == 2 and year % 4 == 0 and day < 29) or (
                                month in [4, 6, 9, 11] and day > 30) or day > 31:  # на реальность даты
                            raise UnrealDate
                        else:
                            d = datetime(year=year, month=month, day=day)
                            t = datetime.today()
                            if d > t:  # если дата еще не прошла
                                self.lb_wrong_bday.setText('')
                                return True
                            else:
                                raise UnrealDate
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
        except UnrealDate:
            self.lb_wrong_bday.setText('Несуществующая дата.')

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
            self.lb_wrong_contact.setText('Обязательное поле.')
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
            ids = []
            for i in range(number):
                cur.execute(f"""INSERT INTO books(name, author, year, genre, position)
                                                VALUES('{name}',
                                                '{author}', '{year}', '{genres}', '{str(shelf)}')""")
                con.commit()
                a = cur.execute(f"select ids from books where name='{name}'").fetchall()[i][0]
                ids.append(a)
            for i in range(len(ids)):
                self.listWidget.addItem(QListWidgetItem(str(ids[i])))

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

    def check_year(self, year_input):  # проверка года издания книги:
        try:
            if year_input.strip() != '':  # на пустую строку
                if year_input.isdigit() or year_input[1:].isdigit() and year_input[
                    0] == '-':  # на наличие символов кроме цифр
                    y = int(year_input)
                    d = datetime(year=y, month=1, day=1)
                    t = datetime.today()
                    if y <= 0 or d > t:  # на реальность года
                        raise UnrealDate
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
        except UnrealDate:
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
        self.book_s.hide()
        self.client_s.hide()
        self.initBookSearch()
        self.initClientSearch()
        self.btn_give.clicked.connect(self.give)
        self.btn_book_choose.clicked.connect(self.show_book_search)
        self.btn_client_choose.clicked.connect(self.show_client_search)

        self.book_id = None
        self.client_id = None

    def initClientSearch(self):
        self.lb_nothing_2.hide()
        self.lb_p.hide()
        self.lb_e.hide()
        self.btn_cancel.clicked.connect(self.closer)
        self.btn_search.clicked.connect(self.show_found_client)
        self.lineEdit_name.editingFinished.connect(self.show_found_client)
        self.table_clients.itemClicked.connect(self.set_client_id)

    def give(self):
        self.lb_empty_ids.setText('')
        ok = self.check_days()
        if ok:
            if self.book_id is not None and self.client_id is not None:
                self.clearer()
                if not cur.execute(f"select * from given where id={self.book_id}").fetchall():
                    print(self.le_days.text())
                    ret = datetime.date(datetime.now()) + timedelta(days=int(self.le_days.text()))
                    cur.execute(
                        f"insert into given(id, name, given, return) values({self.book_id}, {self.client_id}, '{datetime.now().strftime('%d.%m.%Y')}', '{ret.strftime('%d.%m.%Y')}')")
                    cur.execute(f"update books set given=TRUE where ids={self.book_id}")
                    self.lb_output.setText("Успешно.")
                    con.commit()
            else:
                self.lb_empty_ids.setText('Не выбран читатель или книга.')

    def check_name(self, text):
        try:
            if text.strip() != '':
                if '%' not in text:
                    return True
                else:
                    raise PercIn
            else:
                raise EmptyLE
        except PercIn:
            self.lb_p.show()
            return False
        except EmptyLE:
            self.lb_e.show()
            return False

    def check_days(self):
        try:
            days = self.le_days.text()
            if days.strip() != '':
                if days.isdigit():
                    if int(days) <= 31:
                        return True
                    else:
                        raise TooManyDays
                else:
                    raise IsNotDigit
            else:
                raise EmptyLE
        except EmptyLE:
            self.lb_wrong_days.setText('Введите количество дней.')
            return False
        except IsNotDigit:
            self.lb_wrong_days.setText('Допускаются только цифры.')
            return False
        except TooManyDays:
            self.lb_wrong_days.setText('Слишком много дней.')
            return False

    def show_found_client(self):
        self.table_clients.setRowCount(0)
        self.lb_p.hide()
        self.lb_e.hide()
        self.lb_nothing_2.hide()
        name = self.lineEdit_name.text()
        if self.check_name(name):
            found = cur.execute(f"""SELECT * FROM reader where name like '%{name}%' order by name""").fetchall()
            if found != []:
                for i in found:
                    rowPosition = self.table_clients.rowCount()
                    self.table_clients.insertRow(rowPosition)
                    self.table_clients.setItem(rowPosition, 0, QTableWidgetItem(str(i[0])))
                    self.table_clients.setItem(rowPosition, 1, QTableWidgetItem(i[1]))
                    self.table_clients.setItem(rowPosition, 2, QTableWidgetItem(i[4]))
                    self.table_clients.setItem(rowPosition, 3, QTableWidgetItem(str(i[3])))
            elif found == []:
                self.lb_nothing_2.show()

    def initBookSearch(self):
        self.widgets = [self.btn_id, self.lab_id, self.btn_name, self.lab_name, self.le_name,
                        self.btn_author, self.lab_author, self.lab_type, self.btn_type, self.ch_1,
                        self.ch_2, self.ch_3, self.ch_4, self.ch_5, self.ch_6, self.ch_7, self.ch_8, self.ch_9,
                        self.ch_10, self.lb_nothing, self.lab_all, self.lb_perc, self.lb_no_g,
                        self.lb_empty, self.lb_id_not_num]  # прятанье "лишних" элементов при открытии
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
        self.le_name.editingFinished.connect(self.show_found)
        self.btn_cancel.clicked.connect(self.closer)

        self.table_books.itemClicked.connect(self.set_book_id)

    def set_book_id(self):
        self.book_id = self.table_books.item(self.sender().currentRow(), 0).text()
        if self.book_id != "Выдана":
            self.lb_book_id.setText("Выдать книгу: " + self.table_books.item(self.sender().currentRow(), 1).text())
        self.book_s.hide()
        self.lb_empty_ids.setText('')

    def set_client_id(self):
        self.client_id = self.table_clients.item(self.sender().currentRow(), 0).text()
        self.lb_client_id.setText("Читателю: " + self.table_clients.item(self.sender().currentRow(), 1).text())
        self.client_s.hide()
        self.lb_empty_ids.setText('')

    def show_book_search(self):
        self.book_s.show()
        self.client_s.hide()
        self.lb_output.setText('')

    def show_client_search(self):
        self.book_s.hide()
        self.client_s.show()
        self.lb_output.setText('')

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
        self.lb_nothing.hide()
        self.lb_id_not_num.hide()
        self.table_books.clearContents()
        self.table_books.setRowCount(0)

        requirement = self.le_name.text()
        info = []
        not_ok = False

        if self.rb_all.isChecked():
            info = cur.execute("select * from books").fetchall()
            # not_ok = True
        if self.rb_id.isChecked() and self.check_id(requirement):
            if requirement:
                info = cur.execute(f"""select * from books where ids = {requirement}""").fetchall()
                not_ok = True
            else:
                info = []
        if self.rb_name.isChecked() and self.check_le(requirement):
            info = cur.execute(f"""select * from books where name like '%{requirement}%'""").fetchall()
            not_ok = True
        if self.rb_author.isChecked() and self.check_le(requirement):
            info = cur.execute(f"""select * from books where author like '%{requirement}%'""").fetchall()
            not_ok = True
        if self.rb_type.isChecked() and self.check_genre():
            not_ok = True
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
        info2 = list(filter(lambda b: b[6] != 1, info))
        self.table_books.setRowCount(len(info2))
        if info != []:
            self.table_books.setRowCount(len(info2))
            j = 0
            for i in range(len(info)):
                if info[i][6] != 1:
                    # отображение найденного в таблице
                    self.table_books.setItem(j, 0, QTableWidgetItem(str(info[i][0]) if info[i][6] != 1 else "Выдана"))
                    self.table_books.setItem(j, 1, QTableWidgetItem(info[i][1]))
                    self.table_books.setItem(j, 2, QTableWidgetItem(info[i][2]))
                    self.table_books.setItem(j, 3, QTableWidgetItem(str(info[i][3])))
                    self.table_books.setItem(j, 4, QTableWidgetItem(info[i][4]))
                    self.table_books.setItem(j, 5, QTableWidgetItem(str(info[i][5])))
                    j += 1
        elif info == [] and not_ok:
            self.lb_nothing.show()

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

    def check_id(self, id):
        try:
            if id.strip() != '':
                if id.isdigit():
                    return True
                else:
                    raise IsNotDigit
            else:
                raise EmptyLE
        except IsNotDigit:
            self.lb_id_not_num.show()
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

    def clearer(self):
        self.table_books.setRowCount(0)
        self.table_clients.setRowCount(0)
        self.lineEdit_name.clear()
        self.lb_book_id.setText('Выдать книгу:')
        self.lb_client_id.setText('Читателю:')
        for el in self.widgets:
            if 'id' in el.accessibleName():
                el.show()
        self.rb_id.setChecked(True)
        self.lb_wrong_days.setText('')

    def closer(self):
        self.close()


class ReturnBook(QWidget):  # сдача книг
    def __init__(self):
        super().__init__()
        uic.loadUi('ReturnBook.ui', self)
        self.initUI()

    def initUI(self):
        self.btn_return.clicked.connect(self.returner)
        self.le_book_id.editingFinished.connect(self.returner)
        self.btn_cancel.clicked.connect(self.closer)
        self.le_book_id.textChanged.connect(self.clearer)

    def returner(self):
        ok_book = self.check_book_id(self.le_book_id.text())  # вызов проверок

        if ok_book:
            # происходит удаление из таблицы вадачи
            id_return = int(self.le_book_id.text())
            cur.execute(f"update books set given=0 where ids={id_return}")
            con.commit()
            cur.execute(f"delete from given where id={id_return}")
            con.commit()
        self.lb_output.setText('Сдача произведена успешно, книга может быть помещена на полку.')

    def check_book_id(self, id):  # проверка id книги
        try:
            self.lb_wrong_book_id.setText('')
            if id.strip() != '':
                if cur.execute(f"select ids from books where ids={int(id)}").fetchall():
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

    def clearer(self):
        self.lb_output.setText('')

    def closer(self):
        self.close()


class ClientProfile(QWidget):
    def __init__(self, id):
        super().__init__()
        uic.loadUi('ClientProfile.ui', self)
        self.initUI(id)

    def initUI(self, id):
        # выставление данных читателя в форме, а также книг в таблице, если такие у него есть
        self.btn_cancel.clicked.connect(self.closer)

    def closer(self):
        self.close()


# исключения используемые при проверках
class WrongBirthDateFormat(Exception):
    pass


class WrongNameFormat(Exception):
    pass


class UnrealDate(Exception):
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


class IsNotDigit(Exception):
    pass


class TooManyDays(Exception):
    pass


if __name__ == '__main__':
    con = sqlite3.connect("books_db.sqlite")
    cur = con.cursor()
    app = QApplication(sys.argv)

    ex = Librarian()
    ex.show()
    sys.exit(app.exec_())
