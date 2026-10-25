"""Native home refresh and local story navigation presentation."""
import time
from economy import currency_packets

WORLD_ICON = '/data/data/com.square_enix.android_googleplay.FFBEWW/files/en/sd/static_banner/home/ffo_world.png'


def packets():
    # RoutineHomeUpdateRespose -> EventBadgeInfo::parseBadgeInfo: records are
    # comma-separated, with name:text:icon:enabled:display:conditions:extra.
    badge = ':'.join(('HOME_MAINMENU_WORLD_ICON', 'World', WORLD_ICON, '1', '1', '', ''))
    return {**currency_packets(), 'xS3CA5LN': [{
        '0Zpuzj7E': str(int(time.time()) + 300),
        'Ei5Kx2Bb': '0', 'merqbE18': badge}]}
