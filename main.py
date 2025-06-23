import sys
import os
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QMessageBox, QHBoxLayout,
    QVBoxLayout, QListWidgetItem, QGraphicsDropShadowEffect
)
from PyQt5.QtGui import QPixmap, QColor
from PyQt5.QtCore import Qt, QTimer
from chatbot import Ui_Form
from manual_generator import run_manual_import, PDF_RES
import difflib

HELP_ENTRIES = []

class ChatBotWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.setWindowTitle("POS Help Chatbot")

        self.current_results = []
        self.chat_history = set()
        self.selected_pdf_folder = None

        self.typing_timer = QTimer()
        self.typing_step = 0
        self.typing_label = None

        self.ui.send.clicked.connect(self.handle_query)
        self.ui.chatHistory.itemClicked.connect(self.load_from_history)

        if hasattr(self.ui, 'pdfList'):
            self.ui.pdfList.itemClicked.connect(self.select_pdf)

        run_manual_import()
        self.load_pdf_files()

    def load_pdf_files(self):
        self.ui.pdfList.clear()
        for file in os.listdir(PDF_RES):
            if file.lower().endswith(".pdf"):
                self.ui.pdfList.addItem(file)

    def select_pdf(self, item):
        self.selected_pdf_folder = os.path.splitext(item.text())[0]
        self.add_message(f"📄 Selected PDF: {item.text()}", is_user=False)
        self.load_help_entries()

    def load_help_entries(self):
        global HELP_ENTRIES
        HELP_ENTRIES = []
        self.ui.chatHistory.clear()
        self.chat_history.clear()

        if not self.selected_pdf_folder:
            return

        folder = os.path.join("res", "images", self.selected_pdf_folder)
        if not os.path.exists(folder):
            return

        for filename in os.listdir(folder):
            if filename.endswith(".png"):
                title = filename[:-4].replace("_", " ").upper()
                text_path = os.path.join(folder, filename.replace(".png", ".txt"))
                content = ""
                if os.path.exists(text_path):
                    with open(text_path, "r", encoding="utf-8") as f:
                        content = f.read().strip()
                HELP_ENTRIES.append((title, content, os.path.join("images", self.selected_pdf_folder, filename)))

                norm_title = title.lower()
                if norm_title not in self.chat_history:
                    self.chat_history.add(norm_title)
                    item = QListWidgetItem(title.title())
                    item.setTextAlignment(Qt.AlignLeft)
                    self.ui.chatHistory.addItem(item)

    def handle_query(self):
        query = self.ui.lineEdit.text().strip()
        if not query:
            QMessageBox.warning(self, "Warning", "Please enter a help topic.")
            return

        self.add_to_history(query)
        self.add_message(query, is_user=True)

        self.typing_label = QLabel("🤖 Typing")
        self.typing_label.setStyleSheet("color: #aaa; font-style: italic; padding: 10px;")
        self.ui.verticalLayout.addWidget(self.typing_label)
        self.scroll_to_bottom()

        self.typing_step = 0
        if not self.typing_timer.isActive():
            self.typing_timer.timeout.connect(self.animate_typing)
        self.typing_timer.start(500)

        QTimer.singleShot(1500, lambda: self.respond(query))
        self.ui.lineEdit.clear()

    def animate_typing(self):
        self.typing_step = (self.typing_step + 1) % 4
        if self.typing_label:
            self.typing_label.setText("🤖 Typing" + "." * self.typing_step)

    def add_to_history(self, query):
        normalized = query.strip().lower()
        if normalized and normalized not in self.chat_history:
            self.chat_history.add(normalized)
            item = QListWidgetItem(query)
            item.setTextAlignment(Qt.AlignLeft)
            self.ui.chatHistory.addItem(item)

    def load_from_history(self, item):
        query = item.text()
        self.ui.lineEdit.setText(query)
        self.handle_query()

    def respond(self, query):
        self.typing_timer.stop()
        if self.typing_label:
            self.ui.verticalLayout.removeWidget(self.typing_label)
            self.typing_label.deleteLater()
            self.typing_label = None

        query_clean = query.lower().replace("how to", "").replace("how", "").strip()

        def normalize(text):
            return text.lower().replace("_", " ").replace("-", " ").strip()

        scored_matches = []
        for title, desc, image in HELP_ENTRIES:
            norm_title = normalize(title)
            score = difflib.SequenceMatcher(None, query_clean, norm_title).ratio()
            if query_clean in norm_title or score > 0.5:
                scored_matches.append((score, title, desc, image))

        scored_matches.sort(reverse=True)

        if scored_matches:
            _, title, desc, image_path = scored_matches[0]
            if desc:
                self.add_message(self.format_html(desc), is_user=False)
            if image_path:
                self.display_image(image_path)
        else:
            self.add_message(f"❌ No match found for '{query}'.", is_user=False)

        self.scroll_to_bottom()

    def add_message(self, text, is_user=False):
        bubble = QLabel(text)
        bubble.setWordWrap(True)
        bubble.setTextFormat(Qt.RichText)
        bubble.setTextInteractionFlags(Qt.TextSelectableByMouse)
        bubble.setStyleSheet(f"""
            background-color: {'#8e44ad' if is_user else '#2c2c2c'};
            color: white; border-radius: 20px; padding: 16px 20px;
            font-size: 15px; max-width: 520px;
        """)

        timestamp = QLabel(datetime.now().strftime("%I:%M %p"))
        timestamp.setStyleSheet("color: gray; font-size: 11px;")
        timestamp.setAlignment(Qt.AlignRight if is_user else Qt.AlignLeft)

        avatar = QLabel()
        icon_path = "./res/user_icon.png" if is_user else "./res/bot_icon.png"
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path).scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            avatar.setPixmap(pixmap)
            avatar.setFixedSize(40, 40)
        else:
            avatar.setText("👤" if is_user else "🤖")
            avatar.setStyleSheet("font-size: 24px;")

        vbox = QVBoxLayout()
        vbox.setSpacing(2)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.addWidget(bubble)
        vbox.addWidget(timestamp)

        row = QWidget()
        hbox = QHBoxLayout(row)
        hbox.setContentsMargins(10, 10, 10, 10)
        hbox.setSpacing(10)

        if is_user:
            hbox.addStretch()
            hbox.addLayout(vbox)
            hbox.addWidget(avatar)
        else:
            hbox.addWidget(avatar)
            hbox.addLayout(vbox)
            hbox.addStretch()

        self.ui.verticalLayout.addWidget(row)

    def format_html(self, text):
        html = ""
        for line in text.strip().splitlines():
            line = line.strip()
            if line.startswith(("•", "-")):
                html += f"• {line[1:].strip()}<br>"
            elif line:
                html += f"{line}<br><br>"
        return html

    def display_image(self, image_path):
        full_path = os.path.join("res", image_path)
        if os.path.exists(full_path):
            img = QLabel()
            pixmap = QPixmap(full_path).scaledToWidth(600, Qt.SmoothTransformation)
            img.setPixmap(pixmap)
            img.setStyleSheet("border-radius: 6px; margin: 10px;")

            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(12)
            shadow.setColor(QColor(0, 0, 0, 120))
            shadow.setOffset(3, 3)
            img.setGraphicsEffect(shadow)

            wrapper = QWidget()
            layout = QHBoxLayout(wrapper)
            layout.setContentsMargins(10, 0, 10, 10)
            layout.addWidget(img)

            self.ui.verticalLayout.addWidget(wrapper)

    def scroll_to_bottom(self):
        self.ui.scrollArea.verticalScrollBar().setValue(
            self.ui.scrollArea.verticalScrollBar().maximum()
        )

if __name__ == "__main__":
    app = QApplication(sys.argv)
    chatbot = ChatBotWindow()
    chatbot.show()
    sys.exit(app.exec_())
