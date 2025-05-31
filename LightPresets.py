import asyncio
from flask import Flask, request, jsonify

from bleak import BleakClient
from phue import Bridge
import requests
import json

# Govee Light API Details
API_KEY = "23789f96-0f0e-43d2-ab56-b6ea601272b7"
DEVICE_MAC = "D4:60:D3:32:34:38:5D:36"
DEVICE_MODEL = "H6056"
BASE_URL = "https://developer-api.govee.com/v1/devices/control"

headers = {
    "Govee-API-Key": API_KEY,
    "Content-Type": "application/json",
}

# Hue Light API Details
bridge_ip_address = '192.168.2.59'

# Govee Light Functions
async def morning_lights_govee():
    turn_on_lights()
    await set_brightness(90)
    await set_color_temperature(2400)

async def evening_lights_govee():
    turn_on_lights()
    await set_brightness(50)
    await set_color(245, 40, 0)

async def off_lights_govee():
    turn_off_lights()

def turn_on_lights():
    body = {
        "device": DEVICE_MAC,
        "model": DEVICE_MODEL,
        "cmd": {
            "name": "turn",
            "value": "on"
        }
    }
    send_request(body)

def turn_off_lights():
    body = {
        "device": DEVICE_MAC,
        "model": DEVICE_MODEL,
        "cmd": {
            "name": "turn",
            "value": "off"
        }
    }
    send_request(body)

async def set_brightness(brightness):
    body = {
        "device": DEVICE_MAC,
        "model": DEVICE_MODEL,
        "cmd": {
            "name": "brightness",
            "value": brightness
        }
    }
    send_request(body)

async def set_color_temperature(value):
    body = {
        "device": DEVICE_MAC,
        "model": DEVICE_MODEL,
        "cmd": {
            "name": "colorTem",
            "value": value
        }
    }
    send_request(body)

async def set_color(r, g, b):
    body = {
        "device": DEVICE_MAC,
        "model": DEVICE_MODEL,
        "cmd": {
            "name": "color",
            "value": {"r": r, "g": g, "b": b}
        }
    }
    send_request(body)

def send_request(body):
    try:
        response = requests.put(BASE_URL, headers=headers, data=json.dumps(body))
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")

# Hue Light Functions
async def morning_lights_hue():
    print("Setting morning hue lights")
    b = Bridge(bridge_ip_address)
    light_names = b.get_light_objects('name')
    b.set_light('Small lamp', 'on', True)
    b.set_light('Bedroom lamp', 'on', True)
    light_names["Bedroom lamp"].hue = 5000
    b.set_light('Small lamp', 'bri', 140)
    b.set_light('Bedroom lamp', 'bri', 254)

async def evening_lights_hue():
    print("Setting evening hue lights")
    b = Bridge(bridge_ip_address)
    light_names = b.get_light_objects('name')
    b.set_light('Small lamp', 'on', True)
    b.set_light('Bedroom lamp', 'on', True)
    light_names["Bedroom lamp"].hue = 1500
    b.set_light('Small lamp', 'bri', 10)
    b.set_light('Bedroom lamp', 'bri', 140)

async def night_lights_hue():
    print("Setting night hue lights")
    b = Bridge(bridge_ip_address)
    b.set_light('Small lamp', 'on', True)
    b.set_light('Bedroom lamp', 'on', True)
    b.set_light('Small lamp', 'on', False)
    b.set_light('Bedroom lamp', 'bri', 90)

async def off_hue():
    print("Turning off hue lights")
    b = Bridge(bridge_ip_address)
    b.set_light('Small lamp', 'on', False)
    b.set_light('Bedroom lamp', 'on', False)

# ELK light strips
# MAC addresses of the devices
DEVICE_MAC_1 = "A686DE73-5D7A-D84D-0D3E-ACEBCFB0BD40"
DEVICE_MAC_2 = "7D651354-2105-85A0-6669-4A6DFD8714A9"
# Characteristic UUID for controlling the lights
CHARACTERISTIC_CONTROL = "0000fff3-0000-1000-8000-00805f9b34fb"

# Commands
def create_colour_command(red, green, blue):
    return bytearray([0x7E, 0x00, 0x05, 0x03, red, green, blue, 0x00, 0xEF])

def create_brightness_command(brightness):
    return bytearray([0x7E, 0x00, 0x01, brightness, 0x00, 0x00, 0x00, 0x00, 0xEF])

async def morning_lights_ledstrips(mac_address):
    try:
        async with BleakClient(mac_address) as client:
            colour_command = create_colour_command(255, 22, 0)  # Set to Red
            await client.write_gatt_char(CHARACTERISTIC_CONTROL, colour_command)
            brightness_command = create_brightness_command(100)
            await client.write_gatt_char(CHARACTERISTIC_CONTROL, brightness_command)
            await asyncio.sleep(1)  # Wait for 1 second
    except Exception as e:
        print(f"Failed to control the lights on device {mac_address}: {str(e)}")

async def evening_lights_ledstrips(mac_address):
    try:
        async with BleakClient(mac_address) as client:
            colour_command = create_colour_command(255, 7, 0)  # Set to Orange
            await client.write_gatt_char(CHARACTERISTIC_CONTROL, colour_command)
            brightness_command = create_brightness_command(75)
            await client.write_gatt_char(CHARACTERISTIC_CONTROL, brightness_command)
            await asyncio.sleep(1)  # Wait for 1 second
    except Exception as e:
        print(f"Failed to control the lights on device {mac_address}: {str(e)}")

async def night_lights_ledstrips(mac_address):
    try:
        async with BleakClient(mac_address) as client:
            colour_command = create_colour_command(255, 3, 0)  # Set to Dark Red
            await client.write_gatt_char(CHARACTERISTIC_CONTROL, colour_command)
            brightness_command = create_brightness_command(45)
            await client.write_gatt_char(CHARACTERISTIC_CONTROL, brightness_command)
            await asyncio.sleep(1)  # Wait for 1 second
    except Exception as e:
        print(f"Failed to control the lights on device {mac_address}: {str(e)}")

async def off_ledstrips(mac_address):
    try:
        async with BleakClient(mac_address) as client:
            colour_command = create_colour_command(0, 0, 0)  # Set to Black (OFF)
            await client.write_gatt_char(CHARACTERISTIC_CONTROL, colour_command)
            await asyncio.sleep(1)  # Wait for 1 second
    except Exception as e:
        print(f"Failed to control the lights on device {mac_address}: {str(e)}")



app = Flask(__name__)



# Define light functions
async def morning_lights():
    print("Setting morning lights")
    await morning_lights_govee()
    await morning_lights_hue()
    await morning_lights_ledstrips(DEVICE_MAC_1)
    await morning_lights_ledstrips(DEVICE_MAC_2)
    pass

async def evening_lights():
    print("Setting evening lights")
    await evening_lights_govee()
    await evening_lights_hue()
    await evening_lights_ledstrips(DEVICE_MAC_1)
    await evening_lights_ledstrips(DEVICE_MAC_2)
    pass

async def night_lights():
    print("Setting night lights")
    await off_lights_govee()
    await night_lights_hue()
    await night_lights_ledstrips(DEVICE_MAC_1)
    await night_lights_ledstrips(DEVICE_MAC_2)
    pass

async def lights_off():
    print("Turning off all lights")
    await off_ledstrips(DEVICE_MAC_1)
    await off_ledstrips(DEVICE_MAC_2)
    await off_lights_govee()
    await off_hue()
    pass


@app.route('/trigger', methods=['POST'])
def trigger():
    data = request.get_json()
    preset = data.get('preset')

    if preset == "morning":
        asyncio.run(morning_lights())
    elif preset == "evening":
        asyncio.run(evening_lights())
    elif preset == "night":
        asyncio.run(night_lights())
    elif preset == "off":
        asyncio.run(lights_off())
    
    return "Light preset triggered", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)  # Listen on all interfaces
