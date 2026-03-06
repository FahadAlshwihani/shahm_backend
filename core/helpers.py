import os
from django.core.files.storage import default_storage


def delete_file(file_path):
    """Helper لحذف ملف من الخادم"""
    if file_path and default_storage.exists(file_path):
        default_storage.delete(file_path)


def replace_file(old_file, new_file):
    """Helper لاستبدال ملف بآخر"""
    if old_file:
        delete_file(old_file.path)
    return new_file

