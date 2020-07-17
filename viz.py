import matplotlib
import matplotlib.pyplot as plt


def plot_trended_study_time(df):
    fig, ax = plt.subplots(figsize=(16, 10))

    ax.scatter(df["date"], df["seconds"], alpha=0.5, s=10)

    loc = matplotlib.ticker.MultipleLocator(250)
    ax.xaxis.set_major_locator(loc)

    def minutes(x, pos):
        return "{:,.1f}".format(x / 60)

    fmtr = matplotlib.ticker.FuncFormatter(minutes)
    _ = ax.yaxis.set_major_formatter(fmtr)

    ax.plot(
        df["date"],
        df["seconds"].rolling(window=7, center=False).mean(),
        c="r",
        label="7 day rolling avg",
    )
    ax.plot(
        df["date"],
        df["seconds"].rolling(window=30, center=False).mean(),
        c="g",
        label="30 day rolling avg",
    )

    ax.legend(loc="upper left")

    return ax
