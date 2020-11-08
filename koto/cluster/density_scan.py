import pandas as pd
from sklearn.cluster import DBSCAN
import json

##Something Something Make into Dataframe

tl = [40.250580, -83.247525]
tr = [40.251652, -82.671814]
bl = [39.821981, -83.352838]
br = [39.804789, -82.633243]

data_ws = data[["Lat","Lon"]]
data_ws = data_ws[(data_ws["Lat"] < tl[0]) & (data_ws["Lat"] > bl[0])]
data_ws = data_ws[(data_ws["Lon"] > tl[1]) & (data_ws["Lon"] < tr[1])]


db = DBSCAN(eps=0.0011, min_samples=15)

mod = db.fit(data_ws)

data_ws["cluster_labels"] = db.labels_