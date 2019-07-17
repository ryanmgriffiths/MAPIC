## dAPIC Summer Project 2019

## Summary

A program for interface with the pyboard inside the APIC box. Allowing datalogging from the onboard ADCs as well as remote control of the digital potentiometers on the pulse stretcher circuit.

### Setup

First install [python version 3.7.4](https://www.python.org/downloads/release/python-374/)
In order to install dependencies, open command prompt inside the folder containging requirements.txt and sparse the command
```console
$ pip install -r requirements.txt
```


### Features

* Wifi communication using python socket network module. Operational data transfer rate ~ 20Mb/s.
* I2C control of two digital potentiometers.
* 2MSPS ADC readout speed: Polling and interrupt routines.


