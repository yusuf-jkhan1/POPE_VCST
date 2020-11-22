import googlemaps
import numpy as np


class distance_matrix:

    def __init__(self, api_key:str='google_api_key'):
        self.client = googlemaps.Client(key=api_key)

    def distance_calc(self, origins, destinations, mode = 'driving'):
        #gmaps = googlemaps.Client(key='AIzaSyBTfErYq2hwDnJvrGKVPtQud56vUlbx0VA')
        #gmaps = googlemaps.Client(key='AIzaSyDclNSgG3YvJFNvd0aPjKc2rNBIg5u5Jy0')
        distance = self.client.distance_matrix(origins=origins, destinations=destinations, mode=mode)
        distance = distance['rows'][0]['elements']
        return distance

    def create_dist_matrix(self, dataframe):

        n_clusters = dataframe['Cluster Label'].nunique()
        mat = np.empty(shape = (n_clusters,n_clusters))
        locations_list = [(lat,lon) for lat,lon in zip(dataframe['Lat'],dataframe['Lon'])]

        for index, row in dataframe.iterrows():

            label_i = int(row['Cluster Label'])
            location_i = locations_list[index]

            destination_list_1_index = [x for x in range(0,26) if x > label_i]
            destination_list_2_index = [x for x in range(26,50) if x > label_i]
            destination_list_1 = [locations_list[i] for i in destination_list_1_index]
            destination_list_2 = [locations_list[i] for i in destination_list_2_index]

            if len(destination_list_1) > 0:
                dist_list_1 = self.distance_calc(origins=location_i, destinations=destination_list_1)
                for j, enum in zip(destination_list_1_index, enumerate(dist_list_1)):
                    dist_value = dist_list_1[enum[0]]['distance']['value']
                    mat[label_i, j] = dist_value

            if len(destination_list_2) > 0:
                dist_list_2 = self.distance_calc(origins=location_i, destinations=destination_list_2)
                for j, enum in zip(destination_list_2_index, enumerate(dist_list_2)):
                    dist_value = dist_list_2[enum[0]]['distance']['value']
                    mat[label_i, j] = dist_value
        return mat