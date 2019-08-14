# MAPIC Summer Project 2019

## Summary

A software package for wireless control and DAQ from the MAPIC using a __Pyboard D SF3W__. Current features and perforamance include:

* Wifi communication using python socket network module. Data transfer rate determined to be ~ 20Mb/s.
* Read and write to two I2C potentiometers at addresses 0x2C and 0x2D. Also scan for I2C addresses.
* Python level interrupt measurements with ADC, as well as a __high performance C implementation of HAL
analog watchdog for STM32__.
* Histogram generation and display in real time.
* Python Tkinter GUI for control and readout.
* Config file to edit default settings and save setup for repeat measurments.

## Setup

### Pip

First install [python version 3.7.4](https://www.python.org/downloads/release/python-374/)
In order to install dependencies, first ensure that python 3 is installed (with pip) and added to PATH. Then open command prompt inside the folder containing requirements.txt and parse the command:

```shell
$ pip install -r requirements.txt
```

In linux or the event that you have both python 2 and 3 installed, you may find that you will need to specify `pip3` explicitly:

```shell
$ pip3 install -r requirements.txt
```

This installs the following packages for python 3:

* numpy
* pyserial
* matplotlib
* future
* scipy
* pyusb -> used for flashing firmware to the board

If this doesn't work, one can install each individually with the command:

```shell
$ pip install <module>
```

### Micropython Version and Development

This repo relies on a customised fork of the micropython Github found [here](https://github.com/gyr0code/micropython). In this tutorial we will only cover the method of flashing custom firmware using linux

To develop the custom micropython version, it is necessary to have an understanding of how to add custom modules, classes, functions and methods to micropython. The first area to discuss is adding a custom module that can be imported from the micropython command line, which for the sake of this tutorial will be called `mymodule` :

```python
>>> import mymodule
```

To add `mymodule` to the list of discoverable modules we need to first make a new `mymodule.c` file in the ~/ports/stm32 directory of micropython. Then add it to the list of source files under `SRC_C` in this directory's `Makefile`:

```Makefile
SRC_C = \
        main.c \
        system_stm32.c \
        ...
        mymodule.c \
```

Then add the following code to setup up the module:


```c++
#include <stdio.h>

/* Entry to the global table, first defines name of callable object */
/* second entry is the */
STATIC const mp_map_elem_t mymodule_globals_table[] = {
    { MP_OBJ_NEW_QSTR(MP_QSTR___name__), MP_OBJ_NEW_QSTR(MP_QSTR_mymodule) },
};

STATIC MP_DEFINE_CONST_DICT (
    mp_module_mymodule_globals,
    mymodule_globals_table
);

const mp_obj_module_t mp_module_mymodule = {
    .base = { &mp_type_module },
    .globals = (mp_obj_dict_t*)&mp_module_mymodule_globals,
};
```



## Operation

* Once dependencies are installed, connect the control device to the APIC through micro USB.
* Connect to the Wi-Fi access point "PYBD".
* Launch the APIC.exe file to bring up the GUI.

## Useful Links

This application requires knowledge and use of the following python libraries/implementations in addition to those installed through pip:

* [Tkinter](https://www.tutorialspoint.com/python/python_gui_programming)
* [Socket](https://docs.python.org/3/library/socket.html)
* [Micropython](https://docs.micropython.org/en/latest/)
* [Micropython for the pyboard D](https://pybd.io/hw/pybd_sfxw.html)