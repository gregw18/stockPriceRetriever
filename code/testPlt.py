"""
Testing matplotlib, seeing if can get nice looking horizontal bar charts for price range of
each security.
"""

import matplotlib.pyplot as plt
import numpy as np


def plt_me():
    low = 0
    price = 6
    high = 0

    fig, axes = plt.subplots(nrows=3, ncols=1)

    p1 = axes[0]
    p1.barh("AAPL", low, color='red', height=2)
    p1.barh("AAPL", price, color='yellow', left=low, height=2)
    p1.barh("AAPL", high, color="green", left=low + price, height=2)
    # p1.set_xticks([0, 2, 4, 6, 8, 10])
    p1.set_ylabel("Apple")
    # p1.set_title( "Apple Shares")
    p1.vlines(3, -2.5, 2.5)
    p1.set_xbound(0, 12)
    # f1.show()
    # p1.plot()

    low2 = 100
    price2 = 60
    high2 = 20
    p2 = axes[1]
    p2.barh("XOM", low2, color='red')
    p2.barh("XOM", price2, color='yellow', left=low2)
    p2.barh("XOM", high2, color="green", left=low2 + price2)
    # p2.set_xticks([90, 110, 130, 150, 170, 190])
    p2.set_ylabel("Exxon Mobil Shares")
    # p2.set_title( "Exxon Mobil Shares")
    p2.vlines(95, -5, 5)
    p2.set_xbound(80, 200)
    # f2.show()
    # p2.plot()

    low3 = 50
    price3 = 60
    high3 = 70
    p3 = axes[2]
    p3.barh("MSFT", low2, color='red')
    p3.barh("MSFT", price2, color='yellow', left=low3)
    p3.barh("MSFT", high2, color="green", left=low3 + price3)
    # p3.set_xticks([30, 40, 50, 60, 70, 80])
    p3.set_ylabel("Microsoft Shares")
    # p3.set_title( "Microsoft Shares")
    p3.vlines(60, -5, 5)
    p3.set_xbound(50, 80)

    fig.show()
    plt.show(block=True)
    # input()


def plt_sample():
    countries = ['USA', 'GB', 'China', 'Russia', 'Germany']
    bronzes = np.array([38, 17, 26, 19, 15])
    silvers = np.array([37, 23, 18, 18, 10])
    golds = np.array([46, 27, 26, 19, 17])
    ind = [x for x, _ in enumerate(countries)]

    plt.barh(ind, golds, height=0.8, label='golds', color='gold', left=silvers+bronzes)
    plt.barh(ind, silvers, height=0.8, label='silvers', color='silver', left=bronzes)
    plt.barh(ind, bronzes, height=0.8, label='bronzes', color='#CD853F')

    plt.yticks(ind, countries)
    plt.xlabel("Medals")
    plt.ylabel("Countries")
    plt.legend(loc="upper right")
    plt.title("2012 Olympics Top Scorers")

    plt.show()


# plt_sample()
plt_me()
