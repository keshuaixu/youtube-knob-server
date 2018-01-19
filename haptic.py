from collections import namedtuple

from comm import Comm

PIDParam = namedtuple('PIDParam', ['kp', 'ki', 'kd', 'kff'])


class Haptic:
    def __init__(self, hw: Comm):
        self.hw = hw
        self.vel_pid_param = PIDParam(1, 0, 0, 0)

    def detent(self, position, per_rotation=12, power=0.2):
        return

    def velocity_loop(self):
        while True:
            with self.hw.hid_loop_semaphore:
                pass
