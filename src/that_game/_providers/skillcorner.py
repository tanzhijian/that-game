import polars as pl

from .base import NAME_SEPARATOR, PERIOD_MINUTES, ExtraNames, Provider


def _add_type(df: pl.DataFrame) -> pl.DataFrame:
    """将 SkillCorner 分散的事件类型字段合并为统一的 type_name 列。

    1. 首先通过 concat_list 将所有可能包含事件类型信息的列合并成一个列表列。
    2. 使用 list.join 将列表中的元素用 ";" 连接起来，形成最终的 type_name 列。
    """
    type_cols = ["event_type", "event_subtype", "start_type", "end_type"]

    return df.with_columns(
        pl.concat_list([pl.col(col) for col in type_cols])
        .list.join(NAME_SEPARATOR)
        .alias(ExtraNames.TYPE)
    )


def _add_full_time(df: pl.DataFrame) -> pl.DataFrame:
    return df.with_columns(
        (
            (
                pl.col("time_end").str.extract(r"^(\d+):", 1).cast(pl.Float64)
                * 60
                + pl.col("time_end")
                .str.extract(r":(\d+(?:\.\d+)?)$", 1)
                .cast(pl.Float64)
            )
            * 1000
        )
        .round(0)
        .cast(pl.Int64)
        .cast(pl.Duration("ms"))
        .alias("std_full_time")
    )


def _add_time(df: pl.DataFrame) -> pl.DataFrame:
    return df.with_columns(
        (
            pl.col("std_full_time")
            - (
                pl.col("period").replace_strict(PERIOD_MINUTES).cast(pl.Int64)
                * 60_000
            ).cast(pl.Duration("ms"))
        ).alias("std_time"),
    )


def _preprocess(df: pl.DataFrame) -> pl.DataFrame:
    df = _add_type(df)
    df = _add_time(_add_full_time(df))
    return df


skillcorner = Provider(
    data_type="csv",
    preprocess=_preprocess,
    field_aliases={
        "id": "event_id",
        "type": ExtraNames.TYPE,
        "time": ExtraNames.TIME,
        "full_time": ExtraNames.FULL_TIME,
    },
)
