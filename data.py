"""
Utilities for extracting and cleaning our Anki data

This README of schema definitions was super helpful in
constructing these functions

    https://github.com/ankidroid/Anki-Android/wiki/Database-Structure
"""

import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta
from itertools import zip_longest
from typing import Dict, List

import pandas as pd

DB_PATH = "C:/Users/Nick/AppData/Roaming/Anki2/Nick/"


@contextmanager
def connect_to_db(database: str):
    path = DB_PATH
    conn = sqlite3.connect(path + database)
    cur = conn.cursor()

    yield cur

    conn.commit()
    conn.close()


def get_study_time() -> pd.DataFrame:
    """
    Get the number of seconds spent studying per day.

    Gets the min date and the max date from the data and
    fills with 0s where appropriate.
    """

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


def get_reviewed_cards() -> List[int]:
    """
    Query all cards that appear in the review log
    table and also have a valid card id (not deleted)
    """
    sql = """
        select
            distinct r.cid
            from    revlog r
                left join  cards c
                    on     c.id = r.cid
            where   r.ivl > 0
            and  c.id is not null
    """

    with connect_to_db("collection.anki2") as cursor:
        cursor.execute(sql)
        reviewed_cards = [x[0] for x in cursor.fetchall()]

    return reviewed_cards


def get_card_status_by_day(card_id: int) -> pd.DataFrame:
    """
    From the first day we've reviewed it to today, what status
    ('known', 'due') was each card in?
    """
    sql = f"""
        select
            cid,
            strftime('%Y-%m-%d', datetime(id / 1000, 'unixepoch', 'localtime')),
            ivl

            from    revlog
            where   cid = {card_id}
                and ivl > 0
    """
    card_statuses = dict()

    with connect_to_db("collection.anki2") as cursor:
        cursor.execute(sql)
        data = cursor.fetchall()

        # look at pairs of days until there are no more,
        # fill with today when we run out of values
        row_a = [
            (datetime(*map(int, date.split("-"))), delta) for _, date, delta in data
        ]
        row_b = row_a[1:]

        for pair in zip_longest(row_a, row_b, fillvalue=(datetime.now(), 0)):
            (review_date, delta), (next_review_date, _) = pair

            due_date = review_date + timedelta(days=delta)

            days_to_next_review = (next_review_date - review_date).days
            for day in range(days_to_next_review):
                date = review_date + timedelta(days=day)
                date_str = datetime.strftime(date, "%Y-%m-%d")

                past_due = date > (due_date)

                if past_due:
                    card_statuses[date_str] = "due"
                else:
                    card_statuses[date_str] = "known"

    df = pd.DataFrame(
        {
            "card_id": card_id,
            "date": list(card_statuses.keys()),
            "status": list(card_statuses.values()),
        }
    )

    return df


def get_all_card_statuses_by_day() -> pd.DataFrame:
    reviewed_cards = get_reviewed_cards()

    dfs = []
    for card_id in reviewed_cards:
        dfs.append(get_card_status_by_day(card_id))

    df = pd.concat(dfs).reset_index(drop=True)

    return df
