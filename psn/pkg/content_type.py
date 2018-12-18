from aenum import MultiValueEnum


class ContentType(MultiValueEnum):
    UNKNOWN = 0x01
    EMPTY = 0x02, 0x03, 0x08, 0x13
    GAME_DATA = 0x04
    GAME_EXEC = 0x05
    PS1_EMU = 0x06
    PSP_PC_ENGINE = 0x07
    THEME = 0x09
    WIDGET = 0x0A
    LICENSE = 0x0B
    VSH_MODULE = 0x0C
    PSN_AVATAR = 0x0D
    PSP_GO = 0x0E
    MINIS = 0x0F
    NEOGEO = 0x10
    VMC = 0x11
    PS2_CLASSIC = 0x12
    PSP_REMASTERED = 0x14
    PSP2GD = 0x15
    PSP2AC = 0x16
    PSP2LA = 0x17
    PSM = 0x18, 0x1D
    WT = 0x19
    PSP2_THEME = 0x1F

    @property
    def install_path(self) -> str:
        if self in [ContentType.UNKNOWN, ContentType.GAME_DATA, ContentType.GAME_EXEC, ContentType.PS1_EMU,
                    ContentType.PSP_PC_ENGINE, ContentType.PSP_GO, ContentType.MINIS, ContentType.NEOGEO,
                    ContentType.PS2_CLASSIC, ContentType.PSP_REMASTERED, ContentType.WT]:
            return "/dev_hdd0/game/"
        elif self == ContentType.THEME:
            return "/dev_hdd0/theme"
        elif self == ContentType.WIDGET:
            return "/dev_hdd0/widget"
        elif self == ContentType.LICENSE:
            return "/dev_hdd0/home/<current user>/exdata"
        elif self == ContentType.VSH_MODULE:
            return "/dev_hdd0/vsh/modules/"
        elif self == ContentType.PSN_AVATAR:
            return "/dev_hdd0/home/<current user>/psn_avatar"
        elif self == ContentType.VMC:
            return "/dev_hdd0/tmp/vmc/"
        else:
            return ""
