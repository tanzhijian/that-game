import polars as pl

from .base import NAME_SEPARATOR, FieldMap, Provider


def _add_type_name(df: pl.DataFrame) -> pl.DataFrame:
    """将 SkillCorner 分散的事件类型字段合并为统一的 type_name 列。

    1. 首先通过 concat_list 将所有可能包含事件类型信息的列合并成一个列表列。
    2. 使用 list.join 将列表中的元素用 ";" 连接起来，形成最终的 type_name 列。
    """
    type_cols = ["event_type", "event_subtype", "start_type", "end_type"]

    return df.with_columns(
        pl.concat_list([pl.col(col) for col in type_cols])
        .list.join(NAME_SEPARATOR)
        .alias("type_name")
    )


skillcorner = Provider(
    data_type="csv",
    preprocess=_add_type_name,
    field_map=FieldMap(
        id_="event_id",
        type_="type_name",
    ),
)
