import googlemaps
import numpy as np


class distance_matrix:

    def __init__(self, api_key:str='google_api_key'):
        self.client = googlemaps.Client(key=api_key)

    def _distance_calc(self, origins:list, destinations:list, mode:str = 'driving'):
        """
        Objective:
            Pass origin latitude, origin longitude as tuple within a list, and list of tuple destinations
            and get back json object containing driving distances from the origin to each destination
        
        Parameters:
            :origins(list):
                list containing just one element that is the origin as a tuple, first element is
                lat second element is long
            :destinations(list):
                list containing tuples of destinations
            :mode(str):'driving'
                The distance mode passed to the google distance matrix api, other options could be, walking, bus
        
        Returns:
            :rtype: dictionary
            :rvalue: partially unpacked dictionary containing the distances

        Note:
            This function is encapsulated so mode can't change.

        """

        distance = self.client.distance_matrix(origins=origins, destinations=destinations, mode=mode)
        distance = distance['rows'][0]['elements']
        return distance

    def create_dist_matrix(self, dataframe):
        """
        Objective:
            Create empty matix, and create a list of tuples of all coordinates from the supplied dataframe.
            Columns names must match exactly. Call the distance calc column and ouput an adjacency matrix of
            driving distances
        
        Parameters:
            :dataframe:
                This must be a Pandas dataframe object, with the cluster label column as "Cluster Label"
                and the latitude column as a float type with the name "Lat", and the longitude column as a float
                type with the name "Lon"
      
        Returns:
            :rtype: numpy array
            :rvalue: adjacency matrix of distance as specified by the mode

        """
        #TODO: Add assertion that the necessary columns are in the supplied dataframe
        #TODO: Add assertion that the supplied argument for dataframe is a pandas dataframe

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
                dist_list_1 = self._distance_calc(origins=location_i, destinations=destination_list_1)
                for j, enum in zip(destination_list_1_index, enumerate(dist_list_1)):
                    dist_value = dist_list_1[enum[0]]['distance']['value']
                    mat[label_i, j] = dist_value

            if len(destination_list_2) > 0:
                dist_list_2 = self._distance_calc(origins=location_i, destinations=destination_list_2)
                for j, enum in zip(destination_list_2_index, enumerate(dist_list_2)):
                    dist_value = dist_list_2[enum[0]]['distance']['value']
                    mat[label_i, j] = dist_value
        return mat