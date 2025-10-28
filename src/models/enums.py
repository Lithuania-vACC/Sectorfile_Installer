"""Enumerations for the application."""

from enum import Enum


class VatsimRating(str, Enum):
    """VATSIM controller ratings."""

    OBS = "OBS"
    S1 = "S1"
    S2 = "S2"
    S3 = "S3"
    C1 = "C1"
    C3 = "C3"
    I1 = "I1"
    I3 = "I3"
    SUP = "SUP"

    @property
    def numeric_value(self) -> int:
        """Get the numeric rating value for EuroScope."""
        ratings = {
            "OBS": 0,
            "S1": 1,
            "S2": 2,
            "S3": 3,
            "C1": 4,
            "C3": 6,
            "I1": 7,
            "I3": 9,
            "SUP": 10,
        }
        return ratings[self.value]
