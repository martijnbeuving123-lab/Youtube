#!/usr/bin/env python3
"""Maps for the Brides in the Bath video (England and Wales). Coordinates approximate.
    <venv with basemap>/bin/python videos/brides-in-the-bath/make_maps.py videos/brides-in-the-bath/assets/cards
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../tools"))
import maps as M

M.PLACES.update({"London": (51.51, -0.13), "Herne Bay": (51.37, 1.13), "Blackpool": (53.82, -3.05),
    "Weymouth": (50.61, -2.46), "Weston-super-Mare": (51.35, -2.98), "Bath": (51.38, -2.36),
    "Bristol": (51.45, -2.59), "Portsmouth": (50.80, -1.09), "Leicester": (52.64, -1.13),
    "Worthing": (50.81, -0.37), "Maidstone": (51.27, 0.52), "Highgate": (51.57, -0.15)})
POS = {"London": (0.15, 0.15, "left"), "Herne Bay": (0.12, 0.12, "left"), "Blackpool": (0.15, 0.1, "left"),
       "Weymouth": (-0.12, -0.25, "right"), "Weston-super-Mare": (-0.15, 0.1, "right"), "Bath": (0.12, -0.2, "left"),
       "Bristol": (-0.12, 0.12, "right"), "Portsmouth": (0.1, -0.25, "left"), "Leicester": (0.15, 0.1, "left"),
       "Worthing": (0.1, -0.25, "left"), "Maidstone": (0.12, -0.25, "left"), "Highgate": (0.15, 0.1, "left")}

def england(out, names, foot, hi=None, box=(49.8, 55.2, -6.2, 2.2)):
    f, ax = M.fig()
    m = M.base(ax, res="i", projection="merc", llcrnrlat=box[0], urcrnrlat=box[1], llcrnrlon=box[2], urcrnrlon=box[3])
    for n in names:
        lat, lon = M.PLACES[n]; x, y = m(lon, lat)
        big = n in (hi or [])
        ax.plot(x, y, "o", color=M.RED if big else M.INK, ms=13 if big else 7, zorder=5)
        dx, dy, ha = POS[n]; x2, y2 = m(lon + dx, lat + dy)
        ax.text(x2, y2, n, fontsize=30 if big else 20, ha=ha, zorder=6, color=M.RED if big else M.INK, family="serif")
    x, y = m(box[2] + 0.3, box[0] + 0.25); ax.text(x, y, foot, fontsize=22, color=M.DIM, family="serif")
    M.save(f, out)

d = sys.argv[1]
england(f"{d}/map_early.png", ["Leicester", "London", "Worthing", "Bristol"], "1896-1909  ·  LEICESTER, LONDON, WORTHING, BRISTOL")
england(f"{d}/map_weymouth.png", ["Weymouth", "Weston-super-Mare", "Bristol", "London"], "1910  ·  WEYMOUTH", hi=["Weymouth"])
england(f"{d}/map_weston.png", ["Weymouth", "Weston-super-Mare", "Bristol", "London"], "1912  ·  WESTON-SUPER-MARE", hi=["Weston-super-Mare"])
england(f"{d}/map_hernebay.png", ["Herne Bay", "London", "Maidstone"], "JULY 1912  ·  HERNE BAY, KENT", hi=["Herne Bay"])
england(f"{d}/map_blackpool.png", ["Blackpool", "Portsmouth", "London", "Herne Bay"], "DECEMBER 1913  ·  BLACKPOOL", hi=["Blackpool"])
england(f"{d}/map_highgate.png", ["Bath", "Highgate", "Blackpool", "Herne Bay"], "DECEMBER 1914  ·  BATH TO HIGHGATE", hi=["Bath", "Highgate"])
england(f"{d}/map_three.png", ["Herne Bay", "Blackpool", "Highgate"], "THREE TOWNS  ·  1912-1914", hi=["Herne Bay", "Blackpool", "Highgate"])
