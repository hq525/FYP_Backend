
# import matplotlib.pyplot as plt
# import numpy as np

# x = [1, 2, 3, 4, 5, 6]
# randomY = [8450.96179455722,12459.322116147048,13000.76900518537,10750.864571804103,13072.034940399933,12081.273126357415]
# FCFSY = [7812.245626260733,12319.016865414862,12218.677529853181,10483.482501846796,12232.859847397407,11960.69414005934]
# lyapunovY = [11217.91285921344,13083.880872275928,13312.098683954742,12098.787409927676,13202.179628671975,12361.258979849432]

# plt.plot(x, randomY, label="Random")
  
# # second plot with x1 and y1 data
# plt.plot(x, FCFSY, '-.', label="FCFS")

# plt.plot(x, lyapunovY, '-', label="Lyapunov")
  
# plt.xlabel("Attempt")
# plt.ylabel("Value B")
# plt.title('Value B derived for each algorithm')
# plt.ylim(7800, 13320)
# plt.legend()
# plt.show()


# importing package
import matplotlib.pyplot as plt
import numpy as np
  
# create data
x = ['Lyapunov', 'FCFS', 'Random']
y = np.array([739.618599615421,715.8817919151436,808.2324926981532])
y1 = np.array([34.925126120343755,149.6281229080759,199.55971141249415])
y2 = np.array([82.08496713580513,131.11610731888817,144.38696054928573])
y3 = np.array([168.51410377868288,149.38698705713952,141.32761116174967])
y4 = np.array([226.1351147672004,151.79800806492457,153.87725949207567])
y5 = np.array([227.95928781338785,133.95256656611542,169.08095008254776])

plt.plot(x, y, color='black')
# plot bars in stack manner
plt.bar(x, y1, color='r')
plt.bar(x, y2, bottom=y1, color='b')
plt.bar(x, y3, bottom=y1+y2, color='y')
plt.bar(x, y4, bottom=y1+y2+y3, color='g')
plt.bar(x, y5, bottom=y1+y2+y3+y4, color='lavender')
plt.xlabel("Algorithm")
plt.ylabel("ValueA")
plt.legend(["Total","Beneficiary 1", "Beneficiary 2", "Beneficiary 3", "Beneficiary 4"])
plt.title("ValueA by beneficiary for each algorithm")
plt.show()