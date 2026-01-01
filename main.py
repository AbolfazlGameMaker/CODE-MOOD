from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QTextEdit, QPushButton, QMessageBox
from PySide6.QtGui import QColor, QPalette, QFont
from PySide6.QtCore import Qt
from textblob import TextBlob
import matplotlib.pyplot as plt
import sqlite3
import sys

# Database setup
conn = sqlite3.connect('codemood.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY, content TEXT, mood TEXT)''')
conn.commit()

class CodeMoodApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CodeMood - Programmer Mood Tracker")
        self.setGeometry(200, 200, 550, 450)

        self.layout = QVBoxLayout()

        self.label = QLabel("Write your coding experience today:")
        self.label.setFont(QFont("Arial", 12, QFont.Bold))
        self.layout.addWidget(self.label)

        self.text_edit = QTextEdit()
        self.text_edit.setFont(QFont("Arial", 11))
        self.text_edit.setPlaceholderText("Type your thoughts here...")
        self.layout.addWidget(self.text_edit)

        self.analyze_btn = QPushButton("Analyze Mood")
        self.analyze_btn.clicked.connect(self.analyze_mood)
        self.layout.addWidget(self.analyze_btn)

        self.result_label = QLabel("")
        self.result_label.setFont(QFont("Arial", 12))
        self.result_label.setWordWrap(True)
        self.layout.addWidget(self.result_label)

        self.show_chart_btn = QPushButton("Show Mood Chart")
        self.show_chart_btn.clicked.connect(self.show_chart)
        self.layout.addWidget(self.show_chart_btn)

        self.setLayout(self.layout)

        self.mood_colors = {
            "Happy": "#a0e7a0",
            "Angry / Frustrated": "#f08a8a",
            "Sad / Anxious": "#f0d88a",
            "Neutral": "#d0d0d0"
        }

        self.setAutoFillBackground(True)

    def analyze_mood(self):
        text = self.text_edit.toPlainText()
        if not text.strip():
            QMessageBox.warning(self, "Warning", "Please enter your text.")
            return

        blob = TextBlob(text)
        polarity = blob.sentiment.polarity

        if polarity > 0.3:
            mood = "Happy"
        elif polarity < -0.3:
            mood = "Angry / Frustrated"
        elif -0.3 <= polarity <= -0.1:
            mood = "Sad / Anxious"
        else:
            mood = "Neutral"

        self.result_label.setText(f"Detected Mood: {mood}")
        self.set_bg_color(self.mood_colors.get(mood, "#ffffff"))

        # Save to database
        c.execute('INSERT INTO notes (content, mood) VALUES (?, ?)', (text, mood))
        conn.commit()

    def set_bg_color(self, color):
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(color))
        self.setPalette(palette)

    def show_chart(self):
        c.execute('SELECT mood, COUNT(*) FROM notes GROUP BY mood')
        data = c.fetchall()
        if not data:
            QMessageBox.information(self, "Info", "No data to show.")
            return

        moods, counts = zip(*data)
        colors = [self.mood_colors.get(m, "#cccccc") for m in moods]
        plt.figure(figsize=(6,4))
        plt.bar(moods, counts, color=colors)
        plt.title('Mood Tracker Statistics')
        plt.ylabel('Number of Entries')
        plt.tight_layout()
        plt.show()

    def closeEvent(self, event):
        conn.close()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CodeMoodApp()
    window.show()
    sys.exit(app.exec())
    