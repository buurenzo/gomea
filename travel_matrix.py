import requests
import numpy as np
import osmnx
import networkx


'''
contains functions to generate travel time matrices from
longitude and latitude coordinates input with the use of API's
based on two possible websites
1) https://openrouteservice.org/
2) (http://project-osrm.org/)

main function is travel_matrix
'''

# splits list in batches of size 50 one batch with remaining elements
# def get_batches(locations,batchsize=1):
#    batches = []
#    size = len(locations)
#    idx = [i for i in range(size)]
#    div = divmod(size,batchsize)
#    q = div[0]
#    r = div[1]
#    for i in range(q):
#        batches.append(idx[i*batchsize:(i+1)*batchsize])
#    if r > 0:
#        batches.append(idx[-r::])
#    return batches
#
# def glue_matrices(matrices):
#    size = len(matrices)
#    glued_matrix = np.array(matrices[0])
#    for i in range(1,size):
#        matrix = np.array(matrices[i])
#        glued_matrix = np.hstack((glued_matrix,matrix))
#    return glued_matrix

# implementation of open route service API (up to 50x50 requests at the time) (https://openrouteservice.org/)
# returns travel time matrix in minutes between location elements [longitude,latitude] in locations list
# def travel_matrix(locations):
#    batchsize = max(int(np.floor(2500/len(locations))),len(locations))
#    idx_chunks = get_batches(locations,batchsize)
#    nchunks = len(idx_chunks)
#    matrices = [[] for i in range(nchunks)]
#    for i in range(nchunks):
#        #API request
#        destinations = idx_chunks[i]
#        body = {"locations":locations,
#                "destinations":destinations, #default is set to all
#                "metrics":["duration"]}
#
#        headers = {
#            'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8',
#            'Authorization': '5b3ce3597851110001cf6248e69a51e29ad649fc83086b9c4b89acf9',
#            'Content-Type': 'application/json; charset=utf-8'
#        }
#        call = requests.post('https://api.openrouteservice.org/v2/matrix/driving-car', json=body, headers=headers)
#        print(call.status_code, call.reason)
#        matrix = call.json()["durations"]
#        matrices[i] = matrix
#    fullmatrix = glue_matrices(matrices).tolist()
#    fullmatrix = [[0]+[duration/60 for duration in row] for row in fullmatrix]
#    d = [[0 for i in range(len(locations)+1)]] + fullmatrix
#    return d

# alternative to above method is OSRM API implemented below (http://project-osrm.org/)


def travel_matrix(size, lat, lon, path, silent=True):
    print('computing travel times...')
    f = 'using osrm'
    path = path
    if path:
        graph = osmnx.load_graphml(path)
        f = 'using osmnx'
    print(f)
    count = 0
    percent = 0
    n = size
    d = [[0 for j in range(n+1)] for i in range(n+1)]
    for i in range(n):
        for j in range(n):
            if i != j:
                if path:
                    d[i+1][j+1] = traveltime_osmnx(lat[i],
                                                   lat[j], lon[i], lon[j], graph)
                else:
                    d[i+1][j +
                           1] = traveltime_osrm(lat[i], lat[j], lon[i], lon[j])

                count += 1
                if count % np.ceil(0.01*(size**2)) == 0:
                    percent += 1
                    if not silent:
                        print(str(percent)+'%')
            elif i == j:
                d[i+1][j+1] = 0
    print('computation finished')
    return d

# # returns travel time in minutes between two coordinates (latitude,longitude degrees) using OSRM API


def traveltime_osrm(lat1, lat2, lon1, lon2):
    coordinates = str(lon1)+','+str(lat1)+';'+str(lon2)+','+str(lat2)
    url = 'http://router.project-osrm.org/route/v1/driving/'+coordinates
    response = requests.get(url)
    data = response.json()
    duration = data['routes'][0]['duration']
    dist = data['routes'][0]['distance']

    return dist


# returns travel time in minutes between two coordinates(latitude, longitude degrees) using osmnx


def traveltime_osmnx(lat1, lat2, lon1, lon2, graph):
    # Get node IDs of nearest nodes
    node_list = osmnx.distance.nearest_nodes(
        G=graph,
        X=[lon1, lon2],
        Y=[lat1, lat2]
    )
    # Calculate shortest path in seconds
    length = networkx.shortest_path_length(
        G=graph, source=node_list[0], target=node_list[1], weight='length')

    return length


def matrix_dev(distanceMatrix1, distanceMatrix2):
    M1 = np.array(distanceMatrix1)
    M2 = np.array(distanceMatrix2)
    D = M1 - M2
    F = M1/M2
    norm = np.linalg.norm(D)
    return M1, M2, D, F, norm
