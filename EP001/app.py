from abc import ABC, abstractmethod
from typing import Dict, List, Any
from PIL import Image, ExifTags
from tinytag import TinyTag

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

class ImageMedia(Media):
  @classmethod
  def applicable(cls, filepath) -> bool:
    return 'jpg' in filepath

  def info(self) -> Dict[str, Any]:
    img = Image.open(self.filepath)
    exif = {ExifTags.TAGS[k]: v for k, v in img._getexif().items() if k in ExifTags.TAGS}
    return exif

class SoundMedia(Media):
  @classmethod
  def applicable(cls, filepath) -> bool:
    return 'wav' in filepath

  def info(self) -> Dict[str, Any]:
    audio = TinyTag.get(self.filepath)
    return audio.__dict__

class MediaFactory:
  registry: List[Any]
  def __init__(self):
    self.registry = [SoundMedia, ImageMedia]
    
  def build(self, filepath) -> Media:
    for Clz in self.registry:
      if Clz.applicable(filepath):
        return Clz(filepath)
    return None

def main():
  factory: MediaFactory = MediaFactory()
  files = [filename for filename in os.listdir('media') if os.path.isfile(os.path.join('media', filename))]
  for file in files:
    filepath = os.path.join('media', file)
    print(filepath)
    media = factory.build(filepath)
    if media:
      print(media.info())
    else:
      print('No applicable Media handlers')
    

if __name__ == '__main__':
  print('Welcome to TryCatchPlan')
  main()
