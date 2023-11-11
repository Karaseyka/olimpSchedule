import sys
import csv
import sqlite3
import datetime
from PyQt5 import uic
from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QListWidgetItem, QHBoxLayout, QLabel, QVBoxLayout, \
    QFrame, QMessageBox, QInputDialog, QLineEdit, QPushButton
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtChart import *


class WelcomePG(QMainWindow):  # экран для новых пользователей
    def __init__(self):  # формирование окна
        super().__init__()
        uic.loadUi('start.ui', self)
        self.start_but.clicked.connect(self.run)

    def run(self):  # переход на окно авторизации
        self.to_auth = Authentication()
        self.to_auth.show()
        self.close()


class Authentication(QMainWindow):  # экран авторизации
    def __init__(self):  # формирование окна
        super().__init__()
        uic.loadUi("auth.ui", self)
        self.okButton.clicked.connect(self.run)

    def run(self):  # Вывод диалога для и переход в профиль
        dlg = QMessageBox(self)
        dlg.setWindowTitle("Подтвердите ввод данных")
        dlg.setText("Вы увернны что хотите сохранить данные")
        dlg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        dlg.setIcon(QMessageBox.Question)
        button = dlg.exec()
        if button == QMessageBox.Yes:
            try:
                con = sqlite3.connect("olimp.sqlite")
                cur = con.cursor()
                cur.execute(f'INSERT INTO user (name, class, birth, insession) '
                            f'VALUES (?, ?, ?, ?)',
                            (self.nameEdit.text(), int(self.classEdit.text()), self.birthEdit.text(), 1))
                con.commit()
                con.close()
                self.to_main = MainPG()
                self.to_main.show()
                self.close()
            except sqlite3.Error as error:
                print("Ошибка при работе с SQLite", error)


class MainPG(QMainWindow):  # главный экран
    def __init__(self):  # формирование окна
        super().__init__()
        self.que = []
        uic.loadUi("mainDis.ui", self)
        self.olimps = csv_getter()
        self.for_list()
        self.listWidget.setStyleSheet('QListWidget::item '
                                      '{ border: 1px solid black; }'
                                      ' QListWidget::item:selected { '
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
        self.listWidget2.setStyleSheet('QListWidget::item { border: 1px solid black; }'
                                       ' QListWidget::item:selected { '
                                       'background: lightblue; }')
        self.listWidget2.itemClicked.connect(self.run_added)
        try:
            connection = sqlite3.connect('olimp.sqlite')
            cursor = connection.cursor()
            self.nearOlimp = cursor.execute("""SELECT name, olid, date, time, olimpsus.id FROM olimpsus, status
                    WHERE status.id = olimpsus.status""").fetchall()
            connection.commit()
            connection.close()
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
        self.sort_near_olimp = sorted(self.nearOlimp, key=self.sort_key)
        self.str_of_near_olimp = ""
        for i in self.sort_near_olimp:
            if datetime.datetime.strptime(i[2] + " " + i[3],
                                          '%d.%m.%Y %H:%M') >= datetime.datetime.now():
                self.str_of_near_olimp += self.olimps[i[1]][0]
                self.nearLabel.setText(self.str_of_near_olimp)
                self.str_of_near_olimp = ""
                self.str_of_near_olimp += i[0]
                self.nearLabel_2.setText(self.str_of_near_olimp)
                self.str_of_near_olimp = ""
                self.str_of_near_olimp += i[2]
                self.str_of_near_olimp += " "
                self.str_of_near_olimp += i[3]
                self.nearLabel_3.setText(self.str_of_near_olimp)
                break
        else:
            self.nearLabel.setText("Нет предстоящих событий")

        self.pixmap = QPixmap('orig.png')
        self.logo.setPixmap(self.pixmap)
        self.uch = 0
        for i in self.nearOlimp:
            if i[0] == "Участник":
                self.uch += 1
        self.uch = str(self.uch)
        self.uchLab.setText(self.uch)
        self.win = 0
        for i in self.nearOlimp:
            if i[0] == "Победитель":
                self.win += 1
        self.win = str(self.win)
        self.winLab.setText(self.win)
        self.prize = 0
        for i in self.nearOlimp:
            if i[0] == "Призёр":
                self.prize += 1
        self.prize = str(self.prize)
        self.prizeLab.setText(self.prize)
        self.all_static.clicked.connect(self.to_all_static)

    def sort_key(self, k):  # метод для сортировки дат (компаратор для лямбды)
        if len(k[3]) == 4:
            return k[2] + "0" + k[3]
        else:
            return k[2] + k[3]

    def save(self):  # созранение изменённых данных пользователя
        try:
            connection = sqlite3.connect('olimp.sqlite')
            cursor = connection.cursor()
            cursor.execute('UPDATE user SET name = ?, class = ?, birth = ? WHERE id = ?',
                           (self.name.text(), self.clas.text(), self.birth.text(), self.user[0]))
            connection.commit()
            connection.close()
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)

    def for_list(self):  # формирование айтема для листа (во всём листе)
        for ship_data in self.olimps:
            item = QListWidgetItem()
            item.setSizeHint(QSize(200, 100))
            widget = get_item_wight(ship_data)
            self.listWidget.addItem(item)
            self.listWidget.setItemWidget(item, widget)

    def for_list_added(self):  # формирование айтема листа (добавленные олимпиады)
        try:
            connection = sqlite3.connect('olimp.sqlite')
            cursor = connection.cursor()
            added_olimps = cursor.execute("""SELECT name, olid, date, time, olimpsus.id FROM olimpsus, status
            WHERE status.id = olimpsus.status""").fetchall()
            connection.commit()
            connection.close()
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
        for ship_data in added_olimps:
            item = QListWidgetItem()
            item.setSizeHint(QSize(200, 220))
            widget = self.get_item_added(ship_data, self.olimps)
            self.listWidget2.addItem(item)
            self.listWidget2.setItemWidget(item, widget)

    def run(self, item):   # действие по нажатию на айтем (переход на другой экран)
        x = self.listWidget.indexFromItem(item).row()  # индекс выбранного элемента
        self.to_prewatch = Prewatch(self.olimps[x], x, self)
        if len(self.que) == 0:
            self.que.append(self.to_prewatch)
            self.to_prewatch.show()
        else:
            self.que[0].close()
            self.que = [self.to_prewatch]
            self.to_prewatch.show()

    def run_added(self):  # действие по нажатию на айтем
        pass

    def get_item_added(self, olimp, olimps):  # получение данных айтема (из добавленных олимпиад)
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

    def change(self, olimp):  # переход на другое окно для редактирования олимпиады
        self.to_prewatch = ChangeUD(self.olimps[olimp[1]], olimp[1], self, olimp[4])
        self.to_prewatch.show()

    def delete(self, olimp):  # удаление олимпиады
        try:
            connection = sqlite3.connect('olimp.sqlite')
            cursor = connection.cursor()
            cursor.execute("DELETE FROM olimpsus WHERE id = ?", (olimp[4],))
            connection.commit()
            connection.close()
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
        self.mn_reload = MainPG()
        self.mn_reload.show()
        self.close()

    def to_all_static(self):  # добавление окон статистики
        self.to_static = AllStatic()
        self.to_static.show()
        self.to_gr = Graph()
        self.to_gr.show()


class Prewatch(QMainWindow):  # окно для предпросмотра олимпиады
    def __init__(self, olimp, num, mn):  # формирование окна
        super().__init__()
        uic.loadUi("prewatch.ui", self)
        self.cur_status = "0"
        self.olimp = olimp
        self.num = num
        self.mn = mn
        self.olimpName.setText(olimp[0])
        self.olimpDesc.setText("Описание: " + olimp[1])
        self.olimpLev.setText("Уровень: " + olimp[2])
        self.profil.setText("Профиль: " + olimp[3])
        self.connection = sqlite3.connect('olimp.sqlite')
        self.cur = self.connection.cursor()
        try:
            st = (self.cur
                  .execute("SELECT * FROM status").fetchall())
            self.connection.commit()
            for i in st:
                self.comboBox.addItem(i[1])
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)

        self.addstut.clicked.connect(self.addStut)
        self.comboBox.activated.connect(self.onActivated)
        self.accept.clicked.connect(self.run)

    def run(self):  # добавление олимпиады в расписание
        try:
            self.cur.execute(f'INSERT INTO olimpsus (status, olid, date, time) VALUES (?, ?, ?, ?)',
                             (int(self.cur_status) + 1, int(self.num),
                              self.dateEdit.text(), self.timeEdit.text()))
            self.connection.commit()
            self.mn.close()
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
        self.close()
        self.newMN = MainPG()
        self.newMN.show()

    def onActivated(self, text):  # комбобокс
        self.cur_status = text

    def addStut(self):  # добавление статуса диалогом
        newstatus, ok = QInputDialog.getText(self, "Добавление статуса",
                                             "Введите название статуса", QLineEdit.Normal)
        if ok:
            try:
                connection = sqlite3.connect('olimp.sqlite')
                cur = connection.cursor()
                cur.execute(f'INSERT INTO status (name) VALUES (?)',
                            (newstatus,))
                connection.commit()
                connection.close()
                self.rePre = Prewatch(self.olimp, self.num, self.mn)
                self.rePre.show()
                self.close()
            except sqlite3.Error as error:
                print("Ошибка при работе с SQLite", error)


class ChangeUD(QMainWindow):  # окно изменения добавленных олимпиад
    def __init__(self, olimp, num, mn, is_update):  # формирование окна
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
        try:
            st = (self.cur
                  .execute("SELECT * FROM status").fetchall())
            self.connection.commit()
            for i in st:
                self.comboBox.addItem(i[1])
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
        self.addstut.clicked.connect(self.addStut)
        self.comboBox.activated.connect(self.onActivated)
        self.accept.clicked.connect(self.run)

    def run(self):  # изменение данных олимпиады
        try:
            self.cur.execute('UPDATE olimpsus SET status = ?, olid = ?, date = ?, time = ? WHERE id = ?',
                             (int(self.cur_status) + 1,
                              int(self.num), self.dateEdit.text(), self.timeEdit.text(),
                              self.is_update))
            self.connection.commit()
            self.mn.close()
            self.close()
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
        self.newMN = MainPG()
        self.newMN.show()

    def onActivated(self, text):  # комбобокс
        self.cur_status = text

    def addStut(self):  # добавление статуса
        newstatus, ok = QInputDialog.getText(self, "Добавление статуса",
                                             "Введите название статуса", QLineEdit.Normal)
        if ok:
            try:
                connection = sqlite3.connect('olimp.sqlite')
                cur = connection.cursor()
                cur.execute(f'INSERT INTO status (name) VALUES (?)',
                            (newstatus,))
                connection.commit()
                connection.close()
                self.rePre = Prewatch(self.olimp, self.num, self.mn)
                self.rePre.show()
                self.close()
            except sqlite3.Error as error:
                print("Ошибка при работе с SQLite", error)


class AllStatic(QMainWindow):   # окно с диаграммой
    def __init__(self):  # формирование окна
        super().__init__()
        self.setWindowTitle("Круговая диаграмма")
        self.setGeometry(100, 100, 680, 500)
        self.create_diogram()

    def create_diogram(self):  # создание диаграммы
        dio = QPieSeries()
        try:
            connection = sqlite3.connect('olimp.sqlite')
            cursor = connection.cursor()
            added_olimps = cursor.execute("""SELECT name FROM olimpsus, status
                    WHERE status.id = olimpsus.status""").fetchall()
            connection.commit()
            connection.close()
            dict = {}
            for i in added_olimps:
                if i[0] not in dict:
                    dict[i[0]] = 1
                else:
                    dict[i[0]] += 1
            for i in dict:
                dio.append(i, dict[i])
            for i in range(len(dict)):
                slice = dio.slices()[i]
                slice.setLabelVisible()
            chart = QChart()
            chart.addSeries(dio)
            chart.setAnimationOptions(QChart.SeriesAnimations)
            chart.legend().hide()
            chartview = QChartView(chart)
            chartview.setRenderHint(QPainter.Antialiasing)
            self.setCentralWidget(chartview)
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)


class Graph(QMainWindow):  # окно с графиками участия
    def __init__(self):  # формирование окна
        super().__init__()
        uic.loadUi("gr.ui", self)
        self.acces.clicked.connect(self.run)
        self.cur_status = ""
        try:
            connection = sqlite3.connect('olimp.sqlite')
            cursor = connection.cursor()
            self.all_data = cursor.execute("""SELECT date FROM olimpsus""").fetchall()
            connection.commit()
            connection.close()
            self.for_box = set()
            for i in range(len(self.all_data)):
                date = self.all_data[i][0].split(".")
                self.all_data[i] = [int(date[1]), int(date[2])]
                self.for_box.add(self.all_data[i][1])
            self.for_box = list(self.for_box)
            for i in self.for_box:
                self.comboBoxDT.addItem(str(i))
            self.comboBoxDT.activated.connect(self.onActivated)
            self.graphicsView.setBackground("w")
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)

    def run(self):  # формирование графика
        self.graphicsView.clear()
        time = []
        for j in range(1, 13):
            time.append(j)
        cnt = []
        for j in range(1, 13):
            cnt.append(0)
        for i in self.all_data:
            try:
                if str(i[1]) == str(self.for_box[int(self.cur_status)]):
                    cnt[i[0]] += 1
            except Exception:
                pass
        self.graphicsView.plot(time, cnt)

    def onActivated(self, text):
        self.cur_status = text


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
    try:
        with open('olimps.csv', newline="") as csvfile:
            reader = csv.reader(csvfile, delimiter=';', quotechar='"')
            olimps = list(reader)
        csvfile.close()
    except Exception:
        pass
    try:
        with open('prof.csv', newline="") as csvfile:
            reader = csv.reader(csvfile, delimiter=';', quotechar='"')
            prof = dict(reader)
        csvfile.close()
    except Exception:
        pass
    for el in olimps:
        el[3] = prof[el[3]]
    return olimps


def get_user():
    try:
        connection = sqlite3.connect('olimp.sqlite')
        cur = connection.cursor()
        user = cur.execute("SELECT * FROM user").fetchall()
        connection.commit()
        connection.close()
        if len(user) != 0:
            return user[0]
        return False
    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    if not get_user():
        ex = WelcomePG()
    else:
        ex = MainPG()
    ex.show()
    sys.exit(app.exec_())
