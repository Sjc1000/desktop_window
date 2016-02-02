# desktop window

A Python + GTK window that sticks to the desktop and allows for styled drawing via cairo. (Similar to conky)

The desktop_window.py file includes a couple of standard functions for getting things like cpu / ram> so you don't
have to build those yourself.

## Using net up / down or CPU

You need to set a few things before you can use the net up / down or the cpu functions.

Once you have imported the module and set your window (window = desktop_window.DesktopWindow()) you will need to do the following:

For CPU:

window.cpu_interval must be set to a number 1 or higher.
This is how often the cpu info will be grabbed.

For net up / Down:

window.net_interface must be set to the net interface you use. (ie: wlan0)
window.net_interval must be 1 or higher, this is how often the net info is grabbed.

Done! :D

## Variables

| Variable                   | Description                                                 | Required  | Default |
|----------------------------|-------------------------------------------------------------|   :---:   |  :---:  |
| window.update_delay        | The delay between window updates.                           | ** No **  | 1       |
| window.draw_function       | The function that gets called each draw update
                               (see draw function section for more info)                   | ** Yes ** | None    |
| window.x                   | The x position of the window.                               | ** No **  | 0       |
| window.y                   | The y position of the window.                               | ** No **  | 0       |
| window.width               | The width of the window.                                    | ** No **  | 500     |
| window.height              | The height of the window.                                   | ** No **  | 500     |
| desktop_window.cpu_samples |  


### Draw function

the window.draw_function is meant to be a function defined by you. Passed in without the (). desktop_window will call it
every update with the following params.

window:     The DesktopWindow class reference. This will contain all the variables you have set beforehand for easy access.
            (ie: window.width will get the window's width)

context:    The cairo context that you can draw onto. If you're familiar with cairo you will know what this is.


## Functions

It ships with some basic system info related functions to make things easier.

| Function                   | Params               | Description                                                            |
|----------------------------|----------------------|------------------------------------------------------------------------|
| cpu                        | None                 | Returns the current cpu usage.                                         |
| ram                        | None                 | Returns the current ram usage.                                         |
| net_up                     | None                 | Returns the current net up speed in bytes.                             |
| net_down                   | None                 | Returns the current net down speed in bytes.                           |
| brightness                 | backlight_type (/sys/class/backlight_type) Default: intel_backlight      
                                                    | Returns the current brightness level.                                  |
| uptimestr                  | None                 | Returns the current uptime as a string, days hours minutes and seconds |
| uptime                     | None                 | Returns the current uptime as a tuple (days, hours, minutes, seconds)  |
| battery                    | name (/sys/class/power_supply/BAT0) Default: BAT1
                                                    | Returns information about the battery                                  |
| battery_percent            | same as battery      | Returns the current battery percentage                                 |
| battery_current_full_max   | same as battery      | Returns the current battery level, full and designed max of the battery as a tuple   |
| temp                       | None                 | Returns the current temperature of your computer                       |