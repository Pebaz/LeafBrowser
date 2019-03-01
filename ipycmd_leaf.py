import sys
from urllib.parse import quote_plus as qp
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import *
from PyQt5 import QtWebEngineWidgets, QtNetwork
from PyQt5.Qt import pyqtSlot, pyqtSignal, QIcon

class BrowserTab(QWidget):
    def __init__(self, page='http://www.google.com', socks5=True):
        QWidget.__init__(self)

        # Widgets
        self.browser = QWebEngineView()
        self.addr_bar = QLineEdit(page)
        self.search = QLineEdit()
        self.progress = QProgressBar()
        hbox = QHBoxLayout()
        hbox.addWidget(QLabel('Google Search'))
        hbox.addWidget(self.search)
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
        vbox = QVBoxLayout()
        vbox.addLayout(addrbox)
        vbox.addLayout(hbox)
        vbox.addWidget(self.progress)
        vbox.addWidget(self.browser)
        
        # Signals and Slots
        self.addr_bar.returnPressed.connect(
            lambda: self.browser.load(QUrl(self.addr_bar.text())))
        self.search.returnPressed.connect(
            lambda: self.browser.load(QUrl(
                f'https://www.google.com/search?q={qp(self.search.text())}')))
        self.browser.urlChanged.connect(self.handle_url_change)
        self.browser.loadProgress[int].connect(self.progress.setValue)
        self.browser.loadFinished.connect(self.progress.hide)
        self.browser.loadStarted.connect(self.progress.show)

        self.setLayout(vbox)
        self.browser.load(QUrl(page))

    def handle_url_change(self, url):
        self.addr_bar.setText(url.toDisplayString())


class Browser(QTabWidget):
    def __init__(self):
        QTabWidget.__init__(self)
        self.setWindowTitle('Leaf Browser')
        self.setWindowIcon(QIcon('leaf-icon.ico'))
        self.resize(1024, 768)
        self.setTabsClosable(True)
        self.setMovable(True)
        self.setUsesScrollButtons(True)
        self.set_proxy()
        self.currentChanged.connect(self.tab_changed)
        self.tabCloseRequested.connect(self.close_tab)
        self.insertTab(-1, QWidget(), '+')

    def close_tab(self, index):
        if index != self.count() - 1:
            if self.count() == 2:
                self.close()
            self.setCurrentIndex(self.count() - 3)
            self.removeTab(index)

    def tab_changed(self, index):
        # Switched to any tab save for the last one
        if index != self.count() - 1:
            tab = self.widget(index)
            self.setTabText(index, tab.browser.url().host())

        # Switched to the last tab (the plus button)
        else:
            self.insertTab(self.count() - 1, BrowserTab(), 'Tab')
            self.setCurrentIndex(self.count() - 2)

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
















"""
https://stackoverflow.com/questions/11513132/embedding-ipython-qt-console-in-a-pyqt-application
https://ipython.org/ipython-doc/3/interactive/qtconsole.html#embedding-the-qtconsole-in-a-qt-application
https://github.com/jupyter/qtconsole/blob/master/examples/embed_qtconsole.py

USE THIS TO MAKE THE CONSOLE SLIGHTLY TRANSPARENT TO SEE THE GAME UNDERNEATH:
https://stackoverflow.com/questions/4499488/is-it-possible-to-set-the-opacity-of-qt-widgets



MAKE SURE TO STYLE THE WIDGET SO THAT THE BACKGROUND COLOR IS BLACK
AND THE TEXT IS MOSTLY WHITE! :D
"""

from pprint import pprint
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QApplication, QWidget, QBoxLayout, QTextEdit, QPushButton
from PyQt5 import QtGui
from PyQt5.Qt import QFont
#from qtconsole.qt import QtGui
from qtconsole.rich_jupyter_widget import RichJupyterWidget
from qtconsole.inprocess import QtInProcessKernelManager


names = {
	'get_name' : lambda: 'Pebaz',
	'history_file' : lambda: get_ipython().history_manager.hist_file
}

app = QApplication([])
widget = QWidget()
layout = QBoxLayout(QBoxLayout.LeftToRight)
widget.setLayout(layout)



# Put widget under the console
label = QLabel("This should appear below the console but doesn't!")
label.move(64, 64)
layout.addWidget(label)


# Create an in-process kernel
kernel_manager = QtInProcessKernelManager()
kernel_manager.start_kernel(show_banner=False)
kernel = kernel_manager.kernel

# Populate the kernel with names
kernel.shell.user_ns.update(kman=kernel_manager, **names)

kernel.gui = 'qt'
kernel_client = kernel_manager.client()
kernel_client.start_channels()
ipython_widget = RichJupyterWidget()
ipython_widget.kernel_manager = kernel_manager
ipython_widget.kernel_client = kernel_client

	# # They can't currently work well together for some reason
	# USE_OPACITY = False

	# if USE_OPACITY:
	# 	# Transparency:
	# 	op = QGraphicsOpacityEffect(ipython_widget)
	# 	op.setOpacity(0.8) #0 to 1 will cause the fade effect to kick in
	# 	ipython_widget.setGraphicsEffect(op)
	
	# else:
	# 	# SET THE COLOR THEME:
	# 	# https://bitbucket.org/joon/color-schemes-for-jupyter-qt-console
	# 	color_theme = 'blackboard'
	# 	ipython_widget.style_sheet = open(f'C:/Users/samuel.wilder/Coding/Projects/Spire/res/stylesheets/{color_theme}.css').read()
	# 	ipython_widget.syntax_style = color_theme


	



	# layout.addWidget(ipython_widget)
	# #layout.addWidget(QTextEdit())

	# from PyQt5.Qsci import *
	# qs = QsciScintilla()
	# qs.setText(";; Enter your script here.")
	# qs.setFont(QFont("Consolas", 12))
	# layout.addWidget(qs)

	# widget.show()

	# app.exec_()

	# kernel_client.stop_channels()
	# kernel_manager.shutdown_kernel()



























def main(args):
    app = QApplication(sys.argv)
    browser = Browser()
    w = QWidget()
    layout = QHBoxLayout()
    layout.addWidget(ipython_widget)
    layout.addWidget(browser)
    w.setLayout(layout)

    #browser.show()
    w.show()


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
