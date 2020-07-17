import pandas as pd


from contextlib import contextmanager
import sqlite3


@contextmanager
def connect_to_db(database: str):
    path = "C:/Users/Nick/AppData/Roaming/Anki2/Nick/"
    conn = sqlite3.connect(path + database)
    cur = conn.cursor()

    yield cur

    conn.commit()
    conn.close()


def get_study_time():
    sql = """
        SELECT
        strftime('%Y-%m-%d', datetime(round(id / 1000), 'unixepoch', 'localtime')) as review_date,
        sum(time / 1000.0) as seconds
        
        from 		revlog
        
        group by	review_date
        order by	review_date
    """

    with connect_to_db("collection.anki2") as cursor:
        cursor.execute(sql)
        records = cursor.fetchall()

    populated_df = pd.DataFrame(
        {"date": [x[0] for x in records], "seconds": [x[1] for x in records]}
    )
    populated_df["date"] = pd.to_datetime(populated_df["date"])

    min_date = populated_df["date"].min()
    max_date = populated_df["date"].max()

    every_day_series = pd.date_range(min_date, max_date)
    every_day_frame = every_day_series.to_frame(name="date")

    merged = every_day_frame.merge(
        populated_df, left_index=True, right_on="date", how="left"
    )

    del merged["date_x"]
    del merged["date_y"]

    merged = merged.fillna(0)
    merged = merged.reset_index(drop=True)

    return merged

