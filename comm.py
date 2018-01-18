from threading import Thread

import hid
import struct
from timeit import default_timer

import time


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

    def open(self, vid=0x1234, pid=0x0006, blocking=False):
        self.h.open(vid, pid)
        self.h.set_nonblocking(0)
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
            except KeyboardInterrupt:
                break

if __name__ == '__main__':
    hw = Comm()
    hw.open()
    while 1:
        print(hw.encoder_position)
        hw.motor_power = -0.01
        time.sleep(0.1)