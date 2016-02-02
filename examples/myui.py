#!/usr/bin/env python3

"""
Make sure to put this in the same directory as the desktop_window.py file
"""


import desktop_window as desktop
import datetime
from math import radians as rads


bg = 0x3399A8
bga = 0.1

fg = [0x3399A8, 0x3399A8, 0x06D46C,
      0x06D46C, 0xF4E730, 0x3399A8]

tc = [fg[0], fg[2]]

fga = 0.8


def date_suffix(date):
    if date in [1, 21, 31]:
        return 'st'
    if date in [2, 22]:
        return 'nd'
    if date in [3, 23]:
        return 'rd'
    return 'th'


def draw(w, c):
    # Draw the backgrounds

    c.set_line_width(50)
    c.set_source_rgba(*desktop.rgb(bg, bga))


    c.arc(0, w.height, 150, rads(270), rads(0))
    c.stroke()

    c.arc(320, w.height, 100, rads(180), rads(0))
    c.stroke()

    c.arc(570, w.height, 80, rads(180), rads(0))
    c.stroke()

    c.arc(w.width-570, w.height, 80, rads(180), rads(0))
    c.stroke()

    c.arc(w.width-320, w.height, 100, rads(180), rads(0))
    c.stroke()

    c.arc(w.width, w.height, 150, rads(0), rads(270))
    c.stroke()

    # End of background section


    c.set_line_width(25)
    c.set_source_rgba(*desktop.rgb(fg[0],fga))


    # Cpu
    cpu = desktop.cpu()

    c.arc(0, w.height, 150, rads(270), rads(270+(cpu/100*90)))
    c.stroke()


    # Net up

    c.set_source_rgba(*desktop.rgb(fg[1],fga))
    desktop.graph_arc('net_up', c, 320, w.height, 100, 50, 180, 0, desktop.net_up, border=False) 
    
    # Battery

    c.set_source_rgba(*desktop.rgb(fg[2], fga))
    battery = desktop.battery_current_full_max('BAT1')
    m = 180+(battery['full']) / battery['max'] * 180
    
    c.set_line_width(35)
    c.arc(570, w.height, 80, rads(m), rads(0))
    c.stroke()
    c.set_line_width(25)

    percent = 180+battery['current']/battery['full']*(m-180)
    c.arc(570, w.height, 80, rads(180), rads(percent))
    c.stroke()

    # Temp

    c.set_source_rgba(*desktop.rgb(fg[3], fga))
    temp = desktop.temp()

    c.arc_negative(w.width-570, w.height, 80, rads(360), rads(360-(temp/100*180)))
    c.stroke()

    # Net down

    c.set_source_rgba(*desktop.rgb(fg[4], fga))
    desktop.graph_arc('net_down', c, w.width-320, w.height, 100, 50, 180, 360, desktop.net_down, negative=True, border=False) 
    
    # Ram

    c.set_source_rgba(*desktop.rgb(fg[5], fga))
    ram = desktop.ram()

    c.arc_negative(w.width, w.height, 150, rads(270), rads(270-(ram/100*90)))
    c.stroke()


    # Text

    c.select_font_face('Terminal Bold', 0, 1)
    c.set_font_size(25)


    dtime = datetime.datetime.now()
    
    # Day name

    c.set_source_rgba(*desktop.rgb(tc[0], fga))
    c.move_to(15, w.height-50)
    c.show_text(dtime.strftime('%a'))

    # Day of month

    c.set_font_size(20)
    c.set_source_rgba(*desktop.rgb(tc[1], fga))
    c.move_to(15, w.height-30)
    c.show_text(str(dtime.day))

    # Day suffix

    c.set_font_size(10)
    c.move_to(45, w.height-30)
    c.show_text(str(date_suffix(dtime.day)))


    # AM / PM

    c.set_font_size(14)
    c.move_to(w.width-36, w.height-30)
    c.show_text(dtime.strftime('%p'))

    # Time

    c.set_source_rgba(*desktop.rgb(tc[0], fga))
    c.set_font_size(25)
    c.move_to(w.width-90, w.height-50)
    c.show_text(dtime.strftime('%I:%M'))

    return None


if __name__ == '__main__':
    # Settings

    desktop.net_interface = 'wlan0'
    desktop.net_interval = 1
    desktop.cpu_interval = 1

    #

    window = desktop.DesktopWindow()
    window.update_delay = 1
    window.draw_function = draw
    window.x = 0
    window.y = 550
    window.width, window.height = window.get_screen_size()
    window.height = window.height-550
    window.start()