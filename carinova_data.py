import pandas as pd
import os.path
import numpy as np

'''
module to load instance for region: city, suburb or rural
'''


def fetch_data(region):

    # load schedule data of region
    abs_path = os.path.abspath('carinova_data.py')
    directory = os.path.dirname(abs_path)
    save_path = directory
    file_name = 'example_data'
    extension = '.xlsx'
    complete_path = os.path.join(save_path, file_name+extension)
    xfile = pd.ExcelFile(complete_path)

    activity_data = pd.read_excel(xfile, 'activity_data')
    shift_data = pd.read_excel(xfile, 'shift_data')

    # time conversion datetime to minutes
    def convert(t): return 60*t.hour + t.minute + t.second/60

    # number of clients and number of shifts
    n, v = activity_data.shape[0], shift_data.shape[0]

    # processing time per activity
    p = [activity_data['duration'][i] for i in range(n)]
    p.insert(0, 0)

    # travel time matrix
    from store_n_load import load
    #d = load('travel_matrix', save_path)
    d = load('travel_matrix_osmnx', save_path)

    # shift duration
    u = []
    for k in range(v):
        shift_start = shift_data['shift_start'][k]
        shift_end = shift_data['shift_end'][k]
        shift_duration = convert(shift_end)-convert(shift_start)
        u.append(shift_duration)

    # shift start times
    ss = []
    for k in range(v):
        shift_start = shift_data['shift_start'][k]
        ss.append(convert(shift_start))

    # qualification matrix
    activityQ = activity_data['activity_level']
    shiftQ = shift_data['shift_level']
    Q = np.zeros((n, v))
    for i in range(n):
        for k in range(v):
            if activityQ[i] <= shiftQ[k]:
                Q[i][k] = 1

    # extract route from schedule
    route = [[] for k in range(v)]
    for i in range(n):
        shiftnr = activity_data['shift_id'][i]
        route[shiftnr].append(i+1)

    # time windows
    # step 1: temporary set tw to shift start and end time
    twtemp = [0 for i in range(n)]
    for i in range(n):
        shift_id = activity_data['shift_id'][i]
        twtemp[i] = [ss[shift_id], ss[shift_id]+u[shift_id]]
    twtemp.insert(0, None)

    # step 2: interpolate time windows
    import instance
    import schedule
    ins = instance.Instance(n+1, v, d, p, twtemp, Q, u, ss)
    sched = schedule.Schedule(ins, route)
    arrival = sched.arrival

    # arrival times without base location
    arrival2 = []
    for a in arrival:
        if a != None:
            arrival2.append(a[1:-1])
        else:
            arrival2.append([])

    # arrival time per activity: midpoint for tw
    length = 60
    mid = [0 for i in range(n)]
    s = [0 for i in range(n)]
    for activity_id in activity_data['activity_id']:
        for r in route:
            if activity_id in r:
                shift_id = route.index(r)
                activity_idx = r.index(activity_id)
        mid[activity_id-1] = arrival2[shift_id][activity_idx]

    # shift start time per activity
    s = [0 for i in range(n)]
    for i in range(n):
        shift_id = activity_data['shift_id'][i]
        s[i] = ss[shift_id]

    # step 3: compute time windows
    start, end = [], []
    for i in range(n):
        left = min(length/2, mid[i]-s[i])
        right = length-left
        start.append(mid[i]-left)
        end.append(mid[i]+right)
    tw = [0 for i in range(n)]
    for i in range(n):
        tw_bool = activity_data['tw_bool'][i]
        if tw_bool == 1:
            tw[i] = [convert(activity_data['tw_start'][i]),
                     convert(activity_data['tw_end'][i])]
        else:
            tw[i] = [start[i], end[i]]
    tw.insert(0, None)

    extract = {
        'n': n+1,  # +1 to include base
        'v': v,
        'p': p,
        'd': d,
        'tw': tw,
        'Q': Q,
        'u': u,
        'ss': ss,
        'route': route,
        'arrival': arrival,
        'arrival_nobase': arrival2,
        'score': sched.evaluate(),
        'dist': sched.distance(),
        'wt': sched.waiting_time(),
        'ot': sched.shift_overtime()
    }
    return extract


if __name__ == "__main__":

    region = 'city'  # choose city, rural or suburb
    data = fetch_data(region)
    n = data['n']
    v = data['v']
    p = data['p']
    d = data['d']
    tw = data['tw']
    Q = data['Q']
    u = data['u']
    ss = data['ss']
    route = data['route']
    arrival = data['arrival']
    arrival2 = data['arrival_nobase']
    score = data['score']
    dist = data['dist']
    wt = data['wt']
    ot = data['ot']

    # create plot for activity demand and fit of shift
    demand = []
    for a in arrival2:
        demand += a

    def active_shifts(t):
        ee = [0 for k in range(v)]
        for k in range(v):
            ee[k] = ss[k] + u[k]

        active = sum(start <= t for start in ss)
        inactive = sum(end < t for end in ee)
        return active - inactive

    # to configure range x-axis
    max_times = []
    for a in arrival:
        max_times += a
    x = list(np.arange(min(ss), max(max_times), 0.1))
    y = [active_shifts(t) for t in x]

    import matplotlib.pyplot as plt

    fig, ax1 = plt.subplots()

    manual_bins = list(np.arange(min(ss), max(max_times), 60))
    ax1.set_xlabel('time')
    ax1.set_ylabel('Number of activities')
    bins = ax1.hist(demand, color='grey', edgecolor='black', bins=manual_bins)

    xticks = bins[1]

    def convert2(minutes): return '{:02d}:{:02d}'.format(
        *divmod(int(minutes), 60))
    xtick_labels = [convert2(xticks[i]) for i in range(len(bins[1]))]
    ax1.set_xticks(xticks)
    ax1.set_xticklabels(xtick_labels, rotation='vertical')

    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
    ax2.set_ylabel('Number of active shifts')
    ax2.plot(x, y, linestyle='-')

    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    plt.show()
