"""User configuration models."""

from dataclasses import dataclass, asdict
from typing import Optional

from models import VatsimRating


@dataclass
class UserConfig:
    """User configuration and credentials."""

    name: str = ""
    vatsim_id: str = ""
    vatsim_password: str = ""
    rating: Optional[VatsimRating] = None
    hoppie_code: str = ""

    afv_path: str = ""
    theme_mode: str = "system"  # "light", "dark", or "system"

    def __post_init__(self):
        if not self.afv_path:
            default_path = r"C:\AudioForVATSIM\AudioForVATSIM.exe"
            try:
                with open(default_path):
                    self.afv_path = default_path
            except FileNotFoundError:
                pass

    def is_valid(self) -> bool:
        """Check if all required fields are filled."""
        return bool(
            self.vatsim_id
            and self.vatsim_password
            and self.rating
        )

    def to_dict(self) -> dict:
        data = asdict(self)
        data["rating"] = self.rating.value if self.rating else None
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "UserConfig":
        rating_str = data.get("rating")

        return cls(
            name=data.get("name", ""),
            vatsim_id=data.get("vatsim_id", ""),
            vatsim_password=data.get("vatsim_password", ""),
            rating=VatsimRating(rating_str) if rating_str else None,
            hoppie_code=data.get("hoppie_code", ""),
            afv_path=data.get("afv_path", ""),
            theme_mode=data.get("theme_mode", "system"),
        )
