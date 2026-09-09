"""Paper-based ADWIN2 mean estimator; raw Gaussian inputs carry no bounded-data guarantee.

Bifet & Gavalda, https://www.cs.upc.edu/~Gavalda/papers/adwin06.pdf,
practical Eq.(3.1) and bucket compression. Independently implemented, not vendored.
"""
import numpy as np
from numba import njit


@njit(cache=True)
def combine(n0, s0, m0, n1, s1, m1):
    if n0 == 0:
        return n1, s1, m1
    if n1 == 0:
        return n0, s0, m0
    difference = s1/n1-s0/n0
    return n0+n1, s0+s1, m0+m1+difference*difference*n0*n1/(n0+n1)


@njit(cache=True)
def aggregate(counts, sums, moments, used):
    n, total, moment = 0, 0., 0.
    for i in range(used):
        n, total, moment = combine(n, total, moment, counts[i], sums[i], moments[i])
    return n, total, max(0., moment)


@njit(cache=True)
def column(values, delta, clock):
    length = len(values)
    capacity = 6*(int(np.log2(max(1, length)))+2)
    counts = np.zeros(capacity, dtype=np.int64)
    sums, moments = np.zeros(capacity), np.zeros(capacity)
    prediction, updated, flags = np.zeros(length), np.zeros(length), np.zeros(length)
    widths, removed = np.zeros(length, dtype=np.int64), np.zeros(length, dtype=np.int64)
    used, estimate = 0, 0.
    for t in range(length):
        prediction[t] = estimate
        counts[used], sums[used], moments[used] = 1, values[t], 0.
        used += 1
        size = 1
        while True:
            first, number = -1, 0
            for i in range(used):
                if counts[i] == size:
                    if first == -1: first = i
                    number += 1
            if number <= 5:
                break
            assert number == 6 and counts[first+1] == size
            counts[first], sums[first], moments[first] = combine(
                counts[first], sums[first], moments[first], counts[first+1], sums[first+1], moments[first+1])
            for i in range(first+1, used-1):
                counts[i], sums[i], moments[i] = counts[i+1], sums[i+1], moments[i+1]
            used -= 1
            size *= 2
        n, total, moment = aggregate(counts, sums, moments, used)
        if (t+1) % clock == 0:
            while n >= 10:
                left_n, left_sum, violation = 0, 0., False
                logterm = np.log(2.*np.log(n)/delta)
                variance = moment/n
                for i in range(used-1):
                    left_n += counts[i]; left_sum += sums[i]
                    right_n = n-left_n
                    if left_n < 5 or right_n < 5: continue
                    reciprocal = 1./left_n+1./right_n
                    threshold = np.sqrt(2.*reciprocal*variance*logterm)+(2./3.)*reciprocal*logterm
                    if abs(left_sum/left_n-(total-left_sum)/right_n) > threshold:
                        violation = True
                        break
                if not violation: break
                removed[t] += counts[0]
                flags[t] = 1.
                for i in range(used-1):
                    counts[i], sums[i], moments[i] = counts[i+1], sums[i+1], moments[i+1]
                used -= 1
                n, total, moment = aggregate(counts, sums, moments, used)
        widths[t] = n
        estimate = total/n
        updated[t] = estimate
    return prediction, updated, flags, widths, removed


def run(y, delta, clock):
    y = np.asarray(y, dtype=np.float64)
    if y.ndim != 2 or not y.shape[0] or not y.shape[1] or not np.isfinite(y).all():
        raise ValueError('finite nonempty observations required')
    if not np.isfinite(delta) or not 0 < delta < 1 or type(clock) is not int or clock < 1:
        raise ValueError('invalid ADWIN configuration')
    predictions, updated, flags = np.zeros_like(y), np.zeros_like(y), np.zeros_like(y)
    widths, removed = np.zeros(y.shape, dtype=np.int64), np.zeros(y.shape, dtype=np.int64)
    for j in range(y.shape[1]):
        predictions[:, j], updated[:, j], flags[:, j], widths[:, j], removed[:, j] = column(y[:, j], delta, clock)
    norms = np.sqrt(np.sum((updated-predictions)**2, axis=1))
    return predictions, flags, norms, widths, removed
