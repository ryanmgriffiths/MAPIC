## dAPIC Summer Project 2019

## Summary

A program for interface with the pyboard inside the APIC box. Allowing datalogging from the onboard ADCs as well as remote control of the digital potentiometers on the pulse stretcher circuit.

### Requirements

* Python 3 and Anaconda package installed on datalogging device.
* Micropyton v1.11
* Pyboard PYBD-SF3-W4F2

### Features

* Wifi communication using python socket network module. Operational data transfer rate ~ 20Mb/s.
* I2C control of two digital potentiometers.
* 2MSPS ADC readout speed: Polling and interrupt routines.


