#!/usr/bin/env python3
"""Dark archival-style route maps (needs: pip install basemap matplotlib).

    python tools/maps.py <out_dir>

Writes map_atlantic.png, map_belgium.png and map_stlawrence.png for the Crippen case.
Coordinates are approximate and only for orientation on screen.
"""
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap

SEA, LAND, COAST, INK, DIM, RED, BLUE = "#100f0d", "#2b2722", "#7a6d5c", "#ece4d4", "#9a8f7d", "#c0453a", "#d9c9a3"
SERIF = {"family": "serif", "color": INK}
PLACES = {"London": (51.51, -0.13), "Liverpool": (53.41, -2.99), "Antwerp": (51.22, 4.40),
          "Brussels": (50.85, 4.35), "Quebec": (46.81, -71.21), "Father Point": (48.52, -68.47),
          "Harwich": (51.94, 1.28),
          # hidden waypoints so routes stay at sea (approximate)
          "_channel": (50.9, 1.4), "_lizard": (49.7, -6.0), "_malin": (55.6, -7.8),
          "_belleisle": (51.6, -55.8), "_anticosti": (49.75, -64.6)}

def path(m, names, color, style="-", lw=2.4):
    for a, b in zip(names, names[1:]):
        route(m, a, b, color, style=style, lw=lw)


def base(ax, **kw):
    m = Basemap(ax=ax, resolution=kw.pop("res", "l"), fix_aspect=False, **kw)
    m.drawmapboundary(fill_color=SEA, linewidth=0)
    m.fillcontinents(color=LAND, lake_color=SEA)
    m.drawcoastlines(color=COAST, linewidth=0.6)
    m.drawparallels(range(0, 90, 10), color="#2a2723", linewidth=0.4, dashes=[2, 4])
    m.drawmeridians(range(-180, 180, 10), color="#2a2723", linewidth=0.4, dashes=[2, 4])
    return m


def place(m, ax, name, dx=0.4, dy=0.4, size=15, ha="left"):
    lat, lon = PLACES[name]
    x, y = m(lon, lat)
    ax.plot(x, y, "o", color=INK, ms=6, zorder=5)
    x2, y2 = m(lon + dx, lat + dy)
    ax.text(x2, y2, name, fontsize=size, ha=ha, zorder=6, **SERIF)


def route(m, a, b, color, label=None, style="-", lw=2.4):
    (la1, lo1), (la2, lo2) = PLACES[a], PLACES[b]
    import numpy as np
    def v(la, lo):
        la, lo = np.radians(la), np.radians(lo)
        return np.array([np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)])
    p, q = v(la1, lo1), v(la2, lo2)
    w = np.arccos(np.clip(p @ q, -1, 1))
    ts = np.linspace(0, 1, 100)
    pts = [(np.sin((1 - t) * w) * p + np.sin(t * w) * q) / np.sin(w) if w else p for t in ts]
    lats = [np.degrees(np.arcsin(c[2])) for c in pts]
    lons = [np.degrees(np.arctan2(c[1], c[0])) for c in pts]
    x, y = m(lons, lats)
    m.ax.plot(x, y, color=color, linewidth=lw, linestyle=style, zorder=4)


def fig():
    f = plt.figure(figsize=(19.2, 10.8), dpi=100, facecolor=SEA)
    ax = f.add_axes([0, 0, 1, 1])
    return f, ax


def save(f, path):
    f.savefig(path, facecolor=SEA)
    plt.close(f)


def atlantic(out):
    f, ax = fig()
    m = base(ax, projection="merc", llcrnrlat=36, urcrnrlat=62, llcrnrlon=-78, urcrnrlon=12)
    path(m, ["Antwerp", "_channel", "_lizard", "_belleisle", "_anticosti", "Father Point"], RED)
    path(m, ["Liverpool", "_malin", "_belleisle", "_anticosti", "Father Point", "Quebec"], BLUE, style="--")
    for n, dx, dy, ha in [("London", 0.6, -1.4, "left"), ("Liverpool", -0.6, 0.6, "right"),
                          ("Antwerp", 0.6, -0.9, "left"), ("Quebec", 0.6, -1.3, "left"),
                          ("Father Point", 0.6, 0.6, "left")]:
        place(m, ax, n, dx, dy, ha=ha)
    x, y = m(-38, 47.6); ax.text(x, y, "SS Montrose", fontsize=20, color=RED, family="serif", style="italic")
    x, y = m(-38, 57.2); ax.text(x, y, "SS Laurentic", fontsize=20, color=BLUE, family="serif", style="italic")
    x, y = m(-74, 38); ax.text(x, y, "NORTH ATLANTIC  ·  JULY 1910", fontsize=22, color=DIM, family="serif")
    save(f, out)


def belgium(out):
    f, ax = fig()
    m = base(ax, res="i", projection="merc", llcrnrlat=49.6, urcrnrlat=53.4, llcrnrlon=-3.0, urcrnrlon=7.2)
    route(m, "London", "Harwich", RED, style="--")
    route(m, "Harwich", "Brussels", RED, style="--")
    route(m, "Brussels", "Antwerp", RED)
    place(m, ax, "London", -0.15, 0.12, size=22, ha="right")
    place(m, ax, "Brussels", 0.15, -0.25, size=22)
    place(m, ax, "Antwerp", 0.15, 0.12, size=22)
    x, y = m(-2.7, 49.8); ax.text(x, y, "JULY 1910  ·  route approximate", fontsize=20, color=DIM, family="serif")
    save(f, out)


def stlawrence(out):
    f, ax = fig()
    m = base(ax, res="i", projection="merc", llcrnrlat=45.6, urcrnrlat=51.2, llcrnrlon=-73.5, urcrnrlon=-58.0)
    route(m, "_anticosti", "Father Point", RED)
    route(m, "Father Point", "Quebec", BLUE, style="--")
    place(m, ax, "Quebec", 0.2, -0.45, size=22)
    place(m, ax, "Father Point", 0.25, 0.2, size=22)
    x, y = m(-63.2, 48.3); ax.text(x, y, "Gulf of St Lawrence", fontsize=20, color=DIM, family="serif", style="italic")
    save(f, out)


if __name__ == "__main__":
    d = sys.argv[1]
    atlantic(f"{d}/map_atlantic.png"); belgium(f"{d}/map_belgium.png"); stlawrence(f"{d}/map_stlawrence.png")
