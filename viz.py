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
    known_cards = df.query('status=="known"')["date"].value_counts().sort_index()
    all_cards = df["date"].value_counts().sort_index()

    fig, ax = plt.subplots(figsize=(16, 10))
    known_cards.plot(ax=ax, c="b", label="Known Cards")
    all_cards.plot(ax=ax, c="r", label="Total Cards Seen")

    ax.legend(loc="upper left", fontsize=12)
    ax.set_title("Accumulation of Cards", fontsize=20)

    return ax
