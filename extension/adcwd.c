#include <stdio.h>
#include <string.h>

#include "py/nlr.h"
#include "py/obj.h"
#include "py/mphal.h"
#include "py/runtime.h"
#include "py/binary.h"

#include "adcwd.h"
#include "pin.h"
#include "portmodules.h"
#include "modnetwork.h"
#include "py/objtuple.h"
#include "py/objlist.h"
#include "py/stream.h"
#include "py/mperrno.h"

#include "lib/netutils/netutils.h"
#include "lwip/tcp.h"
#include "lwip/timeouts.h"
#include "lwip/init.h"
#include "lwip/init.h"
#include "lwip/tcp.h"
#include "lwip/udp.h"
#include "lwip/raw.h"
#include "lwip/dns.h"
#include "lwip/igmp.h"

/************************************************************
*   CUSTOM MACROS
************************************************************/

#define ADCx                    (ADC1)
#define ADCx_CLK_ENABLE         __HAL_RCC_ADC1_CLK_ENABLE
#define pin_adc_table           pin_adc1
#define clear_pin               (pyb_pin_X7)
#define ADC_pin                 (pyb_pin_X12)

/************************************************************
*   TCP SERVER SETUP CODE
************************************************************/

enum tcp_server_states{
    ES_NONE = 0,
    ES_ACCEPTED,
    ES_RECEIVED,
    ES_CLOSING
};

struct tcp_pcb *awdpcb;

static err_t tcp_server_accept(void *arg, struct tcp_pcb *newpcb, err_t err);
static err_t tcp_server_recv(void *arg, struct tcp_pcb *tpcb, struct pbuf *p, err_t err);
static void tcp_server_error(void *arg, err_t err);

struct tcp_server_struct
{
  u8_t state;             /* current connection state */
  u8_t retries;
  struct tcp_pcb *pcb;    /* pointer on the current tcp_pcb */
  struct pbuf *p;         /* pointer on the received/to be transmitted pbuf */
};

static err_t tcp_server_accept(void *arg, struct tcp_pcb *newpcb , err_t err){
    
    printf("Connection Accepted!\n");
    err_t ret_err;
    
    struct tcp_server_struct *es;

    LWIP_UNUSED_ARG(arg);
    LWIP_UNUSED_ARG(err);

    /* set priority for the newly accepted tcp connection newpcb */
    tcp_setprio(newpcb, TCP_PRIO_MIN);

    /* allocate structure es to maintain tcp connection informations */
    es = (struct tcp_server_struct *)mem_malloc(sizeof(struct tcp_server_struct));

    if (es != NULL){

        printf("Connection success!");
        es->state = ES_ACCEPTED;
        es->pcb = newpcb;
        es->retries = 0;
        es->p = NULL;

        /* pass newly allocated es structure as argument to newpcb */
        tcp_arg(newpcb, es);

        /* initialize lwip tcp_recv callback function for newpcb  */ 
        tcp_recv(newpcb, tcp_server_recv);

        /* initialize lwip tcp_err callback function for newpcb  */
        tcp_err(newpcb, tcp_server_error);

        ret_err = ERR_OK;
        awdpcb = newpcb; 
    
    }

    return ret_err;  

}

static void tcp_server_error(void *arg, err_t err){

    struct tcp_server_struct *es;
    
    LWIP_UNUSED_ARG(err);
    
    printf("Error %d \n", err);
    
    es = (struct tcp_server_struct*)arg;
    
    if (es!= NULL){
        mem_free(es);
    }

}

static err_t tcp_server_recv(void *arg, struct tcp_pcb *new , struct pbuf *p ,err_t err){
    u8_t returned;
    returned = pbuf_get_at(p,0);
    printf("RECEIVED! %u bytes!\n", returned);
    return err;
}

/************************************************************
 * PULSEPIN SETUP
************************************************************/

static void adcwd_configpulsepin(mp_hal_pin_obj_t pin){

    mp_hal_pin_config(pin,MP_HAL_PIN_MODE_OUTPUT,MP_HAL_PIN_PULL_NONE,0);

}

static void adcwd_pulsepin(mp_hal_pin_obj_t pulsepin, uint16_t delaywidth){
    
    mp_hal_pin_high(pulsepin);
    mp_hal_delay_us(delaywidth);
    mp_hal_pin_low(pulsepin);

}

/************************************************************
 * ADC INITIALISATION FUNCTIONS
************************************************************/

static void adcwd_init_adcperiph(ADC_HandleTypeDef *adch){
    
    // ENABLE ADC CLOCK
    ADCx_CLK_ENABLE();

    // ADC CONFIG
    adch->Instance                   = ADCx;
    adch->Init.Resolution            = ADC_RESOLUTION_12B;
    adch->Init.ClockPrescaler        = ADC_CLOCK_SYNC_PCLK_DIV2;
    adch->Init.ContinuousConvMode    = ENABLE;
    adch->Init.DiscontinuousConvMode = DISABLE;
    adch->Init.NbrOfConversion       = 1;
    adch->Init.NbrOfDiscConversion   = 0;
    adch->Init.EOCSelection          = ADC_EOC_SINGLE_CONV;
    adch->Init.ExternalTrigConv      = ADC_EXTERNALTRIGCONV_T1_CC1;
    adch->Init.ExternalTrigConvEdge  = ADC_EXTERNALTRIGCONVEDGE_RISING;
    adch->Init.ScanConvMode          = ADC_SCAN_DISABLE;
    adch->Init.DataAlign             = ADC_DATAALIGN_RIGHT;

    // INIT ADC PERIPH
    HAL_ADC_Init(adch);

}

static void adcwd_config_adc_channel(ADC_HandleTypeDef *adch, uint32_t channel){
    
    ADC_ChannelConfTypeDef sConfig;
    
    sConfig.Channel = channel;
    sConfig.Rank = 1;
    sConfig.SamplingTime = ADC_SAMPLETIME_15CYCLES;
    sConfig.Offset = 0;
    HAL_ADC_ConfigChannel(adch, &sConfig);

}

static void adcwd_init_awd(uint16_t threshold_low, uint16_t threshold_high, ADC_AnalogWDGConfTypeDef *awd, ADC_HandleTypeDef *adch){
    
    // AWD CONFIG
    awd->WatchdogMode   = ADC_CHANNEL_1;
    awd->HighThreshold  = threshold_high;
    awd->LowThreshold   = threshold_low;
    awd->ITMode         = ENABLE;
    awd->WatchdogMode   = ADC_ANALOGWATCHDOG_SINGLE_REG;
    awd->WatchdogNumber = 0;

    // CONFIGURE THE WATCHDOG
    HAL_ADC_AnalogWDGConfig(adch,awd);

}

/************************************************************
 * MICROPYTHON CLASS/METHOD FUCNTIONS
************************************************************/
unsigned int samplecounter;

// this is the actual C-structure for our new object
// ADD CUSTOM ITEMS TO THE WATCHDOG HERE
typedef struct _adcwd_adcwd_obj_t {
    // base represents some basic information, like type
    mp_obj_base_t base;
    // micropython pin obj
    mp_hal_pin_obj_t pin;
    // low adcwd threshold
    uint16_t threshold_low;
    // high awd threshold
    uint16_t threshold_high;
    // adc channel
    int channel;
    // adc config
    ADC_HandleTypeDef handle;
    // watchdog config
    ADC_AnalogWDGConfTypeDef AnalogWDGConfig;

} adcwd_adcwd_obj_t;

static void adcwd_init_adcwd_single(adcwd_adcwd_obj_t *adcwd){

    const pin_obj_t *pin = pin_adc1[adcwd->channel];
    
    // CONFIG GPIO
    mp_hal_pin_config(pin, MP_HAL_PIN_MODE_ADC, MP_HAL_PIN_PULL_NONE, 0);
    
    // CONFIG ADC
    adcwd_init_adcperiph(&adcwd->handle);

    //CONFIG ADC CHANNEL
    adcwd_config_adc_channel(&adcwd->handle, adcwd->channel);

    //CONFIG WATCHDOG
    adcwd_init_awd(adcwd->threshold_low,adcwd->threshold_high,&adcwd->AnalogWDGConfig,&adcwd->handle);

}

// CUTSOMISE THIS PRINT FUNCTION
STATIC void adcwd_adcwd_print( const mp_print_t *print, mp_obj_t self_in, mp_print_kind_t kind ) {
    // get a ptr to the C-struct of the object
    adcwd_adcwd_obj_t *self = MP_OBJ_TO_PTR(self_in);
    // print the number
    printf ("adcwd(%u)", self->channel);
}

STATIC mp_obj_t adcwd_adcwd_make_new( const mp_obj_type_t *type, size_t n_args, size_t n_kw, const mp_obj_t *args ) {
    
    // this checks the number of arguments (min 1, max 1);
    // on error -> raise python exception
    mp_arg_check_num(n_args, n_kw, 2, 2, true);

    // create a new object of our C-struct type
    adcwd_adcwd_obj_t *self = m_new_obj(adcwd_adcwd_obj_t);
    // give it a type
    self->base.type = &adcwd_adcwdObj_type;
    // set AWD class variables
    self->threshold_low = mp_obj_get_int(args[0]);
    self->threshold_high = mp_obj_get_int(args[1]);
    self->channel = ADC_pin->adc_channel;
    self->pin = ADC_pin;
    
    adcwd_configpulsepin(clear_pin);

    //Init the ADC in WD interrupt mode
    adcwd_init_adcwd_single(self);
    adcwd_pulsepin(pyb_pin_X7,10);
    
    return MP_OBJ_FROM_PTR(self);
}

/* PEAKFINDING FUNCTION I.E. MAIN() */
STATIC mp_obj_t adcwd_start_peakfinding(mp_obj_t self_in, mp_obj_t samples){
    
    adcwd_adcwd_obj_t *self =  MP_OBJ_TO_PTR(self_in);
    int num_samples = mp_obj_get_int(samples);
    
    /* CONST DEFINITIONS */
    uint16_t info[10];
    size_t len = sizeof(info);

    err_t errbind;
    err_t errorwrite;
    err_t erroroutput;

    sys_check_timeouts();
    printf("Initialised!");
    
    // INIT FIRST PCB OBJ
    awdpcb = tcp_new();
    if (awdpcb == NULL){
        printf("tcp_new returned NULL");
    }
    else{
        printf("passed!");
    }

    // socket bind to port 9000, any IP
    errbind = tcp_bind(awdpcb, IP_ADDR_ANY, 9000);
    if(errbind == ERR_OK){
        awdpcb = tcp_listen(awdpcb);
        tcp_accept(awdpcb, tcp_server_accept);
    }
    else{
        printf("Error %d", errbind);
    }

    mp_hal_delay_ms(100);
    
    errorwrite = tcp_write(awdpcb,(void*)info,len,0x01);
    printf("%d\n", errorwrite);

    erroroutput = tcp_output(awdpcb);
    printf("%d\n", erroroutput);

    samplecounter = 0;

    printf("Low to high-> %u to %u\n", self->threshold_low , self->threshold_high);
    //HAL_ADC_Start_IT(&self->handle);
    //While loop for samples
    while(samplecounter<num_samples){
        ;
    }

    //HAL_ADC_Stop_IT(&self->handle);
    tcp_close(awdpcb);
    
    return mp_const_none;

}

MP_DEFINE_CONST_FUN_OBJ_2(adcwd_start_peakfinding_obj, adcwd_start_peakfinding);

/************************************************************
 * MICROPYTHON WRAPPER LINKING
************************************************************/

STATIC const mp_rom_map_elem_t adcwd_adcwd_locals_dict_table[] = {
    { MP_ROM_QSTR(MP_QSTR_start_peakfinding), MP_ROM_PTR(&adcwd_start_peakfinding_obj)}
};
STATIC MP_DEFINE_CONST_DICT(adcwd_adcwd_locals_dict,
                            adcwd_adcwd_locals_dict_table);

// create the class-object itself
const mp_obj_type_t adcwd_adcwdObj_type = {
    // "inherit" the type "type"
    { &mp_type_type },
     // give it a name
    .name = MP_QSTR_adcwdObj,
     // give it a print-function
    .print = adcwd_adcwd_print,
     // give it a constructor
    .make_new = adcwd_adcwd_make_new,
     // and the global members
    .locals_dict = (mp_obj_dict_t*)&adcwd_adcwd_locals_dict,
};

/* Micropython mapping for each callable function and */
STATIC const mp_map_elem_t adcwd_globals_table[] = {
    { MP_OBJ_NEW_QSTR(MP_QSTR___name__), MP_OBJ_NEW_QSTR(MP_QSTR_adcwd) },
    { MP_OBJ_NEW_QSTR(MP_QSTR_adcwdObj), (mp_obj_t)&adcwd_adcwdObj_type },
};

/* MICROPYTHON MODULE BINDINGS */
STATIC MP_DEFINE_CONST_DICT (
    mp_module_adcwd_globals,
    adcwd_globals_table
);

const mp_obj_module_t mp_module_adcwd = {
    .base = { &mp_type_module },
    .globals = (mp_obj_dict_t*)&mp_module_adcwd_globals,
};