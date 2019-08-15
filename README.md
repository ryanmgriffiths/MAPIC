# MAPIC Summer Project 2019

## Summary

A software package for wireless control and DAQ from the MAPIC using a __Pyboard D SF3W__. Current features and perforamance include:

* Wifi communication using python socket network module/UDP. Data transfer rate determined to be ~ 20Mb/s.
* Read and write to two I2C potentiometers at addresses 0x2C and 0x2D. Also scan for I2C addresses.
* Python level interrupt measurements with ADC, as well as a __high performance C implementation of HAL
analog watchdog for STM32__.
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
* future
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

## Micropython Development

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
/* Important includes */
#include <stdio.h>
#include <string.h>

#include "py/nlr.h"
#include "py/obj.h"
#include "py/runtime.h"
#include "py/binary.h"
#include "portmodules.h"
#include "py/mphal.h"           /* useful mphal macros here */

/* Entry to the global table, first defines name of callable object */
/* __name__ gives the module a name -> mymodule                     */
STATIC const mp_map_elem_t mymodule_globals_table[] = {
    { MP_OBJ_NEW_QSTR(MP_QSTR___name__), MP_OBJ_NEW_QSTR(MP_QSTR_mymodule) },
};

STATIC MP_DEFINE_CONST_DICT (
    mp_module_mymodule_globals,
    mymodule_globals_table
);
/* Creates the module and adds to globals */
const mp_obj_module_t mp_module_mymodule = {
    .base = { &mp_type_module },
    .globals = (mp_obj_dict_t*)&mp_module_mymodule_globals,
};
```

Now to add a class and method called `custom` and `customise` respectively, we require several actions. First we define a `struct` that will hold our class variables, we will call this `_mymodule_custom_obj_t`.



```C
typedef struct _mymodule_custom_obj_t {
    // base represents some basic information, like type
    mp_obj_base_t base;
    // add more custom variables here
    int custom_var
} mymodule_custom_obj_t;
```

```C
/* Add a print function for the class, called in class construction */
STATIC void adcwd_adcwd_print( const mp_print_t *print, mp_obj_t self_in, mp_print_kind_t kind ) {
    // get a ptr to the C-struct of the object
    mymodule_custom_obj_t *self = MP_OBJ_TO_PTR(self_in);
    // assign the print for when mymodule.custom is called in python
    printf ("custom(%d)", self->custom_var);
}

/* Class constructor function , called in class construction*/
STATIC mp_obj_t mymodule_custom_make_new( const mp_obj_type_t *type, size_t n_args, size_t n_kw, const mp_obj_t *args ) {
    
    // this checks the number of arguments (min 1, max 1);
    // on error -> raise python exception
    mp_arg_check_num(n_args, n_kw, 1, 1, true);
    
    // create an instance of our class
    mymodule_custom_obj_t self* = m_new_obj(mymodule_custom_obj_t)
    
    // give it a type
    self->base.type = &mymodule_customObj_type;
    
    // assign first argument supplied in python to the custom_var
    self->custom_var = arg[0]
    
    return MP_OBJ_FROM_PTR(self);
}

    // create the class-object itself
const mp_obj_type_t mymodule_customdObj_type = {
    // "inherit" the type "type"
    { &mp_type_type },
     // give it a name - this is mymodule.custom() in python
    .name = MP_QSTR_custom,
     // give it a print-function
    .print = mymodule_hello_print,
     // give it a constructor
    .make_new = mymodule_hello_make_new,
     // and the global members
    .locals_dict = (mp_obj_dict_t*)&mymodule_hello_locals_dict,

};

/* Add a local dict for the class, fill this with class methods */
STATIC const mp_rom_map_elem_t adcwd_adcwd_locals_dict_table[] = {};
STATIC MP_DEFINE_CONST_DICT(mymodule_custom_locals_dict,
                            mymodule_custom_locals_dict_table);
```

For this to compile, you may find it helpful to add the following line at the beggining of the program or in a header file. 

```C
extern const mp_obj_type_t mymodule_customObj_type;
```

Finally go back and add this class with the code below, and add the line `Q(custom)` to the `qstrdefsport.h` file.

```C
STATIC const mp_map_elem_t adcwd_globals_table[] = {
    { MP_OBJ_NEW_QSTR(MP_QSTR___name__), MP_OBJ_NEW_QSTR(MP_QSTR_adcwd) },
    { MP_OBJ_NEW_QSTR(MP_QSTR_custom), (mp_obj_t)&mymodule_customObj_type },
};
```
## Custom Micropython Module

The custom module developed for this application is named ```adcwd``` and can be imported in micropython.

ADD DEFINITIONS AND THINGS HERE!


## Operation

* Once dependencies are installed, connect the MAPIC to a power source via usb.
* Connect to the Wi-Fi access point "PYBD" on the readout system.
* Launch the MAPIC.bat file to start the GUI from which one can control the MAPIC and take measurements

## Useful Links

This application requires knowledge and use of the following python libraries/implementations in addition to those installed through pip:

* [Tkinter](https://www.tutorialspoint.com/python/python_gui_programming)
* [Socket](https://docs.python.org/3/library/socket.html)
* [Micropython](https://docs.micropython.org/en/latest/)
* [Micropython for the pyboard D](https://pybd.io/hw/pybd_sfxw.html)