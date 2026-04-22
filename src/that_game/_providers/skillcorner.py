from .base import FieldMap, Provider

skillcorner = Provider(
    data_type="csv",
    field_map=FieldMap(
        id_="event_id",
        type_="end_type",  # 暂时先使用 end_type, 之后再来扩充
        )
    )
