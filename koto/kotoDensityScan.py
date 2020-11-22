from sklearn.cluster import DBSCAN
import numpy as np

class density_cluster:

    def __init__(self, data, lat = "Lat", lon = "Lon"):
        self.data = data
        self.lat = lat
        self.lon = lon


    def fence_data(self,tl = [40.250580, -83.247525], tr = [40.251652, -82.671814], bl = [39.821981, -83.352838], br = [39.804789, -82.633243]):
        self.data = self.data[(self.data[self.lat] < tl[0]) & (self.data[self.lat] > bl[0])]
        self.data = self.data[(self.data[self.lon] > tl[1]) & (self.data[self.lon] < tr[1])]


    def dbscan(self, neighborhood_dist:float=0.1, min_mass:int=15, metric="haversine"):
        kms_per_radian = 6371.0088
        epsilon = neighborhood_dist / kms_per_radian
        db = DBSCAN(eps=epsilon, min_samples=min_mass, metric=metric)
        db.fit(np.radians(self.data[[self.lat,self.lon]]))
        self.data["cluster_labels"] = db.labels_
        return self.data

    # TODO: Implement similar for OPTIC and SPECTRAL