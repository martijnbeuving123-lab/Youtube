"""Maps for the Duquesne Spy Ring video (approximate, for orientation only)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../tools"))
import maps as M
M.PLACES.update({"Mülheim": (51.43, 6.88), "Hamburg": (53.55, 9.99), "Cologne": (50.94, 6.96),
  "Genoa": (44.41, 8.93), "New York": (40.71, -74.0), "Lisbon": (38.72, -9.14),
  "Freetown": (8.48, -13.23), "_gib": (36.0, -6.5), "_azores": (38.5, -28.0),
  "Robin Moor sunk": (6.5, -24.0), "Manhattan": (40.76, -73.98), "Brooklyn": (40.69, -73.99),
  "Long Island": (40.9, -73.35)})
out = sys.argv[1]
# 1. Sebold's journey
f, ax = M.fig()
m = M.base(ax, projection="merc", llcrnrlat=30, urcrnrlat=60, llcrnrlon=-80, urcrnrlon=20)
M.path(m, ["Hamburg", "Mülheim", "Cologne"], M.BLUE, style="--")
M.path(m, ["Cologne", "Genoa"], M.BLUE, style="--")
M.path(m, ["Genoa", "_gib", "_azores", "New York"], M.RED)
for n, dx, dy, ha in [("Hamburg", 0.8, 0.5, "left"), ("Mülheim", -0.8, 0.2, "right"), ("Cologne", 0.8, -1.2, "left"),
                      ("Genoa", 0.8, -1.2, "left"), ("New York", 0.8, -1.4, "left")]:
    M.place(m, ax, n, dx, dy, size=20, ha=ha)
x, y = m(-60, 33); ax.text(x, y, "SEBOLD · 1939–FEBRUARY 8, 1940 · route approximate", fontsize=20, color=M.DIM, family="serif")
M.save(f, f"{out}/map_sebold.png")
# 2. Atlantic: courier route and the Robin Moor
f, ax = M.fig()
m = M.base(ax, projection="merc", llcrnrlat=-2, urcrnrlat=50, llcrnrlon=-80, urcrnrlon=5)
M.route(m, "New York", "Lisbon", M.BLUE, style="--")
M.place(m, ax, "New York", 0.8, -2.2, size=20); M.place(m, ax, "Lisbon", 0.8, 0.8, size=20)
M.place(m, ax, "Freetown", 0.8, -2.0, size=20)
lat, lon = M.PLACES["Robin Moor sunk"]; x, y = m(lon, lat)
ax.plot(x, y, "x", color=M.RED, ms=22, mew=4, zorder=6)
x, y = m(lon - 1, lat + 2); ax.text(x, y, "SS Robin Moor, sunk May 21, 1941", fontsize=22, color=M.RED, family="serif", ha="right")
x, y = m(-50, 36.5); ax.text(x, y, "courier route New York – Lisbon", fontsize=20, color=M.BLUE, family="serif", style="italic")
x, y = m(-78, 0); ax.text(x, y, "NORTH ATLANTIC · 1940–1941 · positions approximate", fontsize=20, color=M.DIM, family="serif")
M.save(f, f"{out}/map_atlantic.png")
# 3. New York
f, ax = M.fig()
m = M.base(ax, res="i", projection="merc", llcrnrlat=40.45, urcrnrlat=41.15, llcrnrlon=-74.3, urcrnrlon=-72.9)
M.place(m, ax, "Manhattan", -0.03, 0.03, size=22, ha="right")
M.place(m, ax, "Brooklyn", 0.03, -0.06, size=22)
M.place(m, ax, "Long Island", 0.03, 0.03, size=22)
x, y = m(-74.28, 41.08); ax.text(x, y, "office near Times Square · trial in Brooklyn · FBI radio on Long Island", fontsize=20, color=M.DIM, family="serif")
M.save(f, f"{out}/map_newyork.png")
