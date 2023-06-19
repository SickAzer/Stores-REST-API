import os
import re
from typing import Union
from werkzeug.datastructures import FileStorage

from flask_uploads import UploadSet, IMAGES

IMAGE_SET = UploadSet("images", IMAGES)  # set name and allowed extentions


def save_image(image: FileStorage, folder: str = None, name: str = None) -> str:
    """Takes FileStorage and saves it to a folder."""
    return IMAGE_SET.save(image, folder, name)


def get_path(filename: str = None, folder: str = None) -> str:
    """Take image and folder and return full path."""
    return IMAGE_SET.path(filename, folder)


def find_image_any_format(filename: str, folder: str) -> Union[str, None]:
    """Takes a filename and returns an image on any accepted formats."""
    for _format in IMAGES:
        image = f"{filename}.{_format}"
        image_path = IMAGE_SET.path(filename=image, folder=folder)
        if os.path.isfile(image_path):
            return image_path
    return None


def _retrieve_filename(file: Union[str, FileStorage]) -> str:
    """Take FileStorage and return the filename.
    Allows functions to call this for both filenames and FileStorages
    and always returns a file name.
    """
    if isinstance(file, FileStorage):
        return file.filename
    return file


def is_filename_safe(file: Union[str, FileStorage]) -> bool:
    """Check regex and return whether the string matches or not."""
    filename = _retrieve_filename(file)

    allwed_format = "|". join(IMAGES)  # png|svg|jpg...
    regex = f"^[a-zA-Z0-9][a-zA-Z0-9_()-\.]*\.({allwed_format})$"
    return re.match(regex, filename) is not None


def get_basename(file: Union[str, FileStorage]) -> str:
    """Return full name of image in the path."""
    filename = _retrieve_filename(file)
    return os.path.split(file)[1]


def get_extention(file: Union[str, FileStorage]):
    """Return file extention."""
    filename = _retrieve_filename(file)
    return os.path.splitext(file)[1]
