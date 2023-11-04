import sys
import csv
import sqlite3
import datetime
from PyQt5 import uic
from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidgetItem, QHBoxLayout, QLabel, QWidget, QVBoxLayout, \
    QFrame, QMessageBox, QListWidget, QInputDialog, QLineEdit, QPushButton


class WelcomePG(QMainWindow):
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
        self.que = []
        uic.loadUi("mainDis.ui", self)
        self.olimps = csv_getter()
        self.for_list()
        self.listWidget.setStyleSheet('QListWidget::item { border: 1px solid black; } QListWidget::item:selected { '
                                      'background: lightblue; }')
        self.listWidget.itemClicked.connect(self.run)
        self.user = get_user()
        self.name.setText(self.user[1])
        self.clas.setText(str(self.user[2]))
        date_time_str = self.user[3]
        date_time_obj = datetime.datetime.strptime(date_time_str, '%d.%m.%Y')
        self.birth.setDate(date_time_obj.date())
        self.savech.clicked.connect(self.save)
        self.for_list_added()
        self.listWidget2.setStyleSheet('QListWidget::item { border: 1px solid black; } QListWidget::item:selected { '
                                       'background: lightblue; }')
        self.listWidget2.itemClicked.connect(self.run_added)

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
            widget = get_item_wight(ship_data)
            self.listWidget.addItem(item)
            self.listWidget.setItemWidget(item, widget)

    def for_list_added(self):
        connection = sqlite3.connect('olimp.sqlite')
        cursor = connection.cursor()
        added_olimps = cursor.execute("""SELECT name, olid, date, time, olimpsus.id FROM olimpsus, status
        WHERE status.id = olimpsus.status""").fetchall()
        connection.commit()
        connection.close()
        for ship_data in added_olimps:
            item = QListWidgetItem()
            item.setSizeHint(QSize(200, 220))
            widget = self.get_item_added(ship_data, self.olimps)
            self.listWidget2.addItem(item)
            self.listWidget2.setItemWidget(item, widget)

    def run(self, item):
        x = self.listWidget.indexFromItem(item).row()  # индекс выбранного элемента
        self.to_prewatch = Prewatch(self.olimps[x], x, self)
        if len(self.que) == 0:
            self.que.append(self.to_prewatch)
            self.to_prewatch.show()
        else:
            self.que[0].close()
            self.que = [self.to_prewatch]
            self.to_prewatch.show()

    def run_added(self):
        pass

    def get_item_added(self, olimp, olimps):
        frame = QFrame()
        layout_main = QVBoxLayout()
        layout_main.addWidget(QLabel(olimps[olimp[1]][0]))
        layout_main.addWidget(QLabel("Дата: " + olimp[2]))
        layout_main.addWidget(QLabel("Время: " + olimp[3]))
        layout_main.addWidget(QLabel("Статаус: " + olimp[0]))
        layout_sec = QHBoxLayout()
        but = QPushButton("Изменить")
        layout_sec.addWidget(but)
        but.clicked.connect(lambda: self.change(olimp))
        but_del = QPushButton("Удалить")
        layout_sec.addWidget(but_del)
        but_del.clicked.connect(lambda: self.delete(olimp))
        layout_main.addLayout(layout_sec)
        frame.setLayout(layout_main)
        return frame

    def change(self, olimp):
        self.to_prewatch = Prewatch(self.olimps[olimp[1]], olimp[1], self, olimp[4])
        self.to_prewatch.show()

    def delete(self, olimp):
        connection = sqlite3.connect('olimp.sqlite')
        cursor = connection.cursor()
        cursor.execute("DELETE FROM olimpsus WHERE id = ?", (olimp[4], ))
        connection.commit()
        connection.close()
        self.mn_reload = MainPG()
        self.mn_reload.show()
        self.close()


class Prewatch(QMainWindow):
    def __init__(self, olimp, num, mn, is_update=-1):
        super().__init__()
        uic.loadUi("prewatch.ui", self)
        self.cur_status = "0"
        self.olimp = olimp
        self.num = num
        self.is_update = is_update
        self.mn = mn
        self.olimpName.setText(olimp[0])
        self.olimpDesc.setText("Описание: " + olimp[1])
        self.olimpLev.setText("Уровень: " + olimp[2])
        self.profil.setText("Профиль: " + olimp[3])
        self.connection = sqlite3.connect('olimp.sqlite')
        self.cur = self.connection.cursor()
        st = self.cur.execute("SELECT * FROM status").fetchall()
        self.connection.commit()
        for i in st:
            self.comboBox.addItem(i[1])
        self.addstut.clicked.connect(self.addStut)
        self.comboBox.activated.connect(self.onActivated)
        self.accept.clicked.connect(self.run)

    def run(self):
        if self.is_update == -1:
            self.cur.execute(f'INSERT INTO olimpsus (status, olid, date, time) VALUES (?, ?, ?, ?)',
                             (int(self.cur_status) + 1, int(self.num), self.dateEdit.text(), self.timeEdit.text()))
            self.connection.commit()
            self.mn.close()
        else:
            self.cur.execute('UPDATE olimpsus SET status = ?, olid = ?, date = ?, time = ? WHERE id = ?',
                             (int(self.cur_status) + 1, int(self.num), self.dateEdit.text(), self.timeEdit.text(),
                              self.is_update))
            self.connection.commit()
            self.mn.close()
        self.close()
        self.newMN = MainPG()
        self.newMN.show()

    def onActivated(self, text):
        self.cur_status = text

    def addStut(self):
        newstatus, ok = QInputDialog.getText(self, "Добавление статуса", "Введите название статуса", QLineEdit.Normal)
        if ok:
            try:
                connection = sqlite3.connect('olimp.sqlite')
                cur = connection.cursor()
                cur.execute(f'INSERT INTO status (name) VALUES (?)', (newstatus,))
                connection.commit()
                connection.close()
                self.rePre = Prewatch(self.olimp, self.num, self.mn)
                self.rePre.show()
                self.close()
            except sqlite3.Error as error:
                print("Ошибка при работе с SQLite", error)


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
    connection = sqlite3.connect('olimp.sqlite')
    cur = connection.cursor()
    user = cur.execute("SELECT * FROM user").fetchall()
    connection.commit()
    connection.close()
    if len(user) != 0:
        return user[0]
    return False


if __name__ == '__main__':
    app = QApplication(sys.argv)
    if not get_user():
        ex = WelcomePG()
    else:
        ex = MainPG()
    ex.show()
    sys.exit(app.exec_())
