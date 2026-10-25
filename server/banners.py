"""Small, explicit local banner catalog for the recovered 9.1.0 client."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COLLAB_BANNER_ID = 900003  # ID 3 is reserved by native TUTORIAL_GACHA_ID.


def entry_packets():
    # These four response groups are registered by the native response factory.
    # The client filters schedules against its current clock before showing them.
    banners = []
    details = []
    schedules = []
    users = []
    for ident, name, category in ((1, 'FF:O Premium Summon', 3),
                                  (COLLAB_BANNER_ID, 'FF:O Collaboration Summon', 3),
                                  (2, 'FF:O Standard Summon', 0)):
        key = str(ident)
        # Modern native detail cards are 640x190. Historical step-up cards
        # (640x392) squash here and also advertise unimplemented bonuses.
        theme={1:'rare',2:'standard',COLLAB_BANNER_ID:'collab'}[ident]
        image = f'ffo_{theme}_v1.png'
        sub_images = sorted((ROOT/'assets/cache/en/sd/static_banner/gacha/sub').glob(image[:-4] + '_*.png'))
        banner_info = ','.join([image] + [f'{index}:{path.name}'
                               for index, path in enumerate(sub_images, 1)])
        banners.append({'X1IuZnj2': key, 'G4L0YIB2': name,
                        'g38Pjk10': 'gacha_animation',
                        'JDFMe3A7': 'mog_rare/anime',
                        '7xBNR2MH': '1',
                        '5hjAJzC0': '1', 'sx4kyW0i': str(category),
                        '8s9wNSpd': '1', '2RtVPS3b': '1'})
        for amount in (1, 10):
            detail_id = str(ident * 10 + amount)
            details.append({'X1IuZnj2': key,
                            'nqzG3b2v': detail_id,
                            'G4L0YIB2': name,
                            't6aQ1voV': '1:313000205' if ident == COLLAB_BANNER_ID else '1:213000105',
                            'XFLm4Mx6': f'gacha_btns_gold_{amount}',
                            'iKJp3am4': '0',
                            'ijEey5f7': '1' if amount == 1 else '2',
                            '0GgK6ytT': f'50:1:1:{amount}:0',
                            # The native availability check parses two integers
                            # from this field before it considers a banner active.
                            '1ovyP04j': '999999:0'})
            users.append({'X1IuZnj2': key, 'nqzG3b2v': detail_id,
                          '08MuyfqD': '0', 'L4QmV0Nz': '0'})
        schedules.append({'X1IuZnj2': key,
                          # Native getters: +0x28 is display order; +0x2c is
                          # banner type. Type 1 uses these normal main images.
                          'Z0EN6jSh': str({1:2,COLLAB_BANNER_ID:1,2:0}[ident]),
                          'w2A76noc': '1',
                          '4yT7FUqj': banner_info,
                          'VjJQ51uG': '2020-01-01 00:00:00',
                          'm8ivD4NX': '2035-01-01 00:00:00'})
    return {'PFGNauNg': [], 'PcUrGH13': banners, 'IC0ueV5s': details,
            '4D5k8dpI': schedules, '80nGg32w': users}
