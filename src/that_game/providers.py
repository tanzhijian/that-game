"""Providers for that-game.

This module contains the implementations of the providers
that are used to fetch data for that-game.
"""

from ._providers.skillcorner import skillcorner
from ._providers.sportec import sportec
from ._providers.statsbomb import statsbomb

__all__ = ("statsbomb", "sportec", "skillcorner")
