import numpy as np
import matplotlib.pyplot as plt

golden_ratio_global = (np.sqrt(5) - 1) / 2


def backward_recursive_power(n, initial_guess, df_type):
    # Initial empty list:
    steps = np.empty(n+2, dtype=df_type)
    steps[-2] = initial_guess
    steps[-1] = initial_guess * golden_ratio_global

    # Iterate backwards using formula:
    for i in range(np.size(steps) - 3, -1, -1):
        steps[i] = steps[i+1] + steps[i+2]

    # Normalize and return:
    return initial_guess / steps[0]


def golden_powers_down(n, df_type):
    # Initialize initial variables:
    data = np.empty((n, 3), dtype=df_type)
    data[0] = (1,1,1)

    # Generate data:
    for i in range(1, n):
        # Generate directly calculated value:
        direct_value = data[i - 1, 0] * golden_ratio_global
        # Generate recursive value using the algorithm:
        recursive_value = backward_recursive_power(i, 1, df_type)
        # Put all in one record of the table:
        data[i] = (recursive_value, direct_value, recursive_value - direct_value)

    return data


a = golden_powers_down(31, 'float32')

goldown = golden_powers_down(31,'float32')
plt.plot(range(2,25),np.log10(abs(goldown[2:25,2])))
plt.title('stab_down',fontsize=16)
plt.xlabel('n',fontsize=14)
plt.ylabel('log-abs-error',fontsize=14)
plt.show()