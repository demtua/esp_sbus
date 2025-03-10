
# --- Global Channel Settings ---
CHANNEL_VALUES = {
    'roll': 992,
    'throttle': 992,
    'pitch': 992,
    'yaw': 192,
    'arm': 192,
    'mode': 200,
    'altitude_hold': 1500  # (500 = ON, 1500 = OFF)
}
invertChannel = {
    'roll': False,
    'throttle': False,
    'pitch': False,
    'yaw': False,
    'arm': False,
    'mode': False,
    'altitude_hold': False,
}
SMOOTHING_FACTOR = 0.5
last_transmitted = {
    'roll': None,
    'throttle': None,
    'pitch': None,
    'yaw': None,
    'arm': None,
    'mode': None,
    'altitude_hold': None,
}
channel_order = ['roll', 'pitch', 'yaw', 'throttle', 'arm', 'mode', 'altitude_hold']


def build_sbus_frame(channels):
    """
    Pack 16 channel values (11 bits each) into a 25-byte SBUS frame.
    """
    frame = bytearray(25)
    frame[0] = 0x0F  # Start byte
    frame[1] = channels[0] & 0xFF
    frame[2] = (((channels[0] >> 8) & 0x07) | ((channels[1] & 0x07FF) << 3)) & 0xFF
    frame[3] = (((channels[1] >> 5) & 0x3F) | ((channels[2] & 0x07FF) << 6)) & 0xFF
    frame[4] = (channels[2] >> 2) & 0xFF
    frame[5] = (((channels[2] >> 10) & 0x01) | ((channels[3] & 0x07FF) << 1)) & 0xFF
    frame[6] = (((channels[3] >> 7) & 0x0F) | ((channels[4] & 0x07FF) << 4)) & 0xFF
    frame[7] = (((channels[4] >> 4) & 0x7F) | ((channels[5] & 0x07FF) << 7)) & 0xFF
    frame[8] = (channels[5] >> 1) & 0xFF
    frame[9] = (((channels[5] >> 9) & 0x03) | ((channels[6] & 0x07FF) << 2)) & 0xFF
    frame[10] = (((channels[6] >> 6) & 0x1F) | ((channels[7] & 0x07FF) << 5)) & 0xFF
    frame[11] = (channels[7] >> 3) & 0xFF
    frame[12] = channels[8] & 0xFF
    frame[13] = (((channels[8] >> 8) & 0x07) | ((channels[9] & 0x07FF) << 3)) & 0xFF
    frame[14] = (((channels[9] >> 5) & 0x3F) | ((channels[10] & 0x07FF) << 6)) & 0xFF
    frame[15] = (channels[10] >> 2) & 0xFF
    frame[16] = (((channels[10] >> 10) & 0x01) | ((channels[11] & 0x07FF) << 1)) & 0xFF
    frame[17] = (((channels[11] >> 7) & 0x0F) | ((channels[12] & 0x07FF) << 4)) & 0xFF
    frame[18] = (((channels[12] >> 4) & 0x7F) | ((channels[13] & 0x07FF) << 7)) & 0xFF
    frame[19] = (channels[13] >> 1) & 0xFF
    frame[20] = (((channels[13] >> 9) & 0x03) | ((channels[14] & 0x07FF) << 2)) & 0xFF
    frame[21] = (((channels[14] >> 6) & 0x1F) | ((channels[15] & 0x07FF) << 5)) & 0xFF
    frame[22] = (channels[15] >> 3) & 0xFF
    frame[23] = 0x00  # Flags
    frame[24] = 0x00  # End byte
    return frame


def send_sbus_packet(serial_port):
    """
    Build a 25-byte SBUS packet from current CHANNEL_VALUES and send it.
    Applies a simple weighted moving average smoothing.
    """
    channels = [1024] * 16
    for i, key in enumerate(channel_order):
        new_value = CHANNEL_VALUES.get(key, 1024)
        if last_transmitted[key] is None:
            smoothed_value = new_value
        else:
            smoothed_value = (SMOOTHING_FACTOR * new_value) + ((1 - SMOOTHING_FACTOR) * last_transmitted[key])
        last_transmitted[key] = smoothed_value
        if invertChannel.get(key, False):
            smoothed_value = 2047 - smoothed_value
        channels[i] = int(round(smoothed_value))
    frame = build_sbus_frame(channels)
    if serial_port is not None and serial_port.is_open:
        try:
            serial_port.write(frame)
        except Exception as e:
            print("Error writing to serial port:", e)

