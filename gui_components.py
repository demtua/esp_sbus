
from kivy.uix.togglebutton import ToggleButton
from channel_data import CHANNEL_VALUES
from kivy.properties import StringProperty, NumericProperty, ObjectProperty
from kivy.uix.boxlayout import BoxLayout




class ArmButton(ToggleButton):

    channel_name = 'arm'

    def toggle_state(self, instance):
        if instance.state == 'down':
            CHANNEL_VALUES[self.channel_name] = 1749
            instance.text = "Armed"
            print(CHANNEL_VALUES[self.channel_name])
        else:
            CHANNEL_VALUES[self.channel_name] = 192
            instance.text = "Disarmed"  
            print(CHANNEL_VALUES[self.channel_name])


class ModeButton(ToggleButton):

    channel_name = 'mode'

    def toggle_mode(self, instance):
        if instance.state == 'down':
            CHANNEL_VALUES[self.channel_name] = 1800
            instance.text = "Horizon"
        else:
            CHANNEL_VALUES[self.channel_name] = 100
            instance.text = "Angle"



class AltitudeButton(ToggleButton):
    channel_name = 'altitude_hold'

    on_value = 500
    off_value = 1500

    def toggle_altitude_hold(self, instance):
        if instance.state == 'down':
            CHANNEL_VALUES[self.channel_name] = self.on_value
            instance.text = "Altitude Hold ON"
            print(CHANNEL_VALUES[self.channel_name])
        else:
            CHANNEL_VALUES[self.channel_name] = self.off_value
            instance.text = "Altitude Hold OFF"



class ChannelWidget(BoxLayout):
    channel_name = StringProperty("")
    value = NumericProperty(0)
    offset = NumericProperty(0)

    def on_slider_value(self, new_value):
        self.value = int(new_value)
        CHANNEL_VALUES[self.channel_name] = self.value

    def on_offset_text(self, text):
        try:
            self.offset = float(text)
        except ValueError:
            self.offset = 0

    

    # def toggle_mode(self, instance):
    #     if instance.state == 'down':
    #         CHANNEL_VALUES[self.channel_name] = 1800
    #         instance.text = "Horizon"
    #     else:
    #         CHANNEL_VALUES[self.channel_name] = 100
    #         instance.text = "Angle"

    # def toggle_altitude_hold(self, instance):
    #     if instance.state == 'down':
    #         CHANNEL_VALUES[self.channel_name] = 500
    #         instance.text = "Altitude Hold ON"
    #     else:
    #         CHANNEL_VALUES[self.channel_name] = 1500
    #         instance.text = "Altitude Hold OFF"
