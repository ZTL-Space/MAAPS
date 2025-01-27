## BUILD STATUS
[![Docker Image Publish Matrix](https://github.com/ZTL-Space/MAAPS/actions/workflows/docker-image_matrix.yaml/badge.svg)](https://github.com/ZTL-Space/MAAPS/actions/workflows/docker-image_matrix.yaml)
 
## MAAPS

MAAPS - Machine Access And Payments System

MAAPS is a system for managing payments and access to machines designed to be used in Makerspaces.
it uses RFID cards for authentification. 

### Hardware

- Raspberry PI
- Raspberry 3.5 inch Touch Display https://www.amazon.de/dp/B07YV5WYM3
- RFID card reader https://www.amazon.de/dp/B074S9FZC5
- Raspberry Pi Relay Board https://www.amazon.de/dp/B01FZ7XLJ4
- Buchsenleiste extra hoch https://www.amazon.de/dp/B07YDKX8SR/
- Jumper Wire Female-Female 10cm https://www.amazon.de/dp/B07GJLCGG8/

| Pinheader  | Raspi    | Function | Hardware    | Hint |
|------------|----------|----------|-------------|------|
| Pin 1      | 3.3V     | 3.3V     | RFID Pin 1  | Löten, Pin belegt von LCD |
| Pin 34     | GND      | GND      | RFID Pin 3  |      |
| Pin 35     | GPIO 19  | MISO     | RFID Pin 5  |      |
| Pin 36     | GPIO 16  | CS0      | RFID Pin 8  |      |
| Pin 38     | GPIO 20  | MOSI     | RFID Pin 6  |      |
| Pin 40     | GPIO 21  | SCLK     | RFID Pin 7  |      |
|            |          |          |             |      |
| Pin 31     | GPIO  6  | Relais 3 | Relais CH3  |      |
| Pin 33     | GPIO 13  | Relais 2 | Relais CH2  |      |
| Pin 37     | GPIO 26  | Relais 1 | Relais CH1  | Jumper auf Relais board |


### Setup

Add devices to setup/devices.csv, edit setup/wpa_supplicant.conf to match your wlan.

#### Server
Execute these commands in the maaps-server-1 docker container
```
pip install -r requirements.txt
python3 manage.py migrate
```

On first install login to server now, run
```
python3 manage.py createsuperuser
```

to add your first user. 
Open the user admin page https://SERVERIP/webif/user/list, add firstname and lastname to admin user and save.
Open the django admin page at https://SERVERIP/admin/, open the "Tokens" page and get the token identifier for admin (for example U:admin;4c31a8d19b95a7dfe85c)


#### Point of Sale
Install your first point of sale
```
python3 setup.py install <POS_IP>
```
After that, we must write our first admin RFID card. 
Login to the first POS, go to /home/{PI_USERNAME}/MAAPS/client/. 
Use the token you got from the token admin page
```
python3 hardware.py write "YOUR_ADMIN_TOKEN_HERE" 
```
After your first card was created, you can login on the POS with this card and create additional cards.


add prices
```
spaceRentPayment.daily
spaceRentPayment.monthly
```
