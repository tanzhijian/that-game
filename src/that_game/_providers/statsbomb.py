import polars as pl

from .base import PERIOD_MINUTES, ExtraNames, Provider


def _add_time(df: pl.DataFrame) -> pl.DataFrame:
    return df.with_columns(
        (
            pl.col("timestamp").str.to_time(
                format="%H:%M:%S%.f"
            )  # 1. 先转换为 Time 类型
            - pl.time(0, 0, 0)  # 2. 减去参考点 00:00:00 得到 Duration
        )
        .dt.cast_time_unit("ms")
        .alias(ExtraNames.TIME)
    )


def _add_full_time(df: pl.DataFrame) -> pl.DataFrame:
    # 3. full_time = period 起始分钟 + period 内相对时间
    return df.with_columns(
        (
            pl.col("std_time")
            + (
                pl.col("period").replace_strict(PERIOD_MINUTES).cast(pl.Int64)
                * 60_000
            ).cast(pl.Duration("ms"))
        ).alias("std_full_time")
    )


def _preprocess(df: pl.DataFrame) -> pl.DataFrame:
    df = _add_full_time(_add_time(df))
    return df


statsbomb = Provider(
    data_type="json",
    root=".",
    field_aliases={
        "type": "type.name",
        "time": ExtraNames.TIME,
        "full_time": ExtraNames.FULL_TIME,
    },
    preprocess=_preprocess,
)
