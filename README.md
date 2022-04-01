# Secure Admin- groupFour 
#### A replacement to fail to ban
This project implements an alternative to ```fail2ban``` for ```ssh```, and for the administrative panels of ```Joomla```, ```WordPress```, and ```phpMyAdmin``` and also the project offers a UI through which the parameters such as  ban time, max retries and failure window for each service can be configured.

File Description:
1. ```secure_admin_run.py```: This file is the backbone of the service and has the core logic implemented. This script needs to be executed on a separate terminal using the following command:
```python3 secure_admin_run.py```
2. secure_admin_web.py```: This file createsa a localhost service theoughwhich parameters such as ```bantime```, ```maxretries```  and ```failurewindow``` can be configured.
To execute use the following command in a separate terminal such that this service and  ```secure_admin_run.py```  run on two different terminals simultaneously.
