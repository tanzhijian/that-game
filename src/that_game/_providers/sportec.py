import polars as pl

from .base import NAME_SEPARATOR, PERIOD_MINUTES, ExtraNames, Provider


def _add_type(df: pl.DataFrame) -> pl.DataFrame:
    """Sportec 的事件数据中，事件类型信息分散在多个列中
    （例如 type.name, subType.name 等），需要合并成一个统一的 type_name 列。

    1. 首先通过 concat_list 将所有可能包含事件类型信息的列合并成一个列表列。
    2. 使用 list.eval 对列表中的每个元素进行处理，
    首先通过 str.split(".") 将字符串按 "." 分割成两部分，
    然后通过 list.explode 将分割后的列表展开成多行。
    3. 再次使用 list.eval 对每个元素进行过滤，
    去除以 "@" 开头的字符串和空字符串，并保持唯一性。
    4. 最后通过 list.join 将剩余的元素用 ";" 连接起来，形成最终的 type_name 列
    """
    type_cols = df.columns[7:]

    return df.with_columns(
        pl.concat_list(
            [
                pl.when(pl.col(c).is_not_null())
                .then(pl.lit(c))
                .otherwise(None)
                for c in type_cols
            ]
        )
        .list.drop_nulls()
        .list.eval(
            pl.element()
            .str.split(".")
            .list.explode(keep_nulls=False, empty_as_null=True)
        )
        .list.eval(
            pl.element()
            .filter(
                (pl.element().str.starts_with("@").not_())
                & (pl.element() != "")
            )
            .unique(maintain_order=True)
        )
        .list.join(NAME_SEPARATOR)
        .alias(ExtraNames.TYPE)
    )


_period_mapping = {
    "firstHalf": 1,
    "secondHalf": 2,
    # 3 4 5 是用来占位填充的，公开数据集并没有加时赛和点球
    "extraFirstHalf": 3,
    "extraSecondHalf": 4,
    "shootout": 5,
}


def _add_period(df: pl.DataFrame) -> pl.DataFrame:
    # 1. 先获取 period，后续时间标准化都依赖它
    return df.with_columns(
        pl.col("KickOff.@GameSection")
        .replace_strict(_period_mapping, default=None)
        .cast(pl.Int8)
        .forward_fill()
        .alias("std_period")
    )


def _add_time(df: pl.DataFrame) -> pl.DataFrame:
    _event_time_expr = pl.col("@EventTime").str.to_datetime(
        format="%Y-%m-%dT%H:%M:%S%.f%:z"
    )
    return df.with_columns(
        # 2. 取当前 period 的第一条事件时间，作为该 period 的起点
        (_event_time_expr - _event_time_expr.first().over("std_period"))
        .dt.cast_time_unit("ms")
        .alias(ExtraNames.TIME),
    )


def _add_full_time(df: pl.DataFrame) -> pl.DataFrame:
    return df.with_columns(
        # 3. full_time = period 起始分钟 + period 内相对时间
        (
            pl.col("std_time")
            + (
                pl.col("std_period")
                .replace_strict(PERIOD_MINUTES)
                .cast(pl.Int64)
                * 60_000
            ).cast(pl.Duration("ms"))
        ).alias(ExtraNames.FULL_TIME),
    )


def _preprocess(df: pl.DataFrame) -> pl.DataFrame:
    df = _add_type(df)
    df = _add_full_time(_add_time(_add_period(df)))
    return df


sportec = Provider(
    data_type="xml",
    root="PutDataRequest.Event",
    preprocess=_preprocess,
    field_aliases={
        "id": "@EventId",
        "type": ExtraNames.TYPE,
        "period": ExtraNames.PERIOD,
        "time": ExtraNames.TIME,
        "full_time": ExtraNames.FULL_TIME,
    },
)
