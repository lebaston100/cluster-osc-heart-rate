## General

A `config.ini` was added to configure common parameters without having to rebuild the script.

It defaults to sending osc to the local machine at the VRChat default OSC Port 9000 with path "/avatar/parameters/Heartrate" and a single int number of the current heartrate.

The name set in `device_name` matches all devices *beginning* with this string in case the hardware has it's own auto generated ID suffix.

Please note that the unitypackage included in this repo does not currently work with the modified script without change!

## Tested devices

The script has been tested with a Coospo HW706, but should work with many similar devices as long as they used the standardized Bluetooth LE heartrate service UUID of 180D/2A37

## Usage

- Download the github release file and unzip it
- Add text shader or heartrate display prefab onto avatar
- Modify osc path in config.ini if needed
- Run the exe while your heartrate monitor is discoverable (turned on for the HW706)
- (If your devices is different, take the beginning of the name in the displayed device table and change `device_name` in config.ini to it. Then restart the exe.)
- Enjoy your heartrate live in vrc