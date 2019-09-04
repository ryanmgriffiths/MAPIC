# MAPIC Summer Project 2019

## Summary

A software package for wireless control and DAQ from the MAPIC using a __Pyboard D SF3W__. Current features and perforamance include:

* Wifi communication using python socket network module/UDP. Maximum data transfer rate determined to be > 95Mb/s.
* Read and write to two I2C potentiometers at addresses 0x2C and 0x2D. Also scan for I2C addresses.
* Python level interrupt measurements with ADC, in addition to high performance DMA interrupt peakfinding code integrated into Micropython.
* Histogram generation and display in real time.
* Python Tkinter GUI for control and readout.
* Config file to edit default settings and save setup for repeat measurments.

## Python Setup

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
* scipy
* pyusb -> used for flashing firmware to the board

If this doesn't work, one can install each individually with the command:

```shell
$ pip install <module>
```
## Flashing Micropython Firmware

This repo relies on a customised fork of the micropython Github found [here](https://github.com/gyr0code/micropython). In order to flash new firmware to the Pyboard D SF3W board, you need to have an ARM compiler installed, the recommended package is arm-none-eabi-gcc. This can be installed through the command,
```shell
$ sudo apt-get install arm-none-eabi-gcc
```
There is also a windows/linux compiler available for download at [https://launchpad.net/gcc-arm-embedded](https://launchpad.net/gcc-arm-embedded) or using linux command line with [https://launchpad.net/~team-gcc-arm-embedded/+archive/ubuntu/ppa](https://launchpad.net/~team-gcc-arm-embedded/+archive/ubuntu/ppa)

Once installed, navigate to the root folder and then execute the following command to build the micropython cross-compiler.

```shell
$ make -C mpy-cross
```
Then, edit the first line in the Makefile in the ~/ports/stm32 directory so that it reads,

```makefile
BOARD ?= PYBD_SF3
```

Finally, navigate to the ~/micropython directory and parse the following to compile the build,

```shell
$ git submodule update --init
$ cd ports/stm32
$ make
$ sudo make deploy
```

Note that steps other than the final two only need to be carried out once to set up the library.

## Custom Micropython Code

Added a new custom functions to ```adc.c```. There have also been some changes to ADC class in order to facilitate changing the ADC mode. To set up our ADC object we use the code:

```python
# Necessary imports
from pyb import ADC
from machine import Pin

adcpin = Pin("X12")             # set up ADC pin object on pin PIN
adc = ADC(adcpin, mode)         # create ADC object with the ADC pin, triple mode false

# mode can be "SingleDMA", "TripleDMA", "Single".
# "Single" -> Can use adc.read_timed 
# "SingleDMA" -> Can use adc.read_dma
# "TripleDMA" -> Can use adc.read_interleaved
```

Two more sampling modes have been added in the custom firmware, called ```read_dma``` and ```read_interleaved```.

```python
adc = ADC(adcpin, "TripleDMA")      # create ADC object with the ADC pin, triple mode
adc.read_interleaved(num_samples,ipv4)
# adc.read_interleaved(num_samples,ipv4)
# num_samples : integer number of peaks to sample, ideally multiple of 360
# ipv4 : IPV4 address tuple e.g. ("192.168.1.1",5000) 
# returns nothing

adc = ADC(adcpin, "SingleDMA")      # create ADC object with the ADC pin, triple mode
adc.read_dma(num_samples,ipv4)
# adc.read_interleaved(num_samples,ipv4)
# num_samples : integer number of peaks to sample, ideally multiple of 360
# ipv4 : IPV4 address tuple e.g. ("192.168.1.1",5000) 
# returns nothing
```

```python
adc.deinit_setup()            # deinit the adc peripheral, clear configuration
adc = ADC(adcpin, mode)       # reinitialise the adc object with desired mode
```

## Operation

* Connect to the Wi-Fi access point "PYBD" on the readout system.
* Launch the MAPIC.bat file to start the GUI from which one can control the MAPIC and take measurements

## Useful Links

### Python Links
This application requires knowledge and use of the following python libraries/implementations in addition to those installed through pip:

* [Tkinter](https://www.tutorialspoint.com/python/python_gui_programming) used for the Python GUI.
* [Python Socket API](https://docs.python.org/3/library/socket.html) for data transfer with the board.
* [Micropython Language Docs](https://docs.micropython.org/en/latest/) for python development on the board.
* [Micropython for the Pyboard D](https://pybd.io/hw/pybd_sfxw.html) Pyboard D specific features.

### C Links

Links to specific C apis used in the development of this project, as well as some more detailed instructions on micropython development.

* [STMCUBE32F7](https://www.st.com/en/embedded-software/stm32cubef7.html)  HAL libraries used for coding micropython/board control.
* [lwIP UDP API](https://www.nongnu.org/lwip/2_1_x/index.html) lightweight C socket API, used with python sockets for data streaming.
* [Micropython C modules](https://github.com/MikeTeachman/MicroPython_ESP32_psRAM_LoBo_I2S/blob/master/MicroPython_BUILD/components/micropython/esp32/argument_examples.c) more detailed explanations/examples on how to develop micropython functions.


### Hardware Links
Relevant data sheets and technical documentation for the Pyboard D SF3 chip.

* [STM32F72(3)xxx Reference Manual](https://www.st.com/content/ccc/resource/technical/document/reference_manual/group0/c8/6b/6e/ce/dd/f7/4b/97/DM00305990/files/DM00305990.pdf/jcr:content/translations/en.DM00305990.pdf)
* [STM32F723IEK Datasheet](https://www.st.com/en/microcontrollers-microprocessors/stm32f723ze.html#)
