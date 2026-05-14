from typing import Any

import pytest


@pytest.fixture(scope="session")
def statsbomb_events_data() -> dict[str, Any]:
    return {
        "id": ["1", "2", "3", "4", "5"],
        "type": {
            "name": ["Carry", "Pass", "Pressure", "Shot", "Duel"],
        },
        "period": [1, 2, 3, 4, 5],
        "timestamp": [
            "00:38:59.380",
            "00:32:54.000",
            "00:07:02.000",
            "00:07:02.000",
            "00:00:20.000",
        ],
    }
