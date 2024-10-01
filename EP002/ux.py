from typing import Dict, List
from gpiozero import Button

import os

from media import Media


class UI:
  index = 0
  media_list:List[Media] = []

  def action(self):
    media = self.media_list[self.index]
    print(media.show())

  def state(self):
    print(f"index: {self.index}")

class Hardware:
  buttons: Dict[str, Button]
  ui: UI
  def __init__(self, ui):
    self.buttons = {}
    self.ui = ui

  def init(self):
    self.init_button(13, self._on_press_up,  'U')
    self.init_button(19, self._do_nothing,   'D')
    self.init_button(6,  self._do_nothing,   'L')
    self.init_button(26, self._do_nothing,   'R')
    self.init_button(12, self._on_press_ok,  'A')
    self.init_button(16, self._do_nothing,   'B')
    self.init_button(21, self._do_nothing,   'START')
    self.init_button(20, self._do_nothing,   'SELECT')

  def init_button(self, pin, action, help=None):
    button = Button(pin)
    if not help:
      button.when_pressed = action
    else:
      def when_pressed():
        print(help)
        action()
        self.ui.state()

      button.when_pressed = when_pressed

    self.buttons[pin] = button

  def _do_nothing(self):
    pass

  def _on_press_up(self):
    next_index = (self.ui.index + 1) % len(self.ui.media_list)
    self.ui.index = next_index

  def _on_press_ok(self):
    self.ui.action()