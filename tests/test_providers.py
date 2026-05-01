import polars as pl

from that_game import providers


class TestSkillcornerProvider:
    def test_preprocess_builds_type_name_from_event_type_columns(
        self,
    ) -> None:
        assert providers.skillcorner.preprocess is not None

        df = pl.DataFrame(
            {
                "event_type": ["Shot", "Pass"],
                "event_subtype": ["OpenPlay", None],
                "start_type": [None, "ThrowIn"],
                "end_type": ["Goal", None],
            }
        )

        result = providers.skillcorner.preprocess(df)
        assert result.get_column("std_type").to_list() == [
            "Shot;OpenPlay;Goal",
            "Pass;ThrowIn",
        ]


class TestSportecProvider:
    def test_preprocess_builds_type_name_from_xml_style_column_names(
        self,
    ) -> None:
        assert providers.sportec.preprocess is not None

        df = pl.DataFrame(
            {
                "c0": [1],
                "c1": [1],
                "c2": [1],
                "c3": [1],
                "c4": [1],
                "c5": [1],
                "c6": [1],
                "type.name": ["shot"],
                "type.@id": ["10"],
                "subType.name": ["open_play"],
                "subType.name.detail": ["detail"],
                "subType.@id": ["11"],
                "qualifier..name": ["value"],
            }
        )

        result = providers.sportec.preprocess(df)

        assert result.get_column("std_type").to_list() == [
            "type;name;subType;detail;qualifier"
        ]
