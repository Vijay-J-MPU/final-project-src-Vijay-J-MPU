import syslog
import time


class PIRMonitor:

    def __init__(self, device="/dev/pir"):
        self.device = device

    def wait_for_motion(self):

        with open(self.device, "r") as f:

            data = f.read()

            if data:
                syslog.syslog(syslog.LOG_INFO,
                              "MOTION DETECTED")

                return True

        return False
