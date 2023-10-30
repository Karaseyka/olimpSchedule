import sys
import csv
import sqlite3
import datetime

from PyQt5 import uic
from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidgetItem, QHBoxLayout, QLabel, QWidget, QVBoxLayout, \
    QFrame, QMessageBox


class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('start.ui', self)
        self.start_but.clicked.connect(self.run)

    def run(self):
        self.to_auth = Authentication()
        self.to_auth.show()
        self.close()


class Authentication(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("auth.ui", self)
        self.okButton.clicked.connect(self.run)

    def run(self):
        dlg = QMessageBox(self)
        dlg.setWindowTitle("Подтвердите ввод данных")
        dlg.setText("Вы увернны что хотите сохранить данные")
        dlg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        dlg.setIcon(QMessageBox.Question)
        button = dlg.exec()
        if button == QMessageBox.Yes:
            print("Yes!")
            con = sqlite3.connect("olimp.sqlite")
            cur = con.cursor()
            cur.execute(f'INSERT INTO user (name, class, birth, insession) VALUES (?, ?, ?, ?)',
                        (self.nameEdit.text(), int(self.classEdit.text()), self.birthEdit.text(), 1))
            con.commit()
            con.close()
            self.to_main = MainPG()
            self.to_main.show()
            self.close()


class MainPG(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("mainDis.ui", self)
        self.olimps = csv_getter()
        self.for_list()
        self.listWidget.setStyleSheet('QListWidget::item { border: 1px solid black; } QListWidget::item:selected { '
                                      'background: lightblue; }')
        self.user = get_user()
        self.name.setText(self.user[1])
        self.clas.setText(str(self.user[2]))
        date_time_str = self.user[3]
        date_time_obj = datetime.datetime.strptime(date_time_str, '%d.%m.%Y')
        self.birth.setDate(date_time_obj.date())
        self.savech.clicked.connect(self.save)

    def save(self):
        connection = sqlite3.connect('olimp.sqlite')
        cursor = connection.cursor()
        cursor.execute('UPDATE user SET name = ?, class = ?, birth = ? WHERE id = ?',
                       (self.name.text(), self.clas.text(), self.birth.text(), self.user[0]))

        # Сохраняем изменения и закрываем соединение
        connection.commit()
        connection.close()

    def for_list(self):
        for ship_data in self.olimps:
            item = QListWidgetItem()
            item.setSizeHint(QSize(200, 100))
            widget = get_item_wight(ship_data)  # Call the above function to get the corresponding
            self.listWidget.addItem(item)  # Add item
            self.listWidget.setItemWidget(item, widget)


def get_item_wight(olimp):
    frame = QFrame()
    layout_main = QVBoxLayout()
    layout_main.addWidget(QLabel(olimp[0]))
    layout_main.addWidget(QLabel("Описание: " + olimp[1]))
    layout_main.addWidget(QLabel("Уровень: " + olimp[2]))
    layout_main.addWidget(QLabel("Профиль: " + olimp[3]))
    frame.setLayout(layout_main)
    return frame


def csv_getter():
    olimps = []
    with open('olimps.csv', newline="") as csvfile:
        reader = csv.reader(csvfile, delimiter=';', quotechar='"')
        olimps = list(reader)
    csvfile.close()
    with open('prof.csv', newline="") as csvfile:
        reader = csv.reader(csvfile, delimiter=';', quotechar='"')
        prof = dict(reader)
    csvfile.close()
    for el in olimps:
        el[3] = prof[el[3]]
    return olimps


def get_user():
    con = sqlite3.connect("olimp.sqlite")
    cur = con.cursor()
    user = cur.execute("SELECT * FROM user").fetchall()
    con.commit()
    con.close()
    if len(user) != 0:
        return user[0]
    return False


if __name__ == '__main__':
    app = QApplication(sys.argv)
    if not get_user():
        ex = MyWidget()
    else:
        ex = MainPG()
    ex.show()
    sys.exit(app.exec_())
