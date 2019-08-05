#include <stdio.h>
#include <string.h>

#include "py/nlr.h"
#include "py/obj.h"
#include "py/mphal.h"
#include "py/runtime.h"
#include "py/binary.h"

#include "pin.h"
#include "portmodules.h"
#include "stm32f7xx_ll_adc.h"

/* TODO:
function for socket connection and definition

function to define a GPIO pin and send pulses

obect/function to call in python with selectable GPIO pins/ADC pin, selectable 
*/


// ADD MORE HERE:



/* Define macros with board pin names */
#define X1              LL_GPIO_PIN_0       
#define X2              LL_GPIO_PIN_1       
#define X3              LL_GPIO_PIN_2       
#define X4              LL_GPIO_PIN_3       
#define X5              LL_GPIO_PIN_4       
#define X6              LL_GPIO_PIN_5       
#define X7              LL_GPIO_PIN_6       
#define X8              LL_GPIO_PIN_7       
 
// WATCHDOG CONFIGURATION ######################################################

#define ADC_AWD_THRESHOLD_HIGH           ((uint32_t)200)
#define ADC_AWD_THRESHOLD_LOW            ((uint32_t)0)

__IO   uint8_t ubAnalogWatchdog1Status = 0;

// HAL LL FUNCTIONS ############################################################
void Configure_ADC(void) 
{
  /*## Configuration of GPIO used by ADC channels ############################*/
  
  /* Note: On this STM32 device, ADC1 channel 4 is mapped on GPIO pin PA.04 */ 
  
  /* Enable GPIO Clock */
  LL_AHB1_GRP1_EnableClock(LL_AHB1_GRP1_PERIPH_GPIOA);
  
  /* Configure GPIO in analog mode to be used as ADC input */
  LL_GPIO_SetPinMode(GPIOA, X7, LL_GPIO_MODE_ANALOG);
  
  /*## Configuration of NVIC #################################################*/
  /* Configure NVIC to enable ADC1 interruptions */
  NVIC_SetPriority(ADC_IRQn, 0);
  NVIC_EnableIRQ(ADC_IRQn);
  
  /*## Configuration of ADC ##################################################*/
  /* Enable ADC clock (core clock) */
  LL_APB2_GRP1_EnableClock(LL_APB2_GRP1_PERIPH_ADC1);
  
  /*       Software can be optimized by removing some of these checks, if     */
  /*       they are not relevant considering previous settings and actions    */
  /*       in user application.                                               */
  if(__LL_ADC_IS_ENABLED_ALL_COMMON_INSTANCE() == 0)
  { 
    /* Set ADC clock (conversion clock) common to several ADC instances */
    LL_ADC_SetCommonClock(__LL_ADC_COMMON_INSTANCE(ADC1), LL_ADC_CLOCK_SYNC_PCLK_DIV2);
  }

  if (LL_ADC_IsEnabled(ADC1) == 0)
  {
    /* Set ADC data resolution */
    // LL_ADC_SetResolution(ADC1, LL_ADC_RESOLUTION_12B);
    
    /* Set ADC conversion data alignment */
    // LL_ADC_SetResolution(ADC1, LL_ADC_DATA_ALIGN_RIGHT);
    
    /* Set Set ADC sequencers scan mode, for all ADC groups                   */
    /* (group regular, group injected).                                       */
    // LL_ADC_SetSequencersScanMode(ADC1, LL_ADC_SEQ_SCAN_DISABLE);
    
  }

  if (LL_ADC_IsEnabled(ADC1) == 0)
  {
    /* Set ADC group regular trigger source */
    LL_ADC_REG_SetTriggerSource(ADC1, LL_ADC_REG_TRIG_SOFTWARE);
    
    /* Set ADC group regular trigger polarity */
    // LL_ADC_REG_SetTriggerEdge(ADC1, LL_ADC_REG_TRIG_EXT_RISING);
    
    /* Set ADC group regular continuous mode */
    LL_ADC_REG_SetContinuousMode(ADC1, LL_ADC_REG_CONV_CONTINUOUS);
    
    /* Set ADC group regular conversion data transfer */
    // LL_ADC_REG_SetDMATransfer(ADC1, LL_ADC_REG_DMA_TRANSFER_NONE);
    
    /* Specify which ADC flag between EOC (end of unitary conversion)         */
    /* or EOS (end of sequence conversions) is used to indicate               */
    /* the end of conversion.                                                 */
    // LL_ADC_REG_SetFlagEndOfConversion(ADC1, LL_ADC_REG_FLAG_EOC_SEQUENCE_CONV);
    
    /* Set ADC group regular sequencer */
    /* Note: On this STM32 serie, ADC group regular sequencer is              */
    /*       fully configurable: sequencer length and each rank               */
    /*       affectation to a channel are configurable.                       */
    /*       Refer to description of function                                 */
    /*       "LL_ADC_REG_SetSequencerLength()".                               */
    
    /* Set ADC group regular sequencer length and scan direction */
    LL_ADC_REG_SetSequencerLength(ADC1, LL_ADC_REG_SEQ_SCAN_DISABLE);
    
    /* Set ADC group regular sequencer discontinuous mode */
    // LL_ADC_REG_SetSequencerDiscont(ADC1, LL_ADC_REG_SEQ_DISCONT_DISABLE);
    
    /* Set ADC group regular sequence: channel on the selected sequence rank. */
    LL_ADC_REG_SetSequencerRanks(ADC1, LL_ADC_REG_RANK_1, LL_ADC_CHANNEL_4);
  }
  
  
  /*## Configuration of ADC hierarchical scope: ADC group injected ###########*/
    if (LL_ADC_IsEnabled(ADC1) == 0)
  {
    ;
  }
  
  /*## Configuration of ADC hierarchical scope: channels #####################*/
  if (LL_ADC_IsEnabled(ADC1) == 0)
  {
    /* Set ADC channels sampling time */
    /* Note: Considering interruption occurring after each ADC conversion     */
    /*       when ADC conversion is out of the analog watchdog window         */
    /*       selected (IT from ADC analog watchdog),                          */
    /*       select sampling time and ADC clock with sufficient               */
    /*       duration to not create an overhead situation in IRQHandler.      */
    LL_ADC_SetChannelSamplingTime(ADC1, LL_ADC_CHANNEL_1, LL_ADC_SAMPLINGTIME_15CYCLES);
    
  }
      
  /* Set ADC analog watchdog: channels to be monitored */
  LL_ADC_SetAnalogWDMonitChannels(ADC1, LL_ADC_AWD_CHANNEL_1_REG);
  
  /* Set ADC analog watchdog: thresholds */
  LL_ADC_SetAnalogWDThresholds(ADC1, LL_ADC_AWD_THRESHOLD_HIGH, ADC_AWD_THRESHOLD_HIGH);
  LL_ADC_SetAnalogWDThresholds(ADC1, LL_ADC_AWD_THRESHOLD_LOW, ADC_AWD_THRESHOLD_LOW);
  
  
  /*## Configuration of ADC transversal scope: oversampling ##################*/
  
  /* Note: Feature not available on this STM32 serie */
  
  
  /*## Configuration of ADC interruptions ####################################*/
  /* Enable ADC analog watchdog 1 interruption */
  LL_ADC_EnableIT_AWD1(ADC1);
  
}

void Activate_ADC(void)
{
  #if (USE_TIMEOUT == 1)
  uint32_t Timeout = 0; /* Variable used for timeout management */
  #endif /* USE_TIMEOUT */
  
  if (LL_ADC_IsEnabled(ADC1) == 0)
  {
    /* Enable ADC */
    LL_ADC_Enable(ADC1); 
  }
  /*## Operation on ADC hierarchical scope: ADC group regular ################*/
  /* Note: No operation on ADC group regular performed here.                  */
  /*       ADC group regular conversions to be performed after this function  */
  /*       using function:                                                    */
  /*       "LL_ADC_REG_StartConversion();"                                    */
}

void SystemClock_Config(void)
{
  /* Enable HSE clock */
  LL_RCC_HSE_EnableBypass();
  LL_RCC_HSE_Enable();
  while(LL_RCC_HSE_IsReady() != 1)
  {
  };

  /* Set FLASH latency */
  LL_FLASH_SetLatency(LL_FLASH_LATENCY_7);

  /* Enable PWR clock */
  LL_APB1_GRP1_EnableClock(LL_APB1_GRP1_PERIPH_PWR);

  /* Activation OverDrive Mode */
  LL_PWR_EnableOverDriveMode();
  while(LL_PWR_IsActiveFlag_OD() != 1)
  {
  };

  /* Activation OverDrive Switching */
  LL_PWR_EnableOverDriveSwitching();
  while(LL_PWR_IsActiveFlag_ODSW() != 1)
  {
  };

  /* Main PLL configuration and activation */
  LL_RCC_PLL_ConfigDomain_SYS(LL_RCC_PLLSOURCE_HSE, LL_RCC_PLLM_DIV_8, 432, LL_RCC_PLLP_DIV_2);
  LL_RCC_PLL_Enable();
  while(LL_RCC_PLL_IsReady() != 1)
  {
  };

  /* Sysclk activation on the main PLL */
  LL_RCC_SetAHBPrescaler(LL_RCC_SYSCLK_DIV_1);
  LL_RCC_SetSysClkSource(LL_RCC_SYS_CLKSOURCE_PLL);
  while(LL_RCC_GetSysClkSource() != LL_RCC_SYS_CLKSOURCE_STATUS_PLL)
  {
  };

  /* Set APB1 & APB2 prescaler */
  LL_RCC_SetAPB1Prescaler(LL_RCC_APB1_DIV_4);
  LL_RCC_SetAPB2Prescaler(LL_RCC_APB2_DIV_2);

  /* Set systick to 1ms */
  SysTick_Config(216000000 / 1000);

  /* Update CMSIS variable (which can be updated also through SystemCoreClockUpdate function) */
  SystemCoreClock = 216000000;
}

static void CPU_CACHE_Enable(void)
{
  /* Enable I-Cache */
  SCB_EnableICache();

  /* Enable D-Cache */
  SCB_EnableDCache();
}
 
// CUSTOMISED C FUNCTIONS ################################################################

/* Config the pulsing pin */
static void configure_clearpin_pulse(pin_obj_t pulse_pin){
    mp_hal_pin_config(pulse_pin,MP_HAL_PIN_MODE_INPUT,MP_HAL_PIN_PULL_NONE,0);
}

/* Pulse GPIO pin for ~ 1us */
static void clearpin_pulse(pin_ob_t pulse_pin){
    mp_hal_pin_high(pulse_pin);
    mp_hal_delay_us(1);
    mp_hal_pin_low(pulse_pin);
}

void AdcAnalogWatchdog1_Callback()
{
  /* Disable ADC analog watchdog 1 interruption */
  LL_ADC_DisableIT_AWD1(ADC1);
  
  /* Update status variable of ADC analog watchdog 1 */
  ubAnalogWatchdog1Status = 1;

  /* Perform interrupt handling here */
  clearpin_pulse();

  /* Reset status variable of ADC analog watchdog 1 */
  ubAnalogWatchdog1Status = 0;
  
  /* Clear flag ADC analog watchdog 1 */
  LL_ADC_ClearFlag_AWD1(ADC1);
  
  /* Enable ADC analog watchdog 1 interruption */
  LL_ADC_EnableIT_AWD1(ADC1);
}


void ADC_IRQHandler(void)
{
  /* Check whether ADC analog watchdog 1 caused the ADC interruption */
  if(LL_ADC_IsActiveFlag_AWD1(ADC1) != 0)
  {
    /* Clear flag ADC analog watchdog 1 */
    LL_ADC_ClearFlag_AWD1(ADC1);
    
    /* Call interruption treatment function */
    AdcAnalogWatchdog1_Callback();
  }
}

// MICROPYTHON WRAPPED FUNCTIONS/OBJECTS ################################################

int main(void)
{
  /* Enable the CPU Cache */
  CPU_CACHE_Enable();

  /* Configure the system clock to 216 MHz */
  SystemClock_Config();
  
  /* Initialize LED1 */
  LED_Init();
  
  /* Initialize button in EXTI mode */
  UserButton_Init();

  Configure_ADC();
  
  /* Activate ADC */
  /* Perform ADC activation procedure to make it ready to convert. */
  Activate_ADC();

  /* Possibly unnecessary checks */
  if (LL_ADC_IsEnabled(ADC1) == 1)
  {
    LL_ADC_REG_StartConversionSWStart(ADC1);
  }
  else
  {
    /* Error: ADC conversion start could not be performed */
    ;
  }


// MICROPYTHON IMPLEMENTATION ###########################################


STATIC const mp_map_elem_t adcwd_globals_table[] = {
    { MP_OBJ_NEW_QSTR(MP_QSTR___name__), MP_OBJ_NEW_QSTR(MP_QSTR_adcwd) },
};

STATIC MP_DEFINE_CONST_DICT (
    mp_module_adcw_globals,
    adcwd_globals_table
);

const mp_obj_module_t mp_module_adcwd = {
    .base = { &mp_type_module },
    .globals = (mp_obj_dict_t*)&mp_module_adcw_globals,
};

extern const struct _mp_obj_module_t mp_module_adcwd;

#define MICROPY_PORT_BUILTIN_MODULES \
    { MP_OBJ_NEW_QSTR(MP_QSTR_umachine), (mp_obj_t)&machine_module }, \
    ...
    { MP_OBJ_NEW_QSTR(MP_QSTR_adcwd), (mp_obj_t)&mp_module_adcwd },


