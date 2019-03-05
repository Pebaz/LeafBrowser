import sys, time, codecs
from urllib.parse import quote_plus as qp
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QUrl, QByteArray
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWebEngineWidgets import *
from PyQt5 import QtWebEngineWidgets, QtNetwork
from PyQt5.Qt import pyqtSlot, pyqtSignal, QIcon, Qt, QWebEngineHttpRequest

class AuthPopup(QDialog):
    def __init__(self):
        QWidget.__init__(self)
        self.setWindowTitle('Authenticate')
        self.username = QLineEdit()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)

        layout = QGridLayout()
        layout.addWidget(QLabel('Username'), 0, 0)
        layout.addWidget(QLabel('Password'), 1, 0)
        layout.addWidget(self.username, 0, 1)
        layout.addWidget(self.password, 1, 1)
        button = QPushButton('Ok')
        button.clicked.connect(self.close)
        layout.addWidget(button, 2, 0, 1, 2)
        self.setLayout(layout)

    @staticmethod
    def get_creds():
        auth = AuthPopup()
        auth.exec_()
        return auth.username.text(), auth.password.text()


class BrowserTab(QWidget):
    def __init__(self, page='http://www.google.com', socks5=True):
        QWidget.__init__(self)

        # Widgets
        self.browser = QWebEngineView()
        self.addr_bar = QLineEdit(page)
        self.search = QLineEdit()
        self.find = QLineEdit()
        self.progress = QProgressBar()
        sbox = QHBoxLayout()
        sbox.addWidget(QLabel('Google Search'))
        sbox.addWidget(self.search)
        self.proxy = QPushButton('Proxy')
        sbox.addWidget(self.proxy)
        hbox = QHBoxLayout()
        self.lbl_find = QLabel('Find')
        self.hide_find()
        hbox.addWidget(self.lbl_find)
        hbox.addWidget(self.find)
        addrbox = QHBoxLayout()
        back = QPushButton('<-')
        back.setMaximumSize(32, 24)
        back.clicked.connect(self.browser.back)
        forward = QPushButton('->')
        forward.setMaximumSize(31, 24)
        forward.clicked.connect(self.browser.forward)
        addrbox.addWidget(back)
        addrbox.addWidget(forward)
        addrbox.addWidget(self.addr_bar)

        pbox = QHBoxLayout()
        self.ptxb1 = QLineEdit()
        self.ptxb1.setPlaceholderText('Host')
        self.ptxb2 = QLineEdit()
        self.ptxb2.setPlaceholderText('Port')
        self.ptype = QComboBox()
        self.ptype.addItem('Disable Proxy')
        self.ptype.addItem('Http')
        self.ptype.addItem('Socks5')
        pbox.addWidget(self.ptxb1)
        pbox.addWidget(self.ptxb2)
        pbox.addWidget(self.ptype)
        self.proxy_done()


        vbox = QVBoxLayout()
        vbox.addLayout(addrbox)
        vbox.addLayout(sbox)
        vbox.addLayout(hbox)
        vbox.addLayout(pbox)
        vbox.addWidget(self.progress)
        vbox.addWidget(self.browser)

        # Find
        find_short = QShortcut(QKeySequence('Ctrl+F'), self)
        find_short.activated.connect(self.show_find)
        find_hide = QShortcut(QKeySequence('Escape'), self)
        find_hide.activated.connect(self.hide_find)

        # Signals and Slots
        self.addr_bar.returnPressed.connect(
            lambda: self.browser.load(QUrl(self.addr_bar.text())))
        self.search.returnPressed.connect(
            lambda: self.browser.load(QUrl(
                f'https://www.google.com/search?q={qp(self.search.text())}')))
        self.find.returnPressed.connect(lambda: self.browser.page().findText(self.find.text()))
        self.browser.urlChanged.connect(self.handle_url_change)
        self.browser.loadProgress[int].connect(self.progress.setValue)
        self.browser.loadFinished.connect(self.progress.hide)
        self.browser.loadStarted.connect(self.progress.show)

        self.setLayout(vbox)

        # Ask user for credentials if page needs them
        self.browser.page().authenticationRequired.connect(self.authenticate)
        self.browser.load(QUrl(page))

    def show_find(self):
        self.lbl_find.show()
        self.find.show()
        self.find.setFocus()

    def hide_find(self):
        self.lbl_find.hide()
        self.find.hide()
        self.browser.page().findText('')

    def authenticate(self, url, auth):
        user, pwd = AuthPopup.get_creds()

        auth.setUser('admin')
        auth.setPassword('Colonist22')

    def proxy_show(self):
        self.ptxb1.show()
        self.ptxb2.show()
        self.ptype.show()
        self.proxy.setText('Done')
        self.proxy.clicked.connect(self.proxy_done)

    def proxy_done(self):
        self.ptxb1.hide()
        self.ptxb2.hide()
        self.ptype.hide()
        self.proxy.setText('Proxy')
        self.proxy.clicked.connect(self.proxy_show)
        self.set_proxy(self.ptxb1.text(), self.ptxb2.text(), self.ptype.currentText())

    def handle_url_change(self, url):
        self.addr_bar.setText(url.toDisplayString())

    def set_proxy(self, host, port, type):
        if type =='Socks5':
            proxy_type = QtNetwork.QNetworkProxy.Socks5Proxy
        elif type == 'Http':
            proxy_type = QtNetwork.QNetworkProxy.HttpProxy
        else:
            return
        proxy = QtNetwork.QNetworkProxy()
        proxy.setType(proxy_type)
        proxy.setHostName(host)
        proxy.setPort(int(port))
        QtNetwork.QNetworkProxy.setApplicationProxy(proxy)

#http://52.170.233.2:5984
class Browser(QTabWidget):
    def __init__(self):
        QTabWidget.__init__(self)
        self.setWindowTitle('Leaf Browser')
        self.setWindowIcon(QIcon('leaf-icon.ico'))
        self.setStyleSheet('QTabWidget::pane{border: 0 solid white;margin: -4px -4px -4px -4px;}')
        self.resize(1024, 768)
        self.setTabsClosable(True)
        self.setMovable(True)
        self.setUsesScrollButtons(True)
        #self.setTabShape(self.Triangular)
        #self.set_proxy()
        self.currentChanged.connect(self.tab_changed)
        self.tabCloseRequested.connect(self.close_tab)
        self.insertTab(-1, QWidget(), '+')

        new_tab = QShortcut(QKeySequence('Ctrl+T'), self)
        new_tab.activated.connect(self.add_tab)

    def close_tab(self, index):
        if index != self.count() - 1:
            if self.count() == 2:
                self.close()
            self.setCurrentIndex(self.count() - 3)
            self.removeTab(index)

    def add_tab(self):
        self.insertTab(self.count() - 1, BrowserTab(), 'Tab')
        self.setCurrentIndex(self.count() - 2)

    def tab_changed(self, index):
        # Switched to any tab save for the last one
        if index != self.count() - 1:
            tab = self.widget(index)
            self.setTabText(index, tab.browser.url().host())

        # Switched to the last tab (the plus button)
        else:
            self.add_tab()

    def set_proxy(self, socks5=True):
        proxy = QtNetwork.QNetworkProxy()
        if socks5:
            proxy_type = QtNetwork.QNetworkProxy.Socks5Proxy
        else:
            proxy_type = QtNetwork.QNetworkProxy.HttpProxy
        proxy.setType(proxy_type)
        proxy.setHostName('proxy.hud.gov')
        proxy.setPort(5050 if socks5 else 8080)
        QtNetwork.QNetworkProxy.setApplicationProxy(proxy)


def main(args):
    app = QApplication(sys.argv)

    browser = Browser()
    browser.show()

    try:
        return_code = app.exec_()
    except:
        pass
    finally:
        # Makes sure that the QtWebEngineProcess.exe process is killed
        del browser, app
    return return_code

if __name__ == '__main__':
    sys.exit(main(sys.argv))
