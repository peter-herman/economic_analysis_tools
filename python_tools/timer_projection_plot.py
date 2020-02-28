__Author__ = "Peter Herman"
__Project__ = "misc_tools"
__Created__ = "February 25, 2020"
__Description__ = ''' '''

import numpy as np
import matplotlib.pyplot as plt
import timeit
from numba import jit
test_func = '''
def test_function(iter):
	for i in iter:
		for j in iter:
			i == j
'''

@jit
def numba_test(iter):
	for i in iter:
		for j in iter:
			i == j

a = timeit.timeit(stmt = 'test_function(range(1))', setup=test_func, number=10000)
b = timeit.timeit(stmt = 'test_function(range(10))', setup=test_func, number=10000)
c = timeit.timeit(stmt = 'test_function(range(100))', setup=test_func, number=10000)

x = np.array([0,1,2])
y = np.array([a,b,c])
z = np.polyfit(x, y, 10)
print(z)

p = np.poly1d(z)
print(p(0.5)) # Polynomial Function evaluated at 0.5




xp = np.linspace(0, 5, 5)
_ = plt.plot(x, y, '.', xp, p(xp), '-')
#plt.ylim(-2,2)
plt.show()