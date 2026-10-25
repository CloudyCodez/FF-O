"""Rate disclosure generated from the same uniform pools used by summons."""
from collections import Counter
from html import escape
from banners import entry_packets
from summons import summon_pool
from units import masters

def page(banner_id):
    banner=next((r for r in entry_packets()['PcUrGH13'] if r['X1IuZnj2']==str(banner_id)),None)
    if banner is None:raise ValueError('Unknown banner')
    pool=summon_pool(banner_id);total=len(pool)
    def label(unit):
        return 'Neo Vision' if unit.get('5Mgpv8hJ') in ('1','2') else unit['9fW0TePj']+' star'
    counts=Counter(label(masters()[i]) for i in pool)
    rows=''.join(f'<tr><td>{escape(k)}</td><td>{v}</td><td>{v*100/total:.6f}%</td></tr>' for k,v in sorted(counts.items()))
    units=''.join(f'<tr><td>{i}</td><td>{escape(label(masters()[i]))}</td><td>{100/total:.8f}%</td></tr>' for i in sorted(pool))
    return (f'<!doctype html><meta name="viewport" content="width=device-width,initial-scale=1"><style>body{{background:#102448;color:#fff;font:16px sans-serif;padding:16px}}table{{width:100%;border-collapse:collapse}}td,th{{padding:8px;text-align:left;border-bottom:1px solid #53627b}}h1{{font-size:22px;color:#e9d49c}}</style>'
            f'<h1>{escape(banner["G4L0YIB2"])}</h1><p>{total} eligible units. Each draw independently selects one unit with equal probability. Single and ten summons use the same rates; no guaranteed slot or historical rate-up is active. Percentages are rounded for display.</p>'
            f'<table><tr><th>Rarity</th><th>Units</th><th>Total rate</th></tr>{rows}</table><h2>Individual units</h2><p>Native unit IDs identify the exact forms in this pool.</p><table><tr><th>Unit ID</th><th>Rarity</th><th>Per draw</th></tr>{units}</table>').encode()
