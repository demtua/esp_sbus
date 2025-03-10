#!/usr/bin/env python3
import serial
import serial.tools.list_ports
import struct


from kivy.app import App
from kivy.clock import Clock
from gui_components import *
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, NumericProperty, ObjectProperty
from channel_data import *





class MainScreen(BoxLayout):
    port_spinner = ObjectProperty(None)
    baud_rate_input = ObjectProperty(None)
    heading_label = ObjectProperty(None)
    channels_box = ObjectProperty(None)

    def on_kv_post(self, base_widget):
        """
        This method is called after the KV file has been loaded,
        ensuring that all ids (like channels_box) are available.
        """
        # Dynamically add ChannelWidgets for each channel.
        ibuttons =  ["arm", "mode", "altitude_hold"]
        for key in CHANNEL_VALUES.keys():
            if key not in ibuttons:
                cw = ChannelWidget(channel_name=key, value=CHANNEL_VALUES[key], offset=0)
                self.ids.channels_box.add_widget(cw)
        # Schedule periodic tasks.
        Clock.schedule_interval(self.send_packet, 0.02)
        Clock.schedule_interval(self.read_flight_data, 0.01)

    def send_packet(self, dt):
        send_sbus_packet(self.lora_serial)

    def scan_ports(self):
        ports = serial.tools.list_ports.comports()
        port_list = [port.device for port in ports]
        self.port_spinner.values = port_list
        if port_list:
            self.port_spinner.text = port_list[0]
        print("Available ports:", port_list)

    def connect_serial(self):
        selected_port = self.port_spinner.text
        try:
            baud_rate = int(self.baud_rate_input.text)
        except ValueError:
            print("Invalid baud rate")
            return
        try:
            self.lora_serial = serial.Serial(selected_port, baud_rate, timeout=1)
            print(f"Connected to {selected_port} at {baud_rate} bps")
        except Exception as e:
            print("Error connecting:", e)

    def increase_throttle(self, value):
        CHANNEL_VALUES['throttle'] = min(CHANNEL_VALUES['throttle'] + value, 2053)
        print(f"Throttle increased: {CHANNEL_VALUES['throttle']}")
        # Update the throttle widget.
        for cw in self.channels_box.children:
            if cw.channel_name == 'throttle':
                cw.value = CHANNEL_VALUES['throttle']
                break

    def read_flight_data(self, dt):
        if self.lora_serial is None or not self.lora_serial.is_open:
            return
        try:
            bytes_available = self.lora_serial.in_waiting
            if bytes_available:
                data = self.lora_serial.read(bytes_available)
                self.flight_data_buffer.extend(data)
            MESSAGE_SIZE = 22
            while len(self.flight_data_buffer) >= MESSAGE_SIZE:
                message_bytes = self.flight_data_buffer[:MESSAGE_SIZE]
                self.flight_data_buffer = self.flight_data_buffer[MESSAGE_SIZE:]
                try:
                    if message_bytes[0] == 0x02:
                        # GPS message.
                        lat, lon, alt = struct.unpack("<iii", message_bytes[1:13])
                        lat_deg = lat / 1e7
                        lon_deg = lon / 1e7
                        alt_m = alt / 1000.0
                        print(f"GPS: {lat_deg:.7f}, {lon_deg:.7f}, Alt: {alt_m:.2f} m")
                    else:
                        # HUD message.
                        airspeed, groundspeed, heading, throttle, altitude, climb = struct.unpack("<ffHfff", message_bytes)
                        self.heading_label.text = (
                            f"Heading: {heading}°  Throttle: {throttle:.1f}%, "
                            f"Alt: {altitude:.1f} m, GS: {groundspeed:.1f} m/s"
                        )
                        print(f"HUD: Airspeed: {airspeed:.2f}, Groundspeed: {groundspeed:.2f}, Altitude: {altitude:.2f}")
                except struct.error as e:
                    print("Error unpacking message:", e)
        except Exception as e:
            print("Error reading flight data:", e)


class SBusApp(App):
    def build(self):
        # The KV file (SBusApp.kv) is auto-loaded based on the class name.
        main_screen = MainScreen()
        # Initialize serial connection variables.
        main_screen.lora_serial = None
        main_screen.flight_data_buffer = bytearray()
        return main_screen


if __name__ == '__main__':
    SBusApp().run()
