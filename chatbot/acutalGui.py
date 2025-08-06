import sys
import os
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit, QLineEdit,
    QHBoxLayout, QSizePolicy, QSpacerItem, QFileDialog, QLabel
)
from PySide6.QtCore import Qt
from docx import Document
import PyPDF2
from main import ChatSession  # your existing chatbot backend
from PySide6.QtCore import QRunnable, QThreadPool, Slot, Signal, QObject #threading so that ui doesnt freeze 
from PySide6.QtCore import QTimer




class ChatbotGui(QWidget):


   

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Jenglish - Jarvis that teaches English")
        self.showNormal()
        self.apply_dark_theme()
        self.threadpool = QThreadPool()



        

        self.loading_animation_index = 0
        self.loading_timer = QTimer()
        self.loading_timer.timeout.connect(self.update_loading_animation)


        self.uploaded_files = {}  # Store filename -> extracted text

        # Layout manager
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(30, 30, 30, 30)
        self.layout.setSpacing(20)
        self.setLayout(self.layout)

        #cool loading animation
        self.loading_label = QLabel("💬 Thinking...")
        self.loading_label.setAlignment(Qt.AlignLeft)
        self.loading_label.setStyleSheet("color: #AAAAAA; font-style: italic;")
        self.loading_label.hide()  # Hidden by default
        self.layout.addWidget(self.loading_label)

        # Header layout
        self.header_layout = QHBoxLayout()
        self.layout.addLayout(self.header_layout)

        # Spacer
        self.header_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        # Upload File Button
        self.upload_button = QPushButton("Upload File")
        self.upload_button.setFixedSize(120, 40)
        self.upload_button.clicked.connect(self.upload_file)
        self.header_layout.addWidget(self.upload_button)

        # Exit Button
        self.exit_button = QPushButton("Exit")
        self.exit_button.setFixedSize(100, 40)
        self.exit_button.clicked.connect(self.close)
        self.header_layout.addWidget(self.exit_button)

        # Chat history
        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        self.chat_history.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.chat_history.setStyleSheet("QTextEdit { padding: 15px; }")
        self.layout.addWidget(self.chat_history)

        # Bottom layout (input + send)
        self.bottom_layout = QHBoxLayout()
        self.layout.addLayout(self.bottom_layout)

        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Type your message here...")
        self.user_input.returnPressed.connect(self.send_message)
        self.user_input.setMinimumHeight(40)
        self.bottom_layout.addWidget(self.user_input, 1)

        self.send_button = QPushButton("Send")
        self.send_button.setFixedSize(120, 40)
        self.send_button.clicked.connect(self.send_message)
        self.bottom_layout.addWidget(self.send_button)

        # Chat session instance
        self.chat_session = ChatSession()

    def apply_dark_theme(self):
        self.setStyleSheet("""
        QWidget {
            background-color: #1E1E2F;
            color: #EDEDED;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            font-size: 15px;
        }

        QTextEdit {
            background-color: #252636;
            border: 1px solid #3E3F4A;
            border-radius: 10px;
            padding: 12px;
            color: #EDEDED;
        }

        QLineEdit {
            background-color: #2D2E3E;
            border: 1px solid #3E3F4A;
            border-radius: 10px;
            padding: 10px;
            font-size: 15px;
            color: #FFFFFF;
        }

        QLineEdit:focus {
            border: 1px solid #00BFFF;
            background-color: #2F3244;
        }

        QPushButton {
            background-color: #00BFFF;
            color: #1E1E2F;
            border: none;
            border-radius: 10px;
            padding: 10px 16px;
            font-size: 15px;
            font-weight: bold;
        }

        QPushButton:hover {
            background-color: #1CA8DD;
        }

        QPushButton:pressed {
            background-color: #008CBA;
        }

        QLabel {
            color: #AAAAAA;
        }
    """)

    #update loading animation 
    def update_loading_animation(self):
        dots = "." * (self.loading_animation_index % 4)
        self.loading_label.setText(f"💬 Thinking{dots}")
        self.loading_animation_index += 1
    #send message
    def send_message(self):
        user_message = self.user_input.text().strip()
        self.loading_label.show()
        self.loading_timer.start(400)
        if not user_message:
            return

        self.chat_history.append(self.format_user_message(user_message))

        self.user_input.clear()

        worker = ReplyWorker(self.chat_session, user_message)
        worker.signals.finished.connect(self.display_bot_response)
        self.threadpool.start(worker)

    #display reply of the bot 
    def display_bot_response(self, response):
        self.loading_timer.stop()
        self.loading_label.hide()
        self.chat_history.append(self.format_bot_message(response))

        self.chat_history.verticalScrollBar().setValue(self.chat_history.verticalScrollBar().maximum())



    def format_user_message(self, message):
        return f"""
        <div style="text-align: left; margin: 10px 0;">
            <div style="
                display: inline-block;
                background-color: #3A3B4F;
                color: #FFFFFF;
                padding: 10px 15px;
                border-radius: 10px;
                max-width: 75%;
                font-weight: normal;
            ">
                <b style="color:#00FFFF;">You:</b><br>{message}
            </div>
        </div>
        """

    def format_bot_message(self, message):
        return f"""
        <div style="text-align: left; margin: 10px 0;">
            <div style="
                display: inline-block;
                background-color: #2D2E3E;
                color: #F7B8F1;
                padding: 10px 15px;
                border-radius: 10px;
                max-width: 75%;
                font-weight: normal;
            ">
                <b style="color:#F7B8F1;">Jenglish:</b><br>{message}
            </div>
        </div>
        """




    #make it possible for the user to upload a file 
    def upload_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File", "", "Documents (*.pdf *.docx)")
        if not file_path:
            return

        if file_path.endswith(".docx"):
            text = self.read_docx(file_path)
        elif file_path.endswith(".pdf"):
            text = self.read_pdf(file_path)
        else:
            self.chat_history.append("<p style='color:orange;'>Unsupported file type.</p>")
            return

        if text:
            filename = os.path.basename(file_path)
            self.uploaded_files[filename] = text
            self.chat_session.load_file_content(text)
            self.chat_history.append(
                f"<p style='color:#90EE90;'>✔️ Uploaded <b>{filename}</b> ({len(text)} characters)</p>"
            )
        else:
            self.chat_history.append(f"<p style='color:red;'>❌ Failed to read {file_path}</p>")


    #read a document of type .docx
    def read_docx(self, file_path):
        try:
            doc = Document(file_path)
            return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
        except Exception as e:
            return f"[DOCX read error: {e}]"

    #read a document of type .pdf 
    def read_pdf(self, file_path):
        try:
            with open(file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                return "\n".join([
                    page.extract_text() for page in reader.pages if page.extract_text()
                ])
        except Exception as e:
            return f"[PDF read error: {e}]"
        
    

class WorkerSignals(QObject):
    finished = Signal(str)

class ReplyWorker(QRunnable):
    def __init__(self, chat_session, message):
        super().__init__()
        self.chat_session = chat_session
        self.message = message
        self.signals = WorkerSignals()

    @Slot()
    def run(self):
        response = self.chat_session.reply(self.message)
        self.signals.finished.emit(response)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ChatbotGui()
    window.show()
    sys.exit(app.exec())
