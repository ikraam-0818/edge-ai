import adafruit_dht
import board
from gpiozero import Button
import time

VIBRATION_PIN=17
MQ135_PIN=27

vibration=Button(VIBRATION_PIN)
mq135= Button(MQ135_PIN)
dht=adafruit_dht.DHT22(board.D4)

while True:
	try:
		print('Temp:', dht.temperature, 'C')
		print('Humidity:', dht.humidity, '%')
		print('Vibration:', vibration.is_pressed)
		print('Gas:', mq135.is_pressed)
		print('------')
	except RuntimeError as e:
		print('DHT Error:',e)
	time.sleep(2)
