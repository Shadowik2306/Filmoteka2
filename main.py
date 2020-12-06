import sys
import sqlite3
from PyQt5.QtWidgets import QMainWindow, QApplication
from main_window import Ui_MainWindow
from PyQt5.Qt import QTableWidgetItem
from new_file import Ui_WindNewFilm
from new_genre import Ui_NewGenre
from dely import Ui_Dely


class YearNotExist(Exception):
    pass


class NeedMoreInf(Exception):
    pass


class StrangeLength(Exception):
    pass


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.load_table()
        self.add_film.clicked.connect(self.add_newItem)
        self.add_genre.clicked.connect(self.add_newGenre)
        self.del_film.clicked.connect(self.del_file)
        self.del_genre.clicked.connect(self.del_file)

    def load_table(self):
        con = sqlite3.connect('films_db.sqlite')
        self.cur = con.cursor()
        self.list_genres = [i[0] for i in self.cur.execute('SELECT title FROM genres').fetchall()]
        self.tableWidget.setColumnCount(5)
        self.tableWidget.setHorizontalHeaderLabels(['id', 'title', 'year', 'genre', 'duration'])
        self.tableWidget.horizontalHeader().setSectionResizeMode(1)
        self.tableWidget.setRowCount(0)
        for i, row in enumerate(self.cur.execute('SELECT * FROM films')):
            self.tableWidget.setRowCount(self.tableWidget.rowCount() + 1)
            for j, col in enumerate(row):
                if j == 3:
                    try:
                        self.tableWidget.setItem(i, j, QTableWidgetItem(self.list_genres[col - 1]))
                    except IndexError:
                        self.tableWidget.setItem(i, j, QTableWidgetItem('Error'))
                else:
                    self.tableWidget.setItem(i, j, QTableWidgetItem(str(col)))

        self.tableWidget_2.setColumnCount(2)
        self.tableWidget_2.setHorizontalHeaderLabels(['id', 'title'])
        self.tableWidget_2.horizontalHeader().setSectionResizeMode(1)
        self.tableWidget_2.setRowCount(0)
        for i, row in enumerate(self.cur.execute('SELECT * FROM genres')):
            self.tableWidget_2.setRowCount(self.tableWidget_2.rowCount() + 1)
            for j, col in enumerate(row):
                    self.tableWidget_2.setItem(i, j, QTableWidgetItem(str(col)))

    def add_newItem(self):
        self.wind = WindNewFilm(self.cur.execute('SELECT id FROM films').fetchall()[-1][0],
                                self.list_genres, self.load_table)
        self.wind.show()

    def add_newGenre(self):
        self.wind = WindNewGenre(self.load_table)
        self.wind.show()

    def del_file(self):
        if self.sender().objectName() == 'del_genre':
            key = 'g'
        else:
            key = 'f'
        self.wind = WindDely(key, self.load_table)
        self.wind.show()


class WindNewFilm(QMainWindow, Ui_WindNewFilm):
    def __init__(self, id, genres, table):
        super().__init__()
        self.setupUi(self)
        self.cancel.clicked.connect(self.nope)
        self.cont_2.clicked.connect(self.yes)
        self.id = id
        for i in genres:
            self.genre.addItem(i)
        self.list_genres = genres
        self.table = table
        self.label_5.setVisible(False)


    def nope(self):
        self.close()

    def yes(self):
        try:
            if not (self.name.text() and self.birthyear.text() and self.length.text()):
                raise NeedMoreInf
            if int(self.birthyear.text()) > 2020:
                raise YearNotExist
            if int(self.length.text()) < 0:
                raise StrangeLength
            con = sqlite3.connect('films_db.sqlite')
            cur = con.cursor()
            cur.execute('INSERT INTO films(id, title, year, genre, duration) VALUES(?, ?, ?, ?, ?)',
                        (self.id + 1, self.name.text(),
                         int(self.birthyear.text()),
                         self.list_genres.index(self.genre.currentText()) + 1, int(self.length.text())))
            con.commit()
            self.table()
            self.close()
        except NeedMoreInf:
            self.label_5.setVisible(True)
            self.label_5.setText('Заполните всю нужную информацию')
        except YearNotExist:
            self.label_5.setVisible(True)
            self.label_5.setText('Не корректный год')
        except StrangeLength:
            self.label_5.setVisible(True)
            self.label_5.setText('Ошибка продолжительности')


class WindNewGenre(QMainWindow, Ui_NewGenre):
    def __init__(self, table):
        super(WindNewGenre, self).__init__()
        self.setupUi(self)
        self.table = table
        self.cancel.clicked.connect(self.nope)
        self.accept.clicked.connect(self.yes)

    def nope(self):
        self.close()

    def yes(self):
        try:
            if not (self.lineEdit.text()):
                raise NeedMoreInf
            con = sqlite3.connect('films_db.sqlite')
            cur = con.cursor()
            cur.execute('INSERT INTO genres(id, title) VALUES(?, ?)',
                        (cur.execute('SELECT id FROM genres').fetchall()[-1][0] + 1,
                         self.lineEdit.text()))
            con.commit()
            self.table()
            self.close()
        except NeedMoreInf:
            self.label_5.setVisible(True)
            self.label_5.setText('Заполните всю нужную информацию')


class WindDely(QMainWindow, Ui_Dely):
    def __init__(self, key, table):
        super(WindDely, self).__init__()
        self.setupUi(self)
        self.pushButton_2.clicked.connect(self.nope)
        self.pushButton.clicked.connect(self.yes)
        if key == 'f':
            self.key = 'films'
        else:
            self.key = 'genres'
        self.table = table

    def nope(self):
        self.close()

    def yes(self):
        try:
            con = sqlite3.connect('films_db.sqlite')
            cur = con.cursor()
            cur.execute(f'DELETE FROM {self.key} WHERE id = ?', (self.spinBox.value(),))
            con.commit()
            self.table()
            self.close()
        except Exception as e:
            print(e)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    wind = MainWindow()
    wind.show()
    sys.exit(app.exec())