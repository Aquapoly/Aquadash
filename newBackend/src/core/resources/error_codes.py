OUT_OF_RANGE_WARNING_CODE = 1000
OUT_OF_RANGE_ALERT_CODE = 2000
UNDEFINED_ALERT_CODE = 3000
EXIT_CODE = 4000

TEMPERATURE_CODE = 1
EC_CODE = 2
PH_CODE = 3
WATER_LEVEL_CODE = 4
HUMIDITY_CODE = 5

class range_error:
    variable = None
    oor_warning= None
    oor_alert = None
    undef_alert= None
    def __init__(self, var_name, err_code) -> None:
        self.variable=var_name
        self.oor_warning= OUT_OF_RANGE_WARNING_CODE + err_code
        self.oor_alert = OUT_OF_RANGE_ALERT_CODE + err_code
        self.undef_alert= UNDEFINED_ALERT_CODE + err_code
    

TP_ERRORS = range_error('Température', TEMPERATURE_CODE)
EC_ERRORS = range_error('Electroconducitvité', EC_CODE)
PH_ERRORS = range_error("Potentiel D'hydrogène (PH)", PH_CODE)
WL_ERRORS = range_error('Niveau d\'eau', WATER_LEVEL_CODE)
HU_ERRORS = range_error("% d'humidité", HUMIDITY_CODE)

PROGRAM_COMPLETION_CODE = EXIT_CODE + 1
SIGINT_CODE = EXIT_CODE + 2
SIGUSR_CODE = EXIT_CODE + 3
UNCAUGHT_EXCEPTION_CODE = EXIT_CODE + 4