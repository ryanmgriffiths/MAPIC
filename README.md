## dAPIC Summer Project 2019

## Summary

A program for interface with the pyboard inside the APIC box. Features include:

* Wifi communication using python socket network module. Operational data transfer rate ~ 20Mb/s.
* I2C control of two digital potentiometers.
* 2MSPS ADC readout speed: Polling and interrupt routines with real time processing.
* Histogram generation.

### Setup

First install [python version 3.7.4](https://www.python.org/downloads/release/python-374/)
In order to install dependencies, open command prompt inside the folder containing requirements.txt and parse the command
```shell
$ pip install -r requirements.txt
```
Which installs the following package versions:
* numpy v1.16.2
* pyserial v3.4
* matplotlib v3.0.3
* future v0.17.1

### Operation
* Once dependencies are installed, connect the control device to the APIC through micro USB.
* Connect to the Wi-Fi access point "PYBD".
* Launch the APIC.exe file to bring up the GUI.

## Extending the Program

This application requires knowledge and use of the following python libraries/implementations in addition to those installed through pip:
* [Tkinter](https://www.tutorialspoint.com/python/python_gui_programming)
* [socket](https://docs.python.org/3/library/socket.html)
* [micropython](https://docs.micropython.org/en/latest/)
* [micropython for the pyboard D](https://pybd.io/hw/pybd_sfxw.html)