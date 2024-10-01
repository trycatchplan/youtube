from abc import ABC, abstractmethod
from typing import Dict, List, Any
from PIL import Image, ExifTags
from tinytag import TinyTag
import pygame, pygame.mixer
from pygame.mixer import Sound

import os


class Media(ABC):
  filepath: str
  def __init__(self, filepath):
    self.filepath = filepath

  @classmethod
  def applicable(cls, filepath) -> bool:
    return False

  @abstractmethod
  def info(self) -> Dict[str, Any]:
    return None

  @abstractmethod
  def show(self) -> Dict[str, Any]:
    return None

class ImageMedia(Media):
  @classmethod
  def applicable(cls, filepath) -> bool:
    return 'jpg' in filepath

  def info(self) -> Dict[str, Any]:
    img = Image.open(self.filepath)
    exif = {ExifTags.TAGS[k]: v for k, v in img._getexif().items() if k in ExifTags.TAGS}
    return exif

  def show(self) -> Dict[str, Any]:
    return self.info()

class SoundMedia(Media):
  @classmethod
  def applicable(cls, filepath) -> bool:
    return 'wav' in filepath

  def info(self) -> Dict[str, Any]:
    audio = TinyTag.get(self.filepath)
    return audio.__dict__

  def show(self) -> Dict[str, Any]:
    sound = Sound(self.filepath)
    sound.play()
    return {'filename': self.filepath, 'sound': sound}

class MediaFactory:
  registry: List[Any]

  def __init__(self):
    self.registry = [SoundMedia, ImageMedia]

  def build_all(self, folder) -> List[Media]:
    media_list = []
    files = [filename for filename in os.listdir(folder) if os.path.isfile(os.path.join(folder, filename))]
    for file in files:
      filepath = os.path.join(folder, file)
      media = self.build(filepath)
      if media:
        media_list.append(media)
      else:
        print(f'No applicable Media handlers for {filepath}')
    return media_list

  def build(self, filepath) -> Media:
    for Clz in self.registry:
      if Clz.applicable(filepath):
        return Clz(filepath)
    return None