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

    def open_client_search(self):
        self.client_search = ClientSearch()
        self.client_search.show()

    def open_book_search(self):
        self.book_search = BookSearch()
        self.book_search.show()

    def open_new_client(self):
        self.new_client = NewClient()
        self.new_client.show()


class ClientSearch(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('ClientSearch.ui', self)
        self.initUI()

    def initUI(self):
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
                        self.ch_2, self.ch_3, self.ch_4, self.ch_5, self.ch_6]
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
        for i in range(len(info)):
            if info[i][0]:
                book_is = str(len(info[i][0].split(";")))

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

    def new_input(self):
        name_ok = self.check_name(self.le_name.text())
        date_ok = self.check_birthday(self.le_bday.text())
        if name_ok and date_ok:
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
            if ''.join(name.split()).isalpha():
                self.lb_wrong_name.setText('')
                return True
            else:
                raise WrongNameFormat
        except WrongNameFormat:
            self.lb_wrong_name.setText('Неверный формат имени.')
            return False

    def check_birthday(self, bday):
        try:
            self.lb_success.setText('')
            if len(bday) == 10:
                if bday[0:2].isdigit() and bday[3:5].isdigit() and bday[6:].isdigit() and bday[2] == '.' and bday[
                    5] == '.':
                    self.lb_wrong_bday.setText('')
                    return True
                else:
                    raise WrongBirthDateFormat
            else:
                raise WrongBirthDateFormat
        except WrongBirthDateFormat:
            self.lb_wrong_bday.setText('Неверный формат даты.')
            return False


class WrongBirthDateFormat(Exception):
    pass


class WrongNameFormat(Exception):
    pass


if __name__ == '__main__':
    con = sqlite3.connect("books_db.sqlite")
    cur = con.cursor()

    app = QApplication(sys.argv)
    ex = Librarian()
    ex.show()
    sys.exit(app.exec_())
