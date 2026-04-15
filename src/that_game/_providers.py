from dataclasses import dataclass
from typing import Callable, Literal

import polars as pl


@dataclass(kw_only=True)
class Index:
    id_: str
    type_: str


@dataclass(kw_only=True)
class Provider:
    data_type: Literal["csv", "xml", "json", "jsonl"]
    root: str = "."
    preprocess: Callable[[pl.DataFrame], pl.DataFrame] | None = None

    index: Index


def _sportec_events_add_type_field(df: pl.DataFrame) -> pl.DataFrame:
    """Sportec 的事件数据中，事件类型信息分散在多个列中
    （例如 type.name, subType.name 等），需要合并成一个统一的 type_name 列。

    1. 首先通过 concat_list 将所有可能包含事件类型信息的列合并成一个列表列。
    2. 使用 list.eval 对列表中的每个元素进行处理，
    首先通过 str.split(".") 将字符串按 "." 分割成两部分，
    然后通过 list.explode 将分割后的列表展开成多行。
    3. 再次使用 list.eval 对每个元素进行过滤，
    去除以 "@" 开头的字符串和空字符串，并保持唯一性。
    4. 最后通过 list.join 将剩余的元素用 "_" 连接起来，形成最终的 type_name 列
    """
    target_cols = df.columns[7:]

    return df.with_columns(
        pl.concat_list(
            [
                pl.when(pl.col(c).is_not_null())
                .then(pl.lit(c))
                .otherwise(None)
                for c in target_cols
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
                (pl.element().str.starts_with("@").not_()) &
                (pl.element() != "")
            )
            .unique(maintain_order=True)
        )
        .list.join("_")
        .alias("type_name")
    )


statsbomb = Provider(
    data_type="json",
    root=".",
    index=Index(id_="id", type_="type.name"),
)
sportec = Provider(
    data_type="xml",
    root="PutDataRequest.Event",
    preprocess=_sportec_events_add_type_field,
    index=Index(id_="@EventId", type_="type_name"),
)
