# MAPIC Summer Project 2019

## Summary

A program for interface with the pyboard inside the APIC box. Features include:

* Wifi communication using python socket network module. Operational data transfer rate ~ 20Mb/s.
* I2C control of two digital potentiometers.
* 2MSPS ADC readout speed: Polling and interrupt routines with real time processing.
* Histogram generation.

## Setup

### Pip
First install [python version 3.7.4](https://www.python.org/downloads/release/python-374/)
In order to install dependencies, first ensure that python 3 is installed and added to PATH. Then open command prompt inside the folder containing requirements.txt and parse the command
```shell
$ pip install -r requirements.txt
```
If both python 2 and python 3 are installed, use the command
```shell
$ pip3 install -r requirements.txt
```
This installs the following packages for python 3:
* numpy
* pyserial
* matplotlib
* future
* scipy
* pyusb

### Micropython Version
This repo relies on a customised fork of the micropython Github found [here](https://github.com/gyr0code/micropython). To flash this custom firmware to the pyboard, follow the instructions provided for flashing firmware to STM32 devices in the README [here](micropython https://github.com/micropython/micropython).

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