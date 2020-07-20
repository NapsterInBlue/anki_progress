import matplotlib
import matplotlib.pyplot as plt


def plot_trended_study_time(df):
    fig, ax = plt.subplots(figsize=(16, 10))

    ax.scatter(df["date"], df["seconds"], alpha=0.5, s=10)

    loc = matplotlib.ticker.MultipleLocator(250)
    ax.xaxis.set_major_locator(loc)

    loc = matplotlib.ticker.MultipleLocator(60 * 60)
    ax.yaxis.set_major_locator(loc)

    loc = matplotlib.ticker.MultipleLocator(30 * 60)
    ax.yaxis.set_minor_locator(loc)

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

    ax.legend(loc="upper left", fontsize=12)
    ax.grid(True, "major", axis="y", c="k")
    ax.grid(True, "minor", axis="y", alpha=0.5)

    ax.set_title("Minutes Spent Studying", fontsize=20)

    return ax


def plot_card_catalog_growth(df):
    fig, ax = plt.subplots(figsize=(16, 10))

    loc = matplotlib.ticker.MultipleLocator(250)
    ax.xaxis.set_major_locator(loc)

    ax.stackplot(
        df.index,
        [
            df["> year"],
            df["< year"],
            df["< month"],
            df["< 6 months"],
            df["< week"],
            df["due"],
        ],
        labels=["> year", "< year", "< 6 months", "< month", "< week", "due"],
        colors=["#309143", "#51b364", "#8ace7e", "#f0bd27", "#ff684c", "b60a1c"],
    )
    ax.xaxis.set_major_locator(loc)
    ax.legend(loc="upper left", fontsize=12)

    ax.set_title("Card Growth By Ease", fontsize=20)
    return ax
