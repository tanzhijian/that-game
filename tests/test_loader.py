# 不测公开入口 load_events, load_tracking
# 测几个私有函数
# provider 相关的测试在 test_provider 模块

from pathlib import Path

import polars as pl
import pytest

from that_game._loader import _flatten_structs, _load_xml, _read_text_if_path

DATA_PATH = Path.cwd() / "tests/data/load"
XML_FILE = DATA_PATH / "sample.xml"
XML_STR = """
<root>
  <events>
    <event>
      <id>event-1</id>
      <type>
        <name>Shot</name>
      </type>
      <x>10</x>
    </event>
    <event>
      <id>event-2</id>
      <type>
        <name>Pass</name>
      </type>
      <x>20</x>
    </event>
  </events>
</root>
"""
DATA = [
    {"id": "event-1", "type": {"name": "Shot"}, "x": 10},
    {"id": "event-2", "type": {"name": "Pass"}, "x": 20},
]


@pytest.mark.parametrize("source", [XML_FILE, str(XML_FILE),  XML_STR])
def test_read_text_if_path(source: str | Path) -> None:
    text = _read_text_if_path(source)
    assert text.lstrip()[:6] == "<root>"


def test_flatten_structs() -> None:
    df = pl.DataFrame(DATA)
    flattened_df = _flatten_structs(df)
    assert "type.name" in flattened_df.columns

def test_load_xml() -> None:
    df = _load_xml(XML_STR, root="root.events.event")
    assert df["x"][0] == "10"
