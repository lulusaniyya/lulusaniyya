# import smbus2
# import time
# import paho.mqtt.client as mqtt

# # I2C and MQTT Configuration
# I2C_BUS = 1  # Default I2C bus for Raspberry Pi
# MLX9014_ADDR = 0x5A  # Default I2C address for MLX9014
# MQTT_BROKER = "192.168.68.109"  # Change to the MQTT broker IP if needed
# MQTT_PORT = 1883
# MQTT_TOPIC = "sensor/temperature"

# # Initialize I2C and MQTT
# bus = smbus2.SMBus(I2C_BUS)
# client = mqtt.Client()
# client.connect(MQTT_BROKER, MQTT_PORT, 60)

# def read_temperature():
#     # Read temperature data from MLX9014
#     try:
#         # MLX9014 returns temperature data at register 0x07 (example)
#         data = bus.read_i2c_block_data(MLX9014_ADDR, 0x07, 3)
#         temp_raw = (data[1] << 8) | data[0]
#         temp_celsius = temp_raw * 0.02 - 273.15  # Convert to Celsius
#         return temp_celsius
#     except Exception as e:
#         print(f"Failed to read data: {e}")
#         return None

# try:
#     while True:
#         temperature = read_temperature()
#         if temperature is not None:
#             print(f"Temperature: {temperature:.2f} C")
#             client.publish(MQTT_TOPIC, f"{temperature:.2f}")
#         time.sleep(5)  # Data transmission interval

# except KeyboardInterrupt:
#     print("Program terminated")

# finally:
#     bus.close()
#     client.disconnect()

import smbus2
import time
import aiomqtt
import json
import asyncio

# I2C and MQTT Configuration
I2C_BUS = 1  # Default I2C bus for Raspberry Pi
MLX9014_ADDR = 0x5A  # Default I2C address for MLX9014
MQTT_BROKER = "192.168.68.109"  
MQTT_PORT = 1883
MQTT_TOPIC = "sensor/temperature"

# Initialize I2C
bus = smbus2.SMBus(I2C_BUS)

async def read_temperature():
    # Read temperature data from MLX9014
    try:
        # MLX9014 returns temperature data at register 0x07 (example)
        data = bus.read_i2c_block_data(MLX9014_ADDR, 0x07, 3)
        temp_raw = (data[1] << 8) | data[0]
        temp_celsius = temp_raw * 0.02 - 273.15  # Convert to Celsius
        return temp_celsius
    except Exception as e:
        print(json.dumps({"status": "error", "message": "Failed to read data", "error": str(e)}))
        return None

async def main():
    try:
        # Connect to MQTT broker using 'async with'
        async with aiomqtt.Client(MQTT_BROKER) as client:
            print(json.dumps({"status": "connected", "broker": MQTT_BROKER, "port": MQTT_PORT}))

            while True:
                temperature = await read_temperature()
                if temperature is not None:
                    # Send the temperature value in JSON format, without "value" and "unit"
                    output = {
                        "temperature": round(temperature, 2)  # Just include the temperature directly
                    }
                    print(json.dumps(output))  # Print the temperature in JSON format
                    await client.publish(MQTT_TOPIC, json.dumps(output))  # Send the temperature in JSON format
                await asyncio.sleep(5)  # Data transmission interval

    except Exception as e:
        print(json.dumps({"status": "failed", "error": str(e)}))

    finally:
        bus.close()

# Run the async main function
asyncio.run(main())
