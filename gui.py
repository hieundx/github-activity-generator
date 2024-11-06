import os
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QCheckBox, QSpinBox, QDateEdit, QPushButton
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtCore import Qt, QDate
from datetime import datetime
import contribute  # Import your existing contribute.py script

class ContributeUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Git Contribution Generator")
        self.setGeometry(100, 100, 400, 400)

        self.set_theme()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Repository
        repo_layout = QHBoxLayout()
        repo_layout.addWidget(QLabel("Repository:"))
        self.repo_input = QLineEdit()
        repo_layout.addWidget(self.repo_input)
        layout.addLayout(repo_layout)

        # No Weekends
        self.no_weekends = QCheckBox("No Weekends")
        layout.addWidget(self.no_weekends)

        # Max Commits
        max_commits_layout = QHBoxLayout()
        max_commits_layout.addWidget(QLabel("Max Commits:"))
        self.max_commits = QSpinBox()
        self.max_commits.setRange(1, 20)
        self.max_commits.setValue(10)
        max_commits_layout.addWidget(self.max_commits)
        layout.addLayout(max_commits_layout)

        # Frequency
        freq_layout = QHBoxLayout()
        freq_layout.addWidget(QLabel("Frequency:"))
        self.frequency = QSpinBox()
        self.frequency.setRange(0, 100)
        self.frequency.setValue(80)
        freq_layout.addWidget(self.frequency)
        layout.addLayout(freq_layout)

        # User Name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("User Name:"))
        self.user_name = QLineEdit()
        name_layout.addWidget(self.user_name)
        layout.addLayout(name_layout)

        # User Email
        email_layout = QHBoxLayout()
        email_layout.addWidget(QLabel("User Email:"))
        self.user_email = QLineEdit()
        email_layout.addWidget(self.user_email)
        layout.addLayout(email_layout)

        # Start Date
        start_date_layout = QHBoxLayout()
        start_date_layout.addWidget(QLabel("Start Date:"))
        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate().addYears(-1))
        self.start_date.setCalendarPopup(True)
        start_date_layout.addWidget(self.start_date)
        layout.addLayout(start_date_layout)

        # End Date
        end_date_layout = QHBoxLayout()
        end_date_layout.addWidget(QLabel("End Date:"))
        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setCalendarPopup(True)
        end_date_layout.addWidget(self.end_date)
        layout.addLayout(end_date_layout)

        # Generate Button
        self.generate_button = QPushButton("Generate Contributions")
        self.generate_button.clicked.connect(self.generate_contributions)
        layout.addWidget(self.generate_button)

       
        # Status Label
        self.status_label = QLabel("")
        layout.addWidget(self.status_label)

    def set_theme(self):
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(240, 240, 240))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(0, 0, 0))
        palette.setColor(QPalette.ColorRole.Base, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(240, 240, 240))
        palette.setColor(QPalette.ColorRole.Text, QColor(0, 0, 0))
        palette.setColor(QPalette.ColorRole.Button, QColor(240, 240, 240))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(0, 0, 0))
        self.setPalette(palette)

    def generate_contributions(self):
        args = contribute.Args(
            no_weekends=self.no_weekends.isChecked(),
            max_commits=self.max_commits.value(),
            frequency=self.frequency.value(),
            repository=self.repo_input.text(),
            user_name=self.user_name.text(),
            user_email=self.user_email.text(),
            day_start=self.start_date.date().toPyDate(),
            day_end=self.end_date.date().toPyDate()
        )
        self.status_label.setText("Generating commits...")

        try:
            print(args)
            os.chdir(os.path.dirname(os.path.abspath(__file__)))
            contribute.validate_args(args)
            directory_exists = contribute.create_repository(args)
            if not directory_exists:
                contribute.configure_git(args)
            contribute.generate_commits(args)
            contribute.push_to_remote(args)
          
            self.status_label.setText("Contributions generated successfully!")
        except Exception as e:
            self.status_label.setText(f"Error: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ContributeUI()
    window.show()
    sys.exit(app.exec())
