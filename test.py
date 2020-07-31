import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap

plt.figure(figsize=(20, 20))
m = Basemap(projection='lcc', resolution="c",
            width=1E6, height=1E6, 
            lat_0=37.5267800, lon_0=15.0744050)
m.etopo(scale=0.5, alpha=0.5)
x, y = m(15.0744050, 37.5267800, inverse = False)
plt.plot(x, y, 'ok', markersize=5)
#plt.text(x, y, ' CT', fontsize=12)
plt.show()