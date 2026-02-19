# Sensors
enable the execution of all scripts
```sh
chmod +x deploy/*
```

## Sensor list

In `services/constants.py`, you must add a line to the SENSOR_ID_TO_I2C_ADDR variable, linking the sensor id from the aquadash web app to the i2c address of the sensor (can be found by running `i2cdetect -y 1`). 
Careful, they are in hexadecimal format!

## Crontab jobs
All crontab jobs are in the `sensors/crontab` folder. 

( ***i*** ) - Files with the extension `.disable` will be ignored when updating the jobs.


Update all crontab jobs : (sudo is important)
```sh
sudo ./deploy/enable-crontab-jobs.sh
```
Disable all crontab jobs :
```sh
sudo ./deploy/disable-crontab-jobs.sh
```
Crontab commands are run as root, because to read I2C sensors root access is required, and also to be able to log into /var/log/crontab. To check all crontab jobs currently running (as root), you can run :
```sh
sudo crontab -l
```
## Actuator systemcl service
The actuator is ran using systemcl.
Create the systemcl service for actuator :
```sh
sudo ./deploy/enable-actuator.sh
```
Disable the actuator service :
```sh
sudo ./deploy/disable-actuator.sh
```

## Debugging crontab jobs
Debug (watch logs in console)
```
tail -f /var/log/syslog
```
Logfile path for our scripts run by crontab
```
/var/log/cron.log
```
## Debugging actuator systemcltl service
Use this to get the logs of the actuator service currently running
```sh
sudo journalctl -u actuator.service
```
You can get the 10 most recent logs of the actuator service using 
```sh
sudo journalctl -u actuator.service -f
```

## Troubleshooting
If for some reason the user mode crontab does not start, it may because of the output redirection to `/var/log/crontab/cron.log`.
To change the permissions of `o`thers to `r`ead and `w`rite:
```sh
sudo chmod o=rw /var/log/crontab/cron.log
```