import json
from common.rts_settings import RTSConfigurationLayout, RTSLayout, RTSImages, RTSOverlaySettings, RTSBuildOrderLayout, \
    RTSBuildOrderInputLayout


class SC2BuildOrderInputLayout(RTSBuildOrderInputLayout):
    """Settings for the SC2 panel to input a new build order"""

    def __init__(self):
        """Constructor"""
        super().__init__()
        self.lines_per_step: int = 4  # default number of lines per step


class SC2ConfigurationLayout(RTSConfigurationLayout):
    """Settings for the SC2 configuration layout"""

    def __init__(self):
        """Constructor"""
        super().__init__()
        self.icon_select_size: list = [32, 32]  # size of the icon for race selection


class SC2BuildOrderLayout(RTSBuildOrderLayout):
    """Settings for the RTS build order layout"""

    def __init__(self):
        """Constructor"""
        super().__init__()
        self.image_height: int = 35  # height of the build order images
        self.supply_image_height: int = 25  # height of the supply image
        self.time_image_height: int = 25  # height of the time image


class SC2Layout(RTSLayout):
    """Settings for the SC2 layout"""

    def __init__(self):
        """Constructor"""
        super().__init__()
        self.configuration: SC2ConfigurationLayout = SC2ConfigurationLayout()  # configuration layout
        self.build_order: SC2BuildOrderLayout = SC2BuildOrderLayout()  # build order layout


class SC2Images(RTSImages):
    """Settings for the SC2 images"""

    def __init__(self):
        """Constructor"""
        super().__init__()
        self.supply: str = 'icon/house.png'  # image to use for supply


class SC2OverlaySettings(RTSOverlaySettings):
    """Settings for the SC2 overlay"""

    def __init__(self):
        """Constructor"""
        super().__init__()

        self.panel_build_order = SC2BuildOrderInputLayout()  # panel to input a build order

        self.title: str = 'SC2 Overlay'  # application title

        # layout
        self.layout = SC2Layout()

        # images
        self.images = SC2Images()


if __name__ == '__main__':
    sc2_settings_name = 'sc2_settings.json'

    settings_1 = SC2OverlaySettings()
    with open(sc2_settings_name, 'w') as f:
        f.write(json.dumps(settings_1.to_dict(), sort_keys=False, indent=4))

    settings_2 = SC2OverlaySettings()
    with open(sc2_settings_name, 'rb') as f:
        dict_data = json.load(f)
        settings_2.from_dict(dict_data)
