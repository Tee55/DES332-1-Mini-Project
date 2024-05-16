import sys
from PySide6 import QtCore
from PySide6.QtWidgets import QMessageBox, QLabel, QWidget, QLineEdit, QListWidgetItem, QTextEdit, QHBoxLayout, QVBoxLayout, QPushButton, QListWidget, QApplication, QGridLayout
import rsa
import datetime
import sqlite3

con = sqlite3.connect("chat.db")
cur = con.cursor()

class AppWidget(QWidget):
    def __init__(self, username):
        super().__init__()

        self.userListWidgets = UserListWidgets(username)
        self.chatLogWidgets = ChatLogWidgets(
            username, self.userListWidgets.recipient)

        self.layout = QHBoxLayout(self)
        self.layout.addWidget(self.userListWidgets)
        self.layout.addWidget(self.chatLogWidgets)

class ChatWidgets(QWidget):
    def __init__(self, username, recipient):
        super().__init__()

        self.edit = QLineEdit()
        self.button = QPushButton("Send")

        self.layout = QHBoxLayout(self)
        self.layout.addWidget(self.edit)
        self.layout.addWidget(self.button)

        self.button.clicked.connect(self.send)
        self.username = username
        self.recipient = recipient

    @QtCore.Slot()
    def send(self):
        MESSAGE = self.edit.text().encode('utf8')

        print(self.username + "=>" + self.recipient + ": " + self.edit.text())
        if self.recipient == 'Tee':
            with open('tee_publickey.pem', mode='rb') as f:
                key = rsa.PublicKey.load_pkcs1(f.read())
                f.close()
        elif self.recipient == 'John':
            with open('john_publickey.pem', mode='rb') as f:
                key = rsa.PublicKey.load_pkcs1(f.read())
                f.close()

        ciphertext = rsa.encrypt(MESSAGE, key)

        cur.execute('INSERT INTO messages VALUES(?, ?, ?, ?)', (self.username,
                    self.recipient, datetime.datetime.now().isoformat(), ciphertext))
        con.commit()

class ChatLogWidgets(QWidget):
    def __init__(self, username, recipient):
        super().__init__()

        self.chatWidget = ChatWidgets(username, recipient)
        self.textEdit = QTextEdit()
        self.textEdit.isReadOnly = True

        res = cur.execute(
            f"""SELECT sender, recipient, message FROM messages WHERE recipient = '{username}' or recipient = '{recipient}' and sender = '{username}' or sender = '{recipient}'""")

        for row in res.fetchall():

            if username == row[1]:
                with open(row[1] + '_privatekey.pem', mode='rb') as f:
                    key = rsa.PrivateKey.load_pkcs1(f.read())
                    f.close()
                message = rsa.decrypt(row[2], key)
                self.textEdit.append(message.decode() + ": " + row[0])
                self.textEdit.setAlignment(QtCore.Qt.AlignRight)
            else:
                self.textEdit.append(row[0] + ": Encrypted")
                self.textEdit.setAlignment(QtCore.Qt.AlignLeft)

        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.textEdit)
        self.layout.addWidget(self.chatWidget)

class UserListWidgets(QWidget):
    def __init__(self, username):
        super().__init__()

        self.setLayout(QVBoxLayout())
        self.listWidget = QListWidget()

        res = cur.execute(
            f"""SELECT username FROM users where username != '{username}'""")
        for row in res.fetchall():
            self.listWidget.addItem(QListWidgetItem(row[0]))

        self.layout().addWidget(self.listWidget)

        self.listWidget.itemClicked.connect(self.clicked)
        self.recipient = row[0]

    @QtCore.Slot()
    def clicked(self, item):
        self.recipient = item.text()


def createTable():
    cur.execute(
        f"""CREATE TABLE IF NOT EXISTS users (username TEXT, password TEXT)""")
    cur.execute(
        f"""CREATE TABLE IF NOT EXISTS messages (sender TEXT, recipient TEXT, timestamp TEXT, message BLOB)""")

    res = cur.execute("""SELECT username FROM users""")
    if res.fetchone() is not None:
        return

    cur.execute("""INSERT INTO users VALUES('Tee', '1234')""")
    cur.execute("""INSERT INTO users VALUES('John', '2345')""")
    con.commit()


class LoginForm(QWidget):
    def __init__(self):
        super().__init__()

        layout = QGridLayout()

        label_name = QLabel('Username')
        self.lineEdit_username = QLineEdit()
        self.lineEdit_username.setPlaceholderText('Please enter your username')
        layout.addWidget(label_name, 0, 0)
        layout.addWidget(self.lineEdit_username, 0, 1)

        label_password = QLabel('Password')
        self.lineEdit_password = QLineEdit()
        self.lineEdit_password.setPlaceholderText('Please enter your password')
        layout.addWidget(label_password, 1, 0)
        layout.addWidget(self.lineEdit_password, 1, 1)

        button_login = QPushButton('Login')
        button_login.clicked.connect(self.check_password)
        layout.addWidget(button_login, 2, 0, 1, 2)
        layout.setRowMinimumHeight(2, 75)

        self.setLayout(layout)

    def check_password(self):
        msg = QMessageBox()
        username = self.lineEdit_username.text()
        password = self.lineEdit_password.text()

        res = cur.execute(
            f"""SELECT password FROM users WHERE username = '{username}'""")

        row = res.fetchone()

        if password == row[0]:
            msg.setText('Success')
            msg.exec()
            self.widget = AppWidget(username)
            self.widget.show()
            self.close()
        else:
            msg.setText('Incorrect Password')
            msg.exec()


if __name__ == "__main__":
    createTable()
    app = QApplication([])
    form = LoginForm()
    form.show()
    sys.exit(app.exec())
