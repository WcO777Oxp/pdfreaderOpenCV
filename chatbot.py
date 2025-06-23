# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(1416, 962)

        # 🌒 Dark theme default
        Form.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                color: #eaeaea;
                font-family: 'Segoe UI', sans-serif;
                font-size: 14px;
            }
            QLineEdit, QTextEdit {
                background-color: #2d2d2d;
                border: 1px solid #555;
                border-radius: 6px;
                padding: 6px;
                color: #ffffff;
            }
            QPushButton {
                background-color: #3a3a3a;
                color: #ffffff;
                padding: 6px 12px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #505050;
            }
            QScrollArea {
                background-color: #1e1e1e;
                border: none;
            }
            QListWidget {
                background-color: #181818;
                color: #ffffff;
                border: none;
                padding: 10px;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #333;
            }
            QListWidget::item:selected {
                background-color: #8e44ad;
                color: white;
            }
            QLabel {
                color: #ffffff;
            }
        """)

        # 🧱 Root Layout
        self.mainLayout = QtWidgets.QHBoxLayout(Form)

        # 📚 Left Sidebar
        self.leftPanel = QtWidgets.QVBoxLayout()
        self.leftPanel.setSpacing(10)

        self.pdfList = QtWidgets.QListWidget(Form)
        self.pdfList.setFixedWidth(260)
        self.pdfList.setObjectName("pdfList")
        self.leftPanel.addWidget(self.pdfList)

        self.chatHistory = QtWidgets.QListWidget()
        self.chatHistory.setFixedWidth(260)
        self.chatHistory.setObjectName("chatHistory")
        self.leftPanel.addWidget(self.chatHistory)

        self.mainLayout.addLayout(self.leftPanel)

        # 📦 Right Panel
        self.rightWidget = QtWidgets.QWidget()
        self.rightLayout = QtWidgets.QVBoxLayout(self.rightWidget)
        self.rightLayout.setContentsMargins(0, 0, 0, 0)
        self.rightLayout.setSpacing(10)

        self.label = QtWidgets.QLabel("🧾 POS Help Chatbot")
        font = QtGui.QFont()
        font.setPointSize(20)
        font.setBold(True)
        self.label.setFont(font)
        self.rightLayout.addWidget(self.label)

        self.scrollArea = QtWidgets.QScrollArea()
        self.scrollArea.setWidgetResizable(True)

        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 800, 700))
        self.verticalLayout = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.rightLayout.addWidget(self.scrollArea)

        # 💬 Input Row
        self.bottomWidget = QtWidgets.QWidget()
        self.bottomLayout = QtWidgets.QVBoxLayout(self.bottomWidget)

        self.inputRow = QtWidgets.QHBoxLayout()

        self.lineEdit = QtWidgets.QLineEdit()
        self.lineEdit.setPlaceholderText("Ask a question…")
        self.lineEdit.setStyleSheet("font-size: 15px;")
        self.inputRow.addWidget(self.lineEdit)

        self.send = QtWidgets.QPushButton("➤ Send")
        self.send.setFixedHeight(40)
        self.send.setStyleSheet("font-weight: bold; background-color: #8e44ad;")
        self.inputRow.addWidget(self.send)

        self.bottomLayout.addLayout(self.inputRow)
        self.rightLayout.addWidget(self.bottomWidget)

        self.mainLayout.addWidget(self.rightWidget)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "POS Chatbot"))
