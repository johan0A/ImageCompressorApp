import os
import glob
from PIL import Image
from tkinter import filedialog
from tkinter import Tk
import shutil
import pillow_heif
from PIL import ImageCms

from PyQt5.QtWidgets import QApplication, QTextEdit, QMainWindow, QVBoxLayout, QPushButton, QFileDialog, QLabel, QComboBox, QLineEdit, QWidget
from PyQt5.QtWidgets import QProgressBar
from PyQt5.QtCore import Qt
from PyQt5 import QtCore, QtGui, QtWidgets

import sys

class EmittingStream(QtCore.QObject):
    """smt to make the textEdit widget work for console display thing idk how it works but it works"""
    
    textWritten = QtCore.pyqtSignal(str)

    def write(self, text):
        self.textWritten.emit(str(text))


def select_images():
    root = Tk()
    root.withdraw()
    file_paths = filedialog.askopenfilenames(filetypes=[("Image files", "*.jpg;*.jpeg;*.png")])
    root.destroy()
    return file_paths

def select_output_folder():
    root = Tk()
    root.withdraw()
    folder_path = filedialog.askdirectory()
    root.destroy()
    return folder_path

def get_all_image_paths(input_folder, recursive=True):
    file_types = ('*.jpg', '*.jpeg', '*.png')
    image_paths = []
    
    if recursive:
        for directory, _, _ in os.walk(input_folder):
            for file_type in file_types:
                image_paths.extend(glob.glob(os.path.join(directory, file_type)))
    else:
        for file_type in file_types:
            image_paths.extend(glob.glob(os.path.join(input_folder, file_type)))
    
    return image_paths

from PIL import ImageCms

def compress_image(input_path, output_path, format=None, quality=85):
    with Image.open(input_path) as img:
        if format and format.upper() == "JPEG" and img.mode == "RGBA":
            img = img.convert("RGB")

        img_format = img.format.upper()

        # Check if the image has an ICC profile and preserve it
        icc_profile = img.info.get("icc_profile")

        save_kwargs = {}
        if icc_profile:
            save_kwargs["icc_profile"] = icc_profile

        # Only use the quality parameter when changing formats
        save_kwargs["quality"] = quality

        img.save(output_path, format=img_format, **save_kwargs)



def compress_images(input_paths, output_folder, format=None, quality=85, progress_callback=None):
    """only works well with HEIF and not JPEG for some obscure reason
    todo: fix JPEG compression
    (btw idk if it works for all the other formats but it should \_(ツ)_/¯)
    """
    for i in range(len(input_paths)):
        input_path = input_paths[i]
        file_name, file_ext = os.path.splitext(os.path.basename(input_path))
        output_path = os.path.join(output_folder, f"{file_name}.{format.lower()}" if format else f"{file_name}{file_ext}")
        original_size = os.path.getsize(input_path)
        print(f"Compressing {input_path} to {output_path}...\nOriginal size: {original_size} bytes")

        compress_image(input_path, output_path, format=(format or file_ext[1:]).lower(), quality=quality)
        compressed_size = os.path.getsize(output_path)

        print(f"Compressed size: {compressed_size} bytes ({round(compressed_size / original_size * 100, 2)}% of original size)\n")

        if compressed_size > original_size:
            print("Compressed image is larger than original, using original instead\n")
            os.remove(output_path)
            shutil.copy(input_path, output_path)
        
        if progress_callback:
            progress_callback(int((i + 1) / len(input_paths) * 100))

class ImageCompressorApp(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.init_ui()
    
    def __del__(self):
       # Restore sys.stdout
       sys.stdout = sys.__stdout__

    def init_ui(self):
        self.setWindowTitle('Image Compressor')

        layout = QVBoxLayout()

        select_images_btn = QPushButton('Select Images', self)
        select_images_btn.clicked.connect(self.select_images)
        layout.addWidget(select_images_btn)

        self.images_label = QLabel('Selected Images: None', self)
        layout.addWidget(self.images_label)

        select_output_folder_btn = QPushButton('Select Output Folder', self)
        select_output_folder_btn.clicked.connect(self.select_output_folder)
        layout.addWidget(select_output_folder_btn)

        self.output_folder_label = QLabel('Output Folder: None', self)
        layout.addWidget(self.output_folder_label)

        self.format_label = QLabel('Output Format:', self)
        layout.addWidget(self.format_label)

        self.format_combobox = QComboBox(self)
        self.format_combobox.addItem('JPEG')
        self.format_combobox.addItem('PNG')
        self.format_combobox.addItem('HEIF')
        self.format_combobox.addItem('WEBP')
        self.format_combobox.addItem('TIFF')
        self.format_combobox.addItem('BMP')
        self.format_combobox.addItem('GIF')
        
        layout.addWidget(self.format_combobox)

        self.quality_label = QLabel('Quality (1-100):', self)
        layout.addWidget(self.quality_label)

        self.quality_input = QLineEdit(self)
        self.quality_input.setText('85')
        layout.addWidget(self.quality_input)

        compress_btn = QPushButton('Compress Images', self)
        compress_btn.clicked.connect(self.compress_images)
        layout.addWidget(compress_btn)

        central_widget = QWidget(self)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
        
        self.progress_bar = QProgressBar(self)
        layout.addWidget(self.progress_bar)
        
        sys.stdout = EmittingStream(textWritten=self.normalOutputWritten)
        self.textEdit = QTextEdit(self)
        self.textEdit.setReadOnly(True)
        layout.addWidget(self.textEdit)
        
        self.resize(700, 500)

    def normalOutputWritten(self, text):
        """smt to make the textEdit widget work for console display thing idk how it works but it works"""
        cursor = self.textEdit.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(text)
        self.textEdit.setTextCursor(cursor)
        self.textEdit.ensureCursorVisible()
    
    def select_images(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_paths, _ = QFileDialog.getOpenFileNames(self, "Select Images", "", "Image files (*.jpg *.jpeg *.png)", options=options)
        if file_paths:
            self.input_paths = file_paths
            self.images_label.setText(f'Selected Images: {len(file_paths)}')

    def select_output_folder(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        folder_path = QFileDialog.getExistingDirectory(self, "Select Output Folder", "", options=options)
        if folder_path:
            self.output_folder = folder_path
            self.output_folder_label.setText(f'Output Folder: {folder_path}')

    def compress_images(self):

        if not hasattr(self, 'input_paths') or not hasattr(self, 'output_folder'):
            return

        format = self.format_combobox.currentText()
        try:
            quality = int(self.quality_input.text())
            if not (1 <= quality <= 100):
                raise ValueError("Invalid quality value")
        except ValueError:
            self.quality_input.setText('85')
            return

        compress_images(self.input_paths, self.output_folder, format=format, quality=quality, progress_callback=self.update_progress)
        
    
    def update_progress(self, progress):
        self.progress_bar.setValue(progress)
    
    def run(self):
        input_paths = self.input_images_edit.text().split(';')
        output_folder = self.output_folder_edit.text()
        format = self.format_combobox.currentText()
        quality = self.quality_slider.value()

        compress_images(input_paths, output_folder, format=format, quality=quality, progress_callback=self.update_progress)



if __name__ == '__main__':
    app = QApplication([])
    window = ImageCompressorApp()
    window.show()
    app.exec_()

# # Example usage
# input_paths = select_images()
# print(input_paths)
# output_folder = select_output_folder()
# print(output_folder)
# compress_images(input_paths, output_folder, format="HEIF", quality=90)