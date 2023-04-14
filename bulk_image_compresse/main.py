import os
import glob
from PIL import Image
from tkinter import filedialog
from tkinter import Tk
import shutil
import pillow_heif
from PIL import ImageCms

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



def compress_images(input_paths, output_folder, format=None, quality=85):
    for input_path in input_paths:
        file_name, file_ext = os.path.splitext(os.path.basename(input_path))
        output_path = os.path.join(output_folder, f"{file_name}.{format.lower()}" if format else f"{file_name}{file_ext}")
        original_size = os.path.getsize(input_path)
        print(f"Compressing {input_path} to {output_path}...\nOriginal size: {original_size} bytes")

        compress_image(input_path, output_path, format=(format or file_ext[1:]).lower(), quality=quality)
        compressed_size = os.path.getsize(output_path)

        print(f"Compressed size: {compressed_size} bytes\n")

        if compressed_size > original_size:
            os.remove(output_path)
            shutil.copy(input_path, output_path)


# Example usage
input_paths = select_images()
print(input_paths)
output_folder = select_output_folder()
print(output_folder)
compress_images(input_paths, output_folder, format="HEIF", quality=90)