import pandas as pd
import os.path
import travel_matrix as tmx
import store_n_load as snl
import time


def read_data(nrows):
    abs_path = os.path.abspath('travel_matrix.py')
    directory = os.path.dirname(abs_path)
    save_path = directory
    file_name = 'test'
    extension = '.xlsx'
    complete_path = os.path.join(save_path, file_name+extension)
    xfile = pd.ExcelFile(complete_path)
    activity_data = pd.read_excel(xfile, 'activity_data', nrows=nrows)
    return activity_data


def main():
    df = read_data(nrows=10)
    print(df.head())
    size = df.shape[0]
    print(size)
    lat = df.latitude
    lon = df.longitude
    path = None
    tic = time.perf_counter()
    tm_osrm = tmx.travel_matrix(size, lat, lon, path)
    toc = time.perf_counter()
    print(f'Calculated travel matrix in {toc - tic:0.4f} seconds')
    print(tm_osrm[0])
    print(tm_osrm.__class__.__name__)
    fn = "travel_matrix_osrm"
    sp = os.path.abspath(os.getcwd())
    snl.store(tm_osrm, fn, sp)
    path = "deventer_graph.graphml"
    #path = "deventer_graph_s.graphml"
    tic = time.perf_counter()
    tm_osmnx = tmx.travel_matrix(size, lat, lon, path)
    toc = time.perf_counter()
    print(f'Calculated travel matrix in {toc - tic:0.4f} seconds')
    print(tm_osmnx[0])
    print(tm_osmnx.__class__.__name__)
    fn = "travel_matrix_osmnx"
    sp = os.path.abspath(os.getcwd())
    snl.store(tm_osmnx, fn, sp)
    mx_d = tmx.matrix_dev(tm_osrm, tm_osmnx)
    print(mx_d)


if __name__ == "__main__":
    main()
