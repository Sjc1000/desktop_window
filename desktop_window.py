#!/usr/bin/env python3

"""
desktop_window a python + gtk desktop window that allows for styled drawing
via cairo.

    Copyright (C) 2016 Steven James Core

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along
    with this program; if not, write to the Free Software Foundation, Inc.,
    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
"""


from gi.repository import Gtk, Gdk, GLib
import threading
import time
import datetime
import subprocess
import socket
import os
import math
import cairo


class asthread(object):

    def __init__(self, daemon=False):
        self.daemon = daemon

    def __call__(self, function):
        def inner(*args, **kwargs):
            thread = threading.Thread(target=function, args=args, 
                                      kwargs=kwargs)
            if self.daemon:
                thread.daemon = True
            thread.start()
            return None
        return inner


class DesktopWindow(Gtk.Window):

    x = 0
    y = 0
    width = 500
    height = 500
    update_delay = 1
    draw_function = None


    def __init__(self):
        Gtk.Window.__init__(self)
        self.screen = self.get_screen()
        self.visual = self.screen.get_rgba_visual()
        self.set_visual(self.visual)
        self.set_decorated(False)
        self.set_app_paintable(True)
        self.set_property('skip-taskbar-hint', True)
        self.set_property('type-hint', Gdk.WindowTypeHint.DESKTOP)
        self.stick()
        self.show_all()
        self.connect('delete-event', Gtk.main_quit)

    def start(self):
        if self.draw_function is None:
            raise ValueError('DesktopWindow.draw_function needs to be set '
                             'before use.')

        threads = [cpu_runner, net_runner]
        for i in threads:
            i()

        self.connect('draw', self.draw_function)
        self.update_loop()
        self.resize(self.width, self.height)
        self.move(self.x, self.y)
        try:
            GLib.MainLoop().run()
        except KeyboardInterrupt:
            print('\nClosing program.')
        return None

    def get_screen_size(self):
        screen = self.get_screen()
        return screen.get_width(), screen.get_height()

    def add_update(self):
        self.queue_draw()
        return None

    @asthread(True)
    def update_loop(self):
        while True:
            time.sleep(self.update_delay)
            GLib.idle_add(self.add_update)
        return None

def rgb(color, alpha=1):
    output = [(color/0x10000) % 0x100 / 255,
              (color/0x100) % 0x100 / 255,
              (color % 0x100) / 255, alpha]              
    return output


cpu_samples = 5
cpu_interval = 0
last_cpu = []


@asthread(True)
def cpu_runner():
    global last_cpu
    if cpu_interval == 0:
        return None
    core = 'cpu'
    while True:
        hz = os.sysconf(os.sysconf_names['SC_CLK_TCK'])
        with open('/proc/stat', 'r') as f:
            prev = {x.split(' ')[0]: x.split(' ')[4] for x in f.read().split('\n')
                    if 'cpu' in x}
        if core not in prev:
            print('[CPU] Core was not found.')
            return None
        time.sleep(cpu_interval)
        with open('/proc/stat', 'r') as f:
            data = {x.split(' ')[0]: x.split(' ')[4] for x in f.read().split('\n')
                    if 'cpu' in x}
        cpu = int(data[core]) - int(prev[core]) / (cpu_interval * hz) * 100
        last_cpu.append(cpu)
        last_cpu = last_cpu[-cpu_samples:]
    return None


def cpu():
    if cpu_interval == 0:
        raise ValueError('[CPU] cpu_interval must be set to 1 or higher for cpu to run.')
    average = 0
    for i in last_cpu:
        average += i
    return average / cpu_samples


net_samples = 2
net_interval = 0
net_interface = 'wlan0'
last_net = []


@asthread(True)
def net_runner():
    global last_net
    if net_interval == 0:
        return None
    path = '/sys/class/net/{}/statistics/'.format(net_interface)
    while True:
        with open(path + 'rx_bytes') as f:
            s_rx = int(f.read())
        with open(path + 'tx_bytes') as f:
            s_tx = int(f.read())
        time.sleep(net_interval)
        with open(path + 'rx_bytes') as f:
            rx = int(f.read())
        with open(path + 'tx_bytes') as f:
            tx = int(f.read())
        down = rx - s_rx
        up = tx - s_tx
        last_net.append({'up': up, 'down': down})
        last_net = last_net[-net_samples:]
    return int(data)


def net_up():
    if net_interval == 0:
        raise ValueError('[Net up] net_interval must be 1 or higher to use '
                         'net up or net down.')
    average = 0
    for i in last_net:
        average += i['up']
    return average / net_samples


def net_down():
    if net_interval == 0:
        raise ValueError('[Net down] net_interval must be 1 or higher to use '
                         'net up or net down.')
    average = 0
    for i in last_net:
        average += i['down']
    return average / net_samples


def brightness(backlight_type='intel_backlight'):
    info = {}
    path = '/sys/class/backlight/' + backlight_type
    try:
        flist = os.listdir(path)
    except FileNotFoundError:
        raise ValueError('[Brightness] Could not find info for that '
                         'backlight type')
    for f in flist:
        if os.path.isfile(path + '/' + f):
            with open(path + '/' + f) as fo:
                info[f] = fo.read().split('\n')[0]
    return int(info['actual_brightness']) / int(info['max_brightness']) * 100


def ram():
    output = {}
    with open('/proc/meminfo', 'r') as mfile:
        data = mfile.read()
    for line in data.split('\n'):
        if line == '':
            continue
        name = line.split(':')[0].strip()
        value = line.split(':')[1].strip().replace('kB', '')
        output[name] = int(value)
    return output['Active'] / output['MemTotal'] * 100


def uptimestr():
    with open('/proc/uptime') as f:
        seconds = float(f.read().split(' ')[0])
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    output = ''
    if days > 1:
        output += 'days: {0:.0}, '.format(days)
    if hours > 1:
        output += 'hours: {0:0.0f}, '.format(hours)
    if minutes > 1:
        output += 'minutes: {0:0.0f}, '.format(minutes)
    output += 'seconds: {0:0.0f}'.format(seconds)
    return output


def uptime():
    with open('/proc/uptime') as f:
        seconds = float(f.read().split(' ')[0])
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    return days, hours, minutes, seconds


def battery(name='BAT1'):
    path = '/sys/class/power_supply/{}/'.format(name)
    if os.path.isfile(path + 'uevent') is False:
        raise ValueError('[Battery] Name {} was not found'.format(name))
    with open(path + 'uevent') as f:
        info = {x.split('=')[0]:x.split('=')[1] for x in f.read().split('\n')
                if '=' in x}
    return info

def battery_percent(name='BAT1'):
    info = battery(name)
    full = int(info['POWER_SUPPLY_CHARGE_FULL'])
    current = int(info['POWER_SUPPLY_CHARGE_NOW'])
    return current/full*100


def battery_current_full_max(name='BAT1'):
    info = battery(name)
    full = int(info['POWER_SUPPLY_CHARGE_FULL'])
    current = int(info['POWER_SUPPLY_CHARGE_NOW'])
    m = int(info['POWER_SUPPLY_CHARGE_FULL_DESIGN'])
    return {'current': current, 'full': full, 'max': m}


last_temp = []

def temp():
    global last_temp
    if os.path.isfile('/sys/class/thermal/thermal_zone0/temp'):
        with open('/sys/class/thermal/thermal_zone0/temp') as f:
            data = int(f.read().split('\n')[0])/1000
    elif os.path.isfile('/proc/acpi/thermal_zone/THM0/temperature'):
        with open('/proc/acpi/thermal_zone/THM0/temperature') as f:
            data = int(f.read().split('\n')[0])
    else:
        return None
    if len(last_temp) < 10:
        for i in range(10):
            last_temp.append(data)
    else:
        last_temp.append(data)
    last_temp = last_temp[-10:]
    average = 0
    for t in last_temp:
        average += t
    return average / 10


graphs = {}

def graph_arc(name, cr, x, y, radius, width, start, end, function, flip=True, 
              hard_max=None, border=True, negative=False):
    width = width/2
    previous_width = cr.get_line_width()
    if name not in graphs:
        graphs[name] = []
    graphs[name].append(function())

    if border is True:
        cr.set_line_width(1)
        cr.arc(x, y, radius+width, start*(math.pi/180), math.radians(end))
        cr.arc_negative(x, y, radius-width, end*(math.pi/180), math.radians(start))
        cr.close_path()
        cr.stroke()

    samples = start - end if start > end else end - start
    samples = samples / 2

    array = graphs[name]
    highest = 0
    if hard_max is None:
        for i in array:
            if i == 0:
                i = 1
            if i > highest:
                highest = i
    else:
        highest = hard_max


    graph_length = start - end if start > end else end - start
    max_items = int(graph_length)
    graphs[name] = graphs[name][-max_items:]

    if flip is True:
        items = graphs[name][::-1]
    else:
        items = graphs[name]

    for i, item in enumerate(items):
        index = i/100*graph_length
        num = item/highest*(width)
        cr.set_line_width(num*2)
        if end > start:
            if negative is True:
                s = math.radians(((((max_items-i)/max_items*(end-start))+(start))))
                e = math.radians(((max_items-i)/max_items*(end-start))+(start)-1)
            else:
                s = math.radians(((i/max_items*(end-start))+(start)))
                e = math.radians((i/max_items*(end-start))+(start)-1)
        else:
            if negative is True:
                s = math.radians(((max_items-i)*(360-start+end))+(start))
                e = math.radians(((max_items-i)*(360-start+end))+(start)-1)
            else:
                s = math.radians((i/max_items*(360-start+end))+(start))
                e = math.radians((i/max_items*(360-start+end))+(start)-1)
        cr.arc_negative(x, y, radius-width+(num), s, e)
        cr.stroke()
    cr.set_line_width(previous_width)
    return None