import math
import numpy as np


def bezier(points, pts_to_calc=100):
    result = np.zeros([pts_to_calc, 2])

    Ni = lambda n, i: math.factorial(n) / (math.factorial(i) * math.factorial(n - i))
    Basis = lambda n, i, t: Ni(n, i) * math.pow(t, i) * math.pow(1 - t, n - i)

    npts = len(points)
    cpts = len(result)

    count = 0
    j = np.zeros([1, npts], float)

    t = 0
    step = 1 / (cpts - 1)

    while t <= 1:
        for i in range(1, npts + 1):
            j[0][i - 1] = Basis(npts - 1, i - 1, t)

        temp = j.dot(points)

        result[count][0] = temp[0][0]
        result[count][1] = temp[0][1]

        t += step
        count += 1

    return result
