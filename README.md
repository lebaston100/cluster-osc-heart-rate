# cluster-osc-heart-rate

This is a modified fork of [github.com/tfuru/cluster-osc-heart-rate](https://github.com/tfuru/cluster-osc-heart-rate).

The Python Script was modified and build/release scripts were added for windows .exe builds. Other code currently remains unchanged and untested.

---

### Original Readme (translated):

This is a sample for using the cluster OSC feature to display and utilize heart‑rate sensor values inside a world.


## Overview
Heart‑rate sensor device  
[README](./M5StickC/osc-heart-rate/README.md)
- M5StickC Plus2 
- GROVE – Heart‑rate Sensor  

Unity (Cluster Creator Kit Script)  
[README](./Unity/README.md)
- cluster-osc-heart-rate.unitypackage  

Heart‑rate armband -> PC -> OSC  
Version without device creation — display heart rate in the world using a commercially available heart‑rate armband  
[README](./Python/README.md)  
- Coospo HW706
- Python script 


## Sample cluster world
[OSC Heart‑rate Sensor Sample](https://cluster.mu/w/1f5c2d7d-23d3-45f3-b7c3-3f770c4ca261)  
If you have a heart‑rate sensor device, you can test the display.  
1. Launch the cluster app
2. Open Settings -> Enable OSC Receiving
3. Check the IP address and port
4. Turn on the heart‑rate sensor device and press the `M% button`
5. Connect to the Wi‑Fi AP `OSC App` using a smartphone, etc.
6. Configure SSID, password, OSC device name, destination IP address, and port
7. Attach the sensor to your earlobe
8. Confirm that the heart rate is displayed in the cluster world