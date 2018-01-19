from collections import namedtuple

import numpy as np
import math

from comm import Comm

PIDParam = namedtuple('PIDParam', ['kp', 'ki', 'kd', 'kff'])

N = 10


def high_pass(x, lim):
    if math.fabs(x) < lim:
        return 0
    else:
        return x


def quad_detent(x, start, end, power):
    mid = (end - start) / 2
    d = math.fabs(end - start) / 2
    output = -(power / (d ** 2)) * ((x - mid) ** 2) + power
    return max(output, 0)


def lin_detent(x, start, end, power):
    mid = (end + start) / 2
    d = math.fabs(end - start) / 2
    high = max(start, end)
    low = min(start, end)
    # print(f'{low}, {mid}, {high}, {x}')
    if low < x < mid:
        return -power
    elif mid <= x < high:
        return power
    else:
        return 0


class Detents:
    def __init__(self):
        self.detents = []

    def add_detent(self, start_position, end_position, power=0.1, callback=None, once=True):
        pass

    @property
    def power(self):
        pass


class Haptic:
    def __init__(self, hw: Comm):
        self.hw = hw
        self.vel_pid_param = PIDParam(1, 0, 0, 0)
        self.last_encoder_pos = self.hw.encoder_position_scaled
        self.d_encoder_position = 0
        self.d_encoder_averaged = 0
        self.d_encoder_averaged_slow = 0;
        self.last_motor_power = self.hw.motor_power
        self.d_motor_power = 0
        self.fly_power = 0
        self.mode = 'stop'

        self.stop_position = self.hw.encoder_position_scaled


    def detent_sin(self, per_rotation=20, power=0.1):
        return math.sin(self.hw.encoder_position_scaled * 2 * math.pi * per_rotation) * power

    def create_detent(self, bump_size=0.2, callback=None):
        pass

    def loop(self):
        while True:
            for i in range(1):
                self.hw.hid_loop_semaphore.acquire()

            enc_now = self.hw.encoder_position_scaled
            self.d_encoder_position = enc_now - self.last_encoder_pos
            self.last_encoder_pos = enc_now
            self.d_encoder_averaged = self.d_encoder_position * 0.7 + self.d_encoder_averaged * 0.3
            self.d_encoder_averaged_slow = self.d_encoder_position * 0.01 + self.d_encoder_averaged_slow * 0.99

            # self.hw.motor_power = self.detent_sin() * high_pass(self.d_encoder_averaged, 0.0012) * 1000

            # self.hw.motor_power = 0.04

            if self.mode == 'stop':
                detent_end = self.stop_position + 0.1
                self.hw.motor_power = lin_detent(enc_now, self.stop_position, detent_end, 0.1)
                if enc_now > detent_end:
                    self.mode = 'play'

            if self.mode == 'play':
                forward_power = 0.045
                if self.d_encoder_averaged_slow <= 0:
                    if self.play_was_not_stopped:
                        self.play_was_not_stopped = False
                        self.stop_position = enc_now
                    detent_end = self.stop_position - 0.1
                    self.hw.motor_power = forward_power + lin_detent(enc_now, self.stop_position, detent_end, 0.1)
                    if enc_now < detent_end:
                        self.mode = 'stop'
                        self.stop_position = enc_now
                else:
                    self.play_was_not_stopped = True
                    self.hw.motor_power = forward_power + high_pass(self.fly_power * 10, 0.1)
                    self.fly_power *= 0.9
                    if self.d_encoder_averaged_slow > 0.00040 and self.hw.motor_power <= 0.046:
                        self.fly_power += self.d_encoder_averaged_slow









            # print(self.stop_position)


if __name__ == '__main__':
    hw = Comm(power_lim=0.5)
    hw.start()

    haptic = Haptic(hw)
    haptic.loop()
