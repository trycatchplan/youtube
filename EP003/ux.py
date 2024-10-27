from typing import Dict, List
from gpiozero import Button, LED, LEDBoard, RGBLED
import numpy

import os
import threading
from time import sleep

from media import Media


CYAN = (.0, .6, .8)
ORANGE = (.9, .2, .0)

class UI:
  index = 0
  media_list:List[Media] = []

  def action(self) -> Dict[str, any]:
    media = self.media_list[self.index]
    # return info about length of WAV file
    return media.show()

  def state(self):
    print(f"index: {self.index}")

class Hardware:
  leds: Dict[str, any]
  buttons: Dict[str, Button]
  ui: UI
  def __init__(self, ui):
    self.buttons = {}
    self.leds = {}
    self.ui = ui

  def init(self):
    self.init_button(13, self._on_press_up,  'U')
    self.init_button(19, self._do_nothing,   'D')
    self.init_button(6,  self._do_nothing,   'L')
    self.init_button(26, self._do_nothing,   'R')
    self.init_button(12, self._on_press_ok,  'A')
    self.init_button(16, self._do_nothing,   'B')
    self.init_button(21, self._on_press_start,   'START')
    self.init_button(20, self._do_nothing,   'SELECT')

    self.leds['rgb'] = RGBLED(17, 27, 22, active_high=False, initial_value=CYAN)  # common anode, so pins are low
    self.leds['recording'] = LED(4, initial_value=False)
    self.leds['board'] = LEDBoard(23, 24, 25, initial_value=False)

  def init_button(self, pin, action, help=None):
    button = Button(pin, bounce_time=.07)
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

  def _led_board_sequence(self, sequence):
    # animate LEDBoard based on sequence 
    board = self.leds.get("board")

    # run the sequence in a different thread
    threading.Timer(
      0.0,
      lambda board=board, sequence=sequence: Hardware._set_led_board_sequence(board, sequence)
    ).start()

  def _on_press_up(self):
    next_index = (self.ui.index + 1) % len(self.ui.media_list)
    self.ui.index = next_index

  def _on_press_ok(self):
    info = self.ui.action()
    self._led_board_sequence(Hardware._to_led_board_sequence(self.leds.get('board'), info))

  def _on_press_start(self):
    # TODO call camera to do a capture (turn on "recording" LED while recording) and animate RGB led to match
    # For now, just open a thread that runs for 3 seconds in "red" mode, then 5 seconds in "cyan" mode
    recording = self.leds.get("recording")
    rgb = self.leds.get('rgb')
    board = self.leds.get('board')

    # run the sequence in a different thread
    threading.Timer(
      0.0,
      lambda recording=recording, rgb=rgb, board=board, ui=self.ui: Hardware._set_recording_sequence(recording, rgb, board, ui, None)
    ).start()


  @staticmethod
  def _to_led_board_sequence(board, info) -> List[any]:
    # TODO parse info into a sequence
    # average the sound abs(amplitude) in 0.1 second bins (taking average between channels)
    led_len = len(board)
    sequence = []
    sequence_per_second = 7.0
    _max = 0.0
    ch_left = info.get('left_channel', [])
    ch_right = info.get('right_channel', [])
    sample_rate = info.get('sample_rate', 0.0)
    sample_len = int(sample_rate / sequence_per_second)  # how many samples in 0.1 seconds
    duration = info.get('duration', 0.0)  # in seconds
    if (duration > 0.0):
      for i in range(0, int(duration * sequence_per_second)):  # will be missing the last few bins, but close enough for an LED animation
        ch_left_sub = ch_left[(i * sample_len):((i+1) * sample_len)]
        sample = [abs(v) for v in ch_left_sub]
        sample_average = numpy.average(sample)
        sample_max = max(sample)
        if sample_max > _max:
          _max = sample_max
        sequence.append({
          "duration": 1.0 / sequence_per_second, 
          "leds": Hardware._to_led_board_state(led_len, sample_average, _max),
        })
    
    # set the green, yellow, red "on" if the value is ?25% max, >75% max, or >90% max, respectively
    # e.g. [{duration: N, leds: (True, True, False)}, ...]
    return sequence
  
  @staticmethod
  def _to_led_board_state(num_leds, value, max_value) -> tuple[any]:
    p = value / max_value
    # TODO take into account the number of leds in both the divisions and the return
    print(p)
    if p > .18:
      return (True, True, True)
    elif p > .1:
      return (True, True, False)
    elif p > .05:
      return (True, False, False)
    return (False, False, False)

  @staticmethod
  def _set_led_board(board, states):
    # set the state of the N leds according to the N states
    for idx, v in enumerate(states):
      if v is True:
        board[idx].on()
      else:
        board[idx].off()
  
  @staticmethod
  def _set_led_board_sequence(board, sequence):
    # set the sequence, all in one thread
    for action in sequence:
      states = action.get("leds", (False, False, False))
      Hardware._set_led_board(board, states)
      sleep(action.get("duration", 0.01))

    # turn all LED's off
    Hardware._set_led_board(board, (False, False, False))

  @staticmethod
  def _set_recording_sequence(recording, rgb, board, ui, sequence):
    # TODO make sequencees work with any kind of LED
    recording.on()
    rgb.pulse(on_color=ORANGE)
    sleep(3.0)
    recording.off()

    # perform the main action
    # TODO simplify calling the "action", board, and rgb LED
    info = ui.action()
    sequence = Hardware._to_led_board_sequence(board, info)

    # run the sequence in a different thread
    threading.Timer(
      0.0,
      lambda board=board, sequence=sequence: Hardware._set_led_board_sequence(board, sequence)
    ).start()

    rgb.pulse(on_color=CYAN)
    sleep(5.0)
    rgb.color = CYAN
