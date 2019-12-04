import bluetooth

def get_nearby_devices():
    return bluetooth.discover_devices(duration=8,
                                      lookup_names=True,
                                      flush_cache=True,
                                      lookup_class=False)
