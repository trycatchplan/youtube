from typing import Dict, List, Any
from signal import pause
import pygame

import os

from ux import UI, Hardware
from media import MediaFactory


def main():
  pygame.init()
  ui = UI()
  hardware = Hardware(ui)

  # configure the buttons
  hardware.init()

  factory: MediaFactory = MediaFactory()

  # load all the /media files
  ui.media_list.extend(factory.build_all('media'))

  # wait for input
  pause()

if __name__ == '__main__':
  print('Welcome to TryCatchPlan')
  main()
