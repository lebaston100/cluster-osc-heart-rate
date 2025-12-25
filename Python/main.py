import asyncio
import struct
import argparse
import configparser
import time

from bleak import BleakScanner, BleakClient
from pythonosc import udp_client  # OSC sending library

# --- BLE Settings ---
HEART_RATE_SERVICE_UUID = "0000180D-0000-1000-8000-00805F9B34FB"  # 180D
HEART_RATE_MEASUREMENT_CHAR_UUID = "00002A37-0000-1000-8000-00805F9B34FB" # 2A37
BATTERY_SERVICE_UUID = "0000180F-0000-1000-8000-00805F9B34FB"  # Battery Service
BATTERY_LEVEL_CHAR_UUID = "00002A19-0000-1000-8000-00805F9B34FB"  # Battery Level

# --- OSC Settings (defined as global variables, initialized later) ---
osc_client = None

# --- Battery Monitoring ---
async def read_battery_level(client: BleakClient):
    try:
        battery_data = await client.read_gatt_char(BATTERY_LEVEL_CHAR_UUID)
        battery_level = int(battery_data[0])
        print(f"Battery Level: {battery_level}%")
    except Exception as e:
        print(f"Could not read battery level: {e}")

# --- Main Process ---
async def run(args):
    def notification_handler(sender, data):
        """
        Function called when heart rate measurement notifications are received
        """
        flags = data[0]
        hr_format = (flags >> 0) & 0x01  # 0: UINT8, 1: UINT16
        
        energy_expended_present = (flags >> 3) & 0x01
        rr_interval_present = (flags >> 4) & 0x01

        heart_rate = 0
        offset = 1

        if hr_format == 0:  # UINT8
            heart_rate = data[offset]
            offset += 1
        else:  # UINT16
            heart_rate = struct.unpack("<H", data[offset:offset+2])[0]
            offset += 2

        print(f"Heart Rate: {heart_rate} bpm")
        
        # Send OSC
        if osc_client:
            try:
                osc_client.send_message(args.osc_path, [heart_rate])
                print(f"OSC Sent: {args.osc_path} {heart_rate}")
            except Exception as e:
                print(f"OSC Send Error: {e}")

        if energy_expended_present:
            energy_expended = struct.unpack("<H", data[offset:offset+2])[0]
            offset += 2
            print(f"  Energy Expended: {energy_expended} joules")

        if rr_interval_present:
            rr_intervals = []
            while offset < len(data):
                rr_interval = struct.unpack("<H", data[offset:offset+2])[0]
                rr_intervals.append(rr_interval / 1024.0)  # in 1/1024 second units
                offset += 2
            print(f"  RR Interval: {rr_intervals} s")

    global osc_client

    # Initialize OSC client
    if args.osc_ip and args.osc_port:
        osc_client = udp_client.SimpleUDPClient(args.osc_ip, args.osc_port)
        print(f"OSC Destination: {args.osc_ip}:{args.osc_port}")
    else:
        print("OSC destination IP address and port not specified. OSC sending will not be performed.")

    print("Scanning BLE devices. This can take a while...")
    
    devices_to_process = []
    try:
        discovered_data = await BleakScanner.discover(timeout=10, return_adv=True)
        for device, advertisement_data in discovered_data:
            devices_to_process.append((device, advertisement_data.service_uuids, device.name, advertisement_data.local_name))
            
    except ValueError:
        discovered_devices = await BleakScanner.discover(timeout=5)
        for device in discovered_devices:
            service_uuids_from_device = device.metadata.get("uuids", []) if hasattr(device, "metadata") else []
            devices_to_process.append((device, service_uuids_from_device, device.name, device.name))

    print("\n--- All Detected Devices ---")
    for device, service_uuids, device_name, local_name in devices_to_process:
        print(f"  Name: {device_name or local_name or 'N/A'}, Address: {device.address}, UUIDs: {service_uuids}")
    print("----------------------------\n")

    target_device = None
    for device, service_uuids, device_name, local_name in devices_to_process:
        current_device_name = device_name or local_name
        
        if current_device_name and args.device_name.lower() in current_device_name.lower():
            print(f"Target device '{args.device_name}' found: {current_device_name} ({device.address})")
            target_device = device
            # device_name_for_osc = current_device_name
            break

    if not target_device:
        print(f"Target device '{args.device_name}' not found.")
        print("Check detected device names and try adjusting device_name in config file or cli.")
        time.sleep(10)
        return

    async with BleakClient(target_device.address) as client:
        if client.is_connected:
            print(f"Connected to {target_device.name} ({target_device.address}).")

            try:
                await client.start_notify(HEART_RATE_MEASUREMENT_CHAR_UUID, notification_handler)
                print("Started heart rate measurement notifications. Press Ctrl+C to exit.")

                # Periodically read battery level
                while True:
                    await read_battery_level(client)
                    await asyncio.sleep(30)  # check battery every 30 seconds
            except Exception as e:
                print(f"An error occurred: {e}")
            finally:
                await client.stop_notify(HEART_RATE_MEASUREMENT_CHAR_UUID)
                print("Stopped notifications.")
        else:
            print("Failed to connect.")

def read_config():
    config = configparser.ConfigParser()
    config.read('config.ini')

    osc_ip = config.get('General', 'osc_ip')
    osc_port = config.get('General', 'osc_port')
    osc_path = config.get('General', 'osc_path')
    device_name = config.get('General', 'device_name')

    return {
        "osc_ip": osc_ip,
        "osc_port": osc_port,
        "osc_path": osc_path,
        "device_name": device_name
    }

def main():
    config_data = read_config()
    print(f"Configuration data: {config_data}")
    
    parser = argparse.ArgumentParser(description="Retrieve heart rate from BLE heart rate monitor and send via OSC.")
    parser.add_argument("--osc_ip", type=str, default=str(config_data["osc_ip"]),
                        help="Destination IP address for OSC")
    parser.add_argument("--osc_port", type=int, default=int(config_data["osc_port"]),
                        help="Destination port number for OSC")
    parser.add_argument("--osc_path", type=str, default=str(config_data["osc_path"]),
                        help="OSC address to send the data to")
    parser.add_argument("--device_name", type=str, default=str(config_data["device_name"]),
                        help="The bluetooth device name to connect to")
    args = parser.parse_args()

    try:
        asyncio.run(run(args))
    except KeyboardInterrupt:
        print("\nProgram terminated.")

if __name__ == "__main__":
    main()