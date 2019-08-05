/* FUCNTION DEFINITIONS */
#include "py/obj.h"
#include "py/mphal.h"


void     SystemClock_Config(void);
void     Configure_ADC(void);
void     Activate_ADC(void);
static void CPU_CACHE_Enable(void);
void AdcAnalogWatchdog1_Callback()
void ADC_IRQHandler(void)
int main(void)
static void configure_clearpin_pulse(pin_obj_t pulse_pin)
static void clearpin_pulse(pin_ob_t pulse_pin)