import numpy as np

"""
module contains Instance class

Instance class contains model parameters:
    n: number of clients including base location
    v: number of employees(/vehicles)/shifts
    d: travel time/distance matrix
    p: service time(/processing time) vector
    tw: time window vector
    Q: qualification level matrix
    u: shift duration vector
    ss: shift start time vector
    
    model parameters (except n,v) are randomly generated by default
    function parameters simulate a (random) work day scenario of 4 hours
    time unit is in minutes
"""


class Instance:
    def __init__(self, n, v, d='d', p='p', tw='tw', Q='Q', u='u', ss='ss'):
        self.n = n
        self.v = v
        self.d = self.load(d)
        self.p = self.load(p)
        self.tw = self.load(tw)
        self.Q = self.load(Q)
        self.u = self.load(u)
        self.ss = self.load(ss)

        self.feasibleShiftsForClients = self.det_feas_shifts_for_clients()

    def det_feas_shifts_for_clients(self):

        feasShiftsForClients = []

        for i in range(self.n - 1):
            feasShiftsForClients.append(np.argwhere(self.Q[i, :] == 1)[:, 0])

        return feasShiftsForClients

    def load_d(self, lower=5, upper=15):
        N = set(range(self.n))
        d = []
        for i in N:
            d.append([])
            for j in N:
                if j == i:
                    d[i].append(0)
                else:
                    d[i].append(np.random.randint(lower, upper))
        for i in N:
            for j in N-{i}:
                d[i][j] = d[j][i]
        return d

    def load_p(self, lower=10, upper=45):
        p = [0]
        for i in range(self.n-1):
            p.append(np.random.randint(lower, upper))
        return p

    def load_tw(self, spacing=10, amount=24, length=30):
        s = np.random.choice(
            [spacing*x for x in range(amount)], size=self.n-1).tolist()
        e = [round(x+length) for x in s]
        tw = [None]
        for i in range(self.n-1):
            tw.append((s[i], e[i]))
        return tw

    def load_Q(self):
        return np.ones((self.n-1, self.v))

    def load_u(self, duration=[120, 180, 240]):
        return np.random.choice(duration, size=self.v).tolist()

    def load_ss(self):
        return [0 for k in range(self.v)]

    def load(self, parameter):
        f = {
            'd': self.load_d,
            'p': self.load_p,
            'tw': self.load_tw,
            'Q': self.load_Q,
            'u': self.load_u,
            'ss': self.load_ss
        }

        if isinstance(parameter, str):
            return f[parameter]()
        else:
            return parameter


if __name__ == "__main__":

    n = 5
    v = 2
    ins = Instance(n, v)
    print('n:', ins.n)
    print('v:', ins.v)
    print('d:', ins.d)
    print('p:', ins.p)
    print('tw:', ins.tw)
    print('Q:', ins.Q)
    print('u:', ins.u)
    print('ss:', ins.ss)
