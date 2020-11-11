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


# Github - done by Andrew
# Fixed contact info name
class Librarian(QMainWindow):
    def __init__(self):
        super().__init__()

        uic.loadUi('Librarian.ui', self)
        self.initUI()

    def initUI(self):
        self.btn_client_search.clicked.connect(self.open_client_search)
        self.btn_book_search.clicked.connect(self.open_book_search)
        self.btn_new_client.clicked.connect(self.open_new_client)
        self.btn_new_book.clicked.connect(self.open_new_book)

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


class ClientSearch(QWidget):
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


class BookSearch(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('BookSearch.ui', self)
        self.initUI()

    def initUI(self):
        self.widgets = [self.btn_id, self.lab_id, self.btn_name, self.lab_name, self.le_name,
                        self.btn_author, self.lab_author, self.lab_type, self.btn_type, self.ch_1,
                        self.ch_2, self.ch_3, self.ch_4, self.ch_5, self.ch_6, self.ch_7, self.ch_8, self.ch_9,
                        self.ch_10, self.lb_nothing]
        for el in self.widgets:
            if 'id' not in el.accessibleName():
                el.hide()
        self.rb_id.setChecked(True)

        self.rb_id.clicked.connect(self.hider)
        self.rb_name.clicked.connect(self.hider)
        self.rb_author.clicked.connect(self.hider)
        self.rb_type.clicked.connect(self.hider)
        self.btn_author.clicked.connect(self.show_found)
        self.btn_id.clicked.connect(self.show_found)
        self.btn_name.clicked.connect(self.show_found)
        self.btn_type.clicked.connect(self.show_found)
        self.btn_cancel.clicked.connect(self.closer)

    def hider(self):
        self.le_name.setText("")
        for el in self.widgets:
            if self.sender().accessibleName() in el.accessibleName():
                el.show()
            else:
                el.hide()

    def show_found(self):
        for i in range(self.tableWidget.rowCount()):
            self.tableWidget.removeRow(i)
        requirement = self.le_name.text()
        print(requirement)
        if self.rb_id.isChecked():
            info = cur.execute(f"""select * from books where ids like '%{requirement}%'""").fetchall()
        if self.rb_name.isChecked():
            info = cur.execute(f"""select * from books where lower(name) like '%{requirement.lower()}%'""").fetchall()
        if self.rb_author.isChecked():
            info = cur.execute(f"""select * from books where lower(author) like '%{requirement.lower()}%'""").fetchall()
        if self.rb_type.isChecked():
            genres = [i.text().lower() if i.isChecked() else "" for i in self.widgets[11:]]
            requirement = ""
            for i in genres[:-1]:
                requirement += "'%" + i + "%' and genre like"
            requirement += "'%" + genres[-1] + "%'"
            info = cur.execute(f"select * from books where genre like {requirement}").fetchall()
        print(info)
        for i in range(len(info)):
            if info[i][0]:
                num_prev = info[i][0].split(";")
                num_prev = list(filter( lambda b: b != "", num_prev))
                book_is = str(len(num_prev))

            else:
                book_is = "Нет в наличии"
            self.tableWidget.insertRow(i)
            self.tableWidget.setItem(i, 0, QTableWidgetItem(info[i][1]))
            self.tableWidget.setItem(i, 1, QTableWidgetItem(info[i][2]))
            self.tableWidget.setItem(i, 2, QTableWidgetItem(book_is))
            self.tableWidget.setItem(i, 3, QTableWidgetItem(" ".join(info[i][0].split(";"))))

    def closer(self):
        self.close()


class NewClient(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('NewClient.ui', self)
        self.initUI()

    def initUI(self):
        self.btn_input.clicked.connect(self.new_input)
        self.btn_cancel.clicked.connect(self.closer)

    def new_input(self):
        name_ok = self.check_name(self.le_name.text())
        date_ok = self.check_birthday(self.le_bday.text())
        address_ok = self.check_address(self.le_address.text())
        contact_ok = self.check_contact(self.le_contact.text())
        if name_ok and date_ok and address_ok and contact_ok:
            print("here")
            cur.execute(f"""INSERT INTO reader(id, name, date, address, info)
                        VALUES('{hashlib.md5(bytes(self.le_contact.text(), encoding='utf-8')).hexdigest()}', '{self.le_name.text()}',
                        '{self.le_bday.text()}', '{self.le_address.text()}', '{self.le_contact.text()}')""")
            self.lb_success.setText('Читатель успешно добавлен.')
            con.commit()
            self.le_name.clear()
            self.le_bday.clear()
            self.le_address.clear()
            self.le_contact.clear()

    def check_name(self, name):
        try:
            self.lb_success.setText('')
            if name.strip() != '':
                if ''.join(name.split()).isalpha():
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

    def check_birthday(self, bday):
        try:
            self.lb_success.setText('')
            if bday.strip() != '':
                if len(bday) == 10:
                    if bday[0:2].isdigit() and bday[3:5].isdigit() and bday[6:].isdigit() and bday[2] == '.' and bday[
                        5] == '.':
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

    def check_address(self, address):
        try:
            self.lb_wrong_address.setText('')
            if address.strip() != '':
                return True
            else:
                raise EmptyLE
        except EmptyLE:
            self.lb_wrong_address.setText('Обязтельное поле.')
            return False

    def check_contact(self, contact):
        try:
            self.lb_wrong_contact.setText('')
            if contact.strip() != '':
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
                        self.lb_name, self.lb_number, self.lb_shelf, self.lb_type, self.lb_wrong_number,
                        self.lb_wrong_year, self.lb_year, self.le_author, self.le_directory, self.le_name,
                        self.le_number, self.le_shelf, self.le_year]
        self.types = [self.ch_1, self.ch_2, self.ch_3, self.ch_4, self.ch_5, self.ch_6, self.ch_7, self.ch_8, self.ch_9,
                      self.ch_10]
        for el in self.widgets:
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

    def hider(self):
        for el in self.widgets:
            if self.sender().accessibleName() == el.accessibleName():
                el.show()
            else:
                el.hide()

    def input_file(self):
        pass
        # Катя - предполагается работа с документом
        # Катя - будем запариваться с проверкой верности формата директории?
        # или просто тогда уже найдет или нет?

    def input_form(self):
        self.lb_success.hide()

        ok_name = self.check_name(self.le_name.text())
        ok_author = self.check_author(self.le_author.text())
        ok_year = self.check_year(self.le_year.text())
        ok_type = self.check_type()
        ok_number = self.check_number(self.le_number.text())
        ok_shelf = self.check_shelf(self.le_shelf.text())

        if ok_name and ok_author and ok_year and ok_type and ok_number and ok_shelf:
            name = self.le_name.text()
            author = self.le_author.text()
            year = self.le_year.text()

            genres = [i.text().lower() if i.isChecked() else '' for i in self.widgets[2:12]]
            genres = ";".join(list(set(genres)))

            number = int(self.le_number.text())
            shelf = self.le_shelf.text()

            t = cur.execute(f"select ids from books where name = '{name}'").fetchall()
            num = 0

            if t:
                num = len(cur.execute(f"select ids from books where name = '{name}'").fetchall()[0][0].split(";"))

            ids = ";"
            for i in range(number):
                hash_i = hashlib.md5(bytes(name + str(num + i), encoding="utf-8")).hexdigest()
                ids += hash_i + ";"
            ids += ";"

            if num:
                cur_ids = cur.execute(f"select ids from books where name = '{name}'").fetchall()[0][0]
                final_ids = cur_ids + ids

                cur.execute(f"update books set ids='{final_ids}' where name='{name}'")
                con.commit()
            else:
                cur.execute(f"""INSERT INTO books(ids, name, author, year, genre, position)
                                            VALUES('{ids}', '{name}',
                                            '{author}', '{year}', '{genres}', '{str(shelf)}')""")
                con.commit()
            self.lb_success.show()

    def check_name(self, name):
        try:
            self.lb_wrong_name.setText('')
            if name.strip() != '':
                return True
            else:
                raise EmptyLE
        except EmptyLE:
            self.lb_wrong_name.setText('Обязательное поле.')
            return False

    def check_author(self, author):
        try:
            self.lb_wrong_author.setText('')
            if author.strip() != '':
                return True
            else:
                raise EmptyLE
        except EmptyLE:
            self.lb_wrong_author.setText('Обязательное поле.')
            return False

    def check_year(self, year):
        try:
            if year.strip() != '':
                if year.isdigit() or year[1:].isdigit() and year[0] == '-':
                    year = int(year)
                    if year <= 0:
                        raise UnrealYear
                    else:
                        self.lb_wrong_year.setText('')
                        return True
                else:
                    raise WrongYearFormat
            else:
                raise EmptyLE
        except EmptyLE:
            self.lb_wrong_year.setText('Обязтельное поле.')
            return False
        except UnrealYear:
            self.lb_wrong_year.setText('Несуществующий год.')
            return False
        except WrongYearFormat:
            self.lb_wrong_year.setText('Допускаются только цифры.')
            return False

    def check_type(self):
        try:
            ok = False
            for el in self.types:
                if el.isChecked():
                    ok = True
            print(ok)
            if ok:
                self.lb_wrong_type.hide()
                return True
            else:
                raise NoTypes
        except NoTypes:
            self.lb_wrong_type.show()
            return False

    def check_number(self, number):
        try:
            if number.strip() != '':
                if number.isdigit() or number[1:].isdigit() and number[0] == '-':
                    number = int(number)
                    if number <= 0:
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

    def check_shelf(self, shelf):
        try:
            self.lb_wrong_shelf.setText('')
            if shelf.strip() != '':
                return True
            else:
                raise EmptyLE
        except EmptyLE:
            self.lb_wrong_shelf.setText('Обязательное поле.')
            return False

    def closer(self):
        self.close()


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


class EmptyLE(Exception):
    pass


class NoTypes(Exception):
    pass


if __name__ == '__main__':
    con = sqlite3.connect("books_db.sqlite")
    cur = con.cursor()
    app = QApplication(sys.argv)
    ex = Librarian()
    ex.show()
    sys.exit(app.exec_())
