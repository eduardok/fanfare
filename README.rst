Fanfare - Fan speed control for your ibm thinkpad laptop
========================================================

This is a very simple program I wrote to avoid my own
laptop to shut down due to overheating.

Turns out in my ThinkPad T420s laptop running Fedora 20
was overheating due to the fact it never increased the
fan speed, even though the core processor would reach
temperatures over 80C, making it shut down when it reached
100C.

So this program is a simple way to keep track of what is
going on with the temperature and proactively set the
fan speed to 'full-speed'. Instead of parsing lm-sensors
output, I chose to depend on the PySensors library [1],
which means I should probably start to package it for
the distros I want Fanfare to be available.

Usage
=====

There's still no setup.py script (hard to take care of
everything in a couple of hours hack), but it's on the
plans, so if you want to run it, check:

::

    #./fanfare-daemon

Inside the top directory.

[1] https://bitbucket.org/blackjack/pysensors/
