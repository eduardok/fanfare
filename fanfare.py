"""
Module that contains the basic implementation of the Fanfare daemon.
"""
import logging
import logging.handlers
import sys
import time

import sensors


class FanfareDaemon(object):
    """
    Basic fanfare daemon functionality:

    * Check the temperature value for your label of interest
    * If the temperature exceeds a treshold, set fan speed to 'full-speed'
    * If the temperature comes below the treshold, set fan speed to 'auto'
    """
    def __init__(self):
        self.log = logging.getLogger("fanfare")
        self.log.setLevel(logging.INFO)
        formatter = logging.Formatter(fmt='[%(name)s] %(message)s')
        handler = logging.handlers.SysLogHandler(
                         facility=logging.handlers.SysLogHandler.LOG_DAEMON,
                         address="/dev/log")
        handler.setFormatter(formatter)
        handler.setLevel(logging.INFO)
        self.log.addHandler(handler)

        self.temp_treshold = 75
        self.poll_time = 30
        self.fan_control_device = '/proc/acpi/ibm/fan'
        self.target_label = 'Physical id 0'
        self.full_speed_on = False

        self.log.info("Starting fanfare daemon")
        sensors.init()

    def set_fan_speed(self, level):
        """
        Set fan speed to level.

        :param level: Speed level. It can be 'full-speed' or 'auto'.
        """
        self.log.info('Setting fan to %s', level)
        with open(self.fan_control_device, 'w') as fan_control:
            fan_control.write('level %s' % level)

    def check_temperature(self):
        """
        Check label value, if it exceeds treshold, set fan to full speed.
        """
        for chip in sensors.iter_detected_chips():
            for feature in chip:
                if feature.label == self.target_label:
                    if feature.get_value() >= self.temp_treshold:
                        if not self.full_speed_on:
                            self.log.info('%s: %.2f exceeds the treshold %.2f',
                                          feature.label, feature.get_value(),
                                          self.temp_treshold)
                            self.set_fan_speed('full-speed')
                            self.full_speed_on = True
                    else:
                        if self.full_speed_on:
                            self.log.info('%s: %.2f back below %.2f',
                                          feature.label, feature.get_value(),
                                          self.temp_treshold)
                            self.set_fan_speed('auto')
                            self.full_speed_on = False

    def run(self):
        """
        Main program loop. Keep checking the temperature and set fan speed.
        """
        while True:
            try:
                self.check_temperature()
                time.sleep(self.poll_time)
            except Exception, details:
                self.log.error("Main loop ended with exception: %s", details)
                self.log.error("Daemon is shutting down...")
                sensors.cleanup()
                sys.exit(1)

