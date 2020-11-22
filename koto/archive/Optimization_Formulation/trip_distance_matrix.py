import googlemaps

def distance_calc(origin_lat, origin_long, dest_lat, dest_long, mode = 'driving'):
    gmaps = googlemaps.Client(key='AIzaSyDclNSgG3YvJFNvd0aPjKc2rNBIg5U5Jy0') #TODO replace by reading from config
    distance = gmaps.distance_matrix([str(origin_lat) + " " + str(origin_long)], [str(dest_lat) + " " + str(dest_long)], mode=mode)['rows'][0]['elements'][0]
    return distance['distance']['value']