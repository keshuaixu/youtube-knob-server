import logging
from threading import Thread, BoundedSemaphore

import hid
import struct
from timeit import default_timer

import time

ppr = 768


class Comm:
    def __init__(self):
        self.h = hid.device()
        self.data_in = b''
        self.data_out = b''
        self.motor_power = 0.
        self.encoder_position = 0
        self.running = True
        self.loop_thread = Thread(target=self.loop, daemon=True)
        self.loop_frequency_timer = default_timer()
        self.elapsed_time = 0
        self.hid_loop_semaphore = BoundedSemaphore(value=1)

    def open(self, vid=0x1234, pid=0x0006):
        while True:
            try:
                self.h.open(vid, pid)
                self.h.set_nonblocking(0)
            except (OSError, ValueError):
                logging.warning('failed to open port. retrying')
                self.h.close()
                time.sleep(0.5)
            else:
                break

    def start(self, blocking=False):
        self.loop_thread.start()
        if blocking:
            self.loop_thread.join()

    def loop(self):
        while self.running:
            try:
                now = default_timer()
                self.elapsed_time = now - self.loop_frequency_timer
                self.loop_frequency_timer = now

                data_in = self.h.read(8)
                self.encoder_position += struct.unpack('i4x', struct.pack('8B', *data_in))[0]
                self.h.write(struct.pack('f4x', self.motor_power))
                try:
                    self.hid_loop_semaphore.release()
                except ValueError:
                    pass
            except (ValueError, OSError):
                logging.warning('reconnecting hid')
                self.open()
            except KeyboardInterrupt:
                break
            except Exception as e:
                logging.exception(e)

    @property
    def encoder_position_scaled(self, wrap=False):
        if wrap:
            return (self.encoder_position / ppr) % 1
        else:
            return self.encoder_position / ppr


if __name__ == '__main__':
    hw = Comm()
    hw.start()
    while 1:
        print(hw.encoder_position)
        hw.motor_power = -0.01
        time.sleep(0.1)
