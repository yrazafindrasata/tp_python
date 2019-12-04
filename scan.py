import bluetooth, json
from blscan import get_nearby_devices, get_rssi_for_devices

print("Performing inquiry ... ", end='', flush=True)

nearby_devices = get_nearby_devices()
nearby_devices = {row[0]: {"name": row[1]} for row in nearby_devices}

print("Found {} devices".format(len(nearby_devices)))
print("Getting RSSI ... ", end='', flush=True)

get_rssi_for_devices(nearby_devices)

print("Done")
print("Logging ... ", end='', flush=True)

with open("devices.json", "w") as f:
    f.write(json.dumps(nearby_devices))

print("Done")
