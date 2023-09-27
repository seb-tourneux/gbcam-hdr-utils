from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QFileDialog, QPushButton, QLineEdit, QStyle
from PySide6.QtCore import Qt
import os
import platform
import subprocess

class FolderSelectorLineWidget(QWidget):
	def __init__(self):
		super(FolderSelectorLineWidget, self).__init__()

		layout = QGridLayout()
		self.setLayout(layout)
		
		file_browser_btn = QPushButton()
		pixmapi = getattr(QStyle, "SP_DirIcon")
		icon = self.style().standardIcon(pixmapi)
		file_browser_btn.setIcon(icon)
		file_browser_btn.setStyleSheet("QPushButton { border: none; }")
		file_browser_btn.clicked.connect(self.open_file_dialog)
		
		file_browser_goto_btn = QPushButton()
		pixmapi_arrow = getattr(QStyle, "SP_FileDialogContentsView")
		icon_arrow = self.style().standardIcon(pixmapi_arrow)
		file_browser_goto_btn.setIcon(icon_arrow)
		file_browser_goto_btn.setStyleSheet("QPushButton { border: none; }")
		file_browser_goto_btn.clicked.connect(self.open_explorer)

		self.folder_line_edit = QLineEdit(self)

		layout.addWidget(self.folder_line_edit, 0, 0)
		layout.addWidget(file_browser_btn, 0, 1)
		layout.addWidget(file_browser_goto_btn, 0, 2)

	def open_file_dialog(self):
		dialog = QFileDialog(self)
		dialog.setFileMode(QFileDialog.FileMode.Directory)
		if dialog.exec():
			self.folderpath = dialog.selectedFiles()
			self.folder_line_edit.setText(self.folderpath[0])
	
	def open_explorer(self):
		path = self.get_folder()
		if path:
			if platform.system() == "Windows":
				os.startfile(path)
			elif platform.system() == "Darwin":
				subprocess.Popen(["open", path])
			else:
				subprocess.Popen(["xdg-open", path])
			
	def get_folder(self):
		if self.folder_line_edit.text():
			return os.path.normpath(self.folder_line_edit.text())
		else:
			return ""



class FolderSelectorWidget(QWidget):
	def __init__(self, label):
		super(FolderSelectorWidget, self).__init__()

		self.main_layout = QVBoxLayout()
		self.setLayout(self.main_layout)
		
		self.dialog = QFileDialog(self)
		self.dialog.setFileMode(QFileDialog.FileMode.Directory)
		
		self.main_layout.setAlignment(Qt.AlignTop)
		
		self.main_layout.addWidget(QLabel(label))
		self.folder_selector_line = FolderSelectorLineWidget()
		self.main_layout.addWidget(self.folder_selector_line)
		
	def get_folder(self):
		return self.folder_selector_line.get_folder()
	
class InOutFoldersSelectorWidget(QWidget):
	def __init__(self):
		super(InOutFoldersSelectorWidget, self).__init__()

		self.main_layout = QHBoxLayout()
		self.setLayout(self.main_layout)
		
		self.in_folder_selector = FolderSelectorWidget("Input directory")
		self.out_folder_selector = FolderSelectorWidget("Output directory")
		
		self.main_layout.addWidget(self.in_folder_selector)
		self.main_layout.addWidget(self.out_folder_selector)
		
	def get_folders(self):
		return (	self.in_folder_selector.get_folder(), 
				    self.out_folder_selector.get_folder())
