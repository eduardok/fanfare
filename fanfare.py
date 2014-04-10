# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# See LICENSE for more details.
#
# Copyright: Lucas Meneghel Rodrigues 2013-2014
# Author: Lucas Meneghel Rodrigues <lmr@redhat.com>

"""
Module that contains the basic implementation of the Fanfare daemon.
"""
import logging.handlers
import os
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
        if os.getuid() != 0:
            self.log.error('This program must run as root, as it needs access '
                           'to the fan control device %s. Exiting...',
                           self.fan_control_device)
            sys.exit(2)

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
