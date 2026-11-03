import math
from typing import Tuple
from land.models import LandArea

class LandAreaConverter:
    """
    Standardizes regional Indian land measurements across:
    - Hectares & Ares (Maharashtra, Gujarat, Goa)
    - Acres & Gunthas (Karnataka, Maharashtra, Telangana, AP)
    - Bigha & Biswa (UP, Haryana, Punjab, Rajasthan)
    - Square Meters & Square Feet
    """

    SQ_METERS_PER_HECTARE = 10000.0
    SQ_METERS_PER_ARE = 100.0
    SQ_METERS_PER_ACRE = 4046.8564224
    SQ_METERS_PER_GUNTHA = 101.17141056  # 40 Gunthas in 1 Acre
    SQ_METERS_PER_PUCCA_BIGHA = 2529.285264  # Standard UP/North Pucca Bigha (20 Biswa)

    @classmethod
    def from_sq_meters(cls, sq_meters: float) -> LandArea:
        sq_m = max(0.0, float(sq_meters))
        hectares = sq_m / cls.SQ_METERS_PER_HECTARE
        rem_sqm_hec = sq_m % cls.SQ_METERS_PER_HECTARE
        ares = rem_sqm_hec / cls.SQ_METERS_PER_ARE

        acres = sq_m / cls.SQ_METERS_PER_ACRE
        rem_sqm_acre = sq_m % cls.SQ_METERS_PER_ACRE
        gunthas = rem_sqm_acre / cls.SQ_METERS_PER_GUNTHA

        bigha = sq_m / cls.SQ_METERS_PER_PUCCA_BIGHA

        raw = f"{math.floor(hectares)}H {round(ares, 2)}R ({round(acres, 2)} Acres / {round(gunthas, 1)} Gunthas)"

        return LandArea(
            hectares=round(hectares, 4),
            ares=round(ares, 2),
            sq_meters=round(sq_m, 2),
            acres=round(acres, 4),
            gunthas=round(gunthas, 2),
            bigha=round(bigha, 4),
            raw_string=raw
        )

    @classmethod
    def from_hectare_are(cls, hectares: float, ares: float) -> LandArea:
        total_sqm = (float(hectares) * cls.SQ_METERS_PER_HECTARE) + (float(ares) * cls.SQ_METERS_PER_ARE)
        return cls.from_sq_meters(total_sqm)

    @classmethod
    def from_acres_gunthas(cls, acres: float, gunthas: float) -> LandArea:
        total_sqm = (float(acres) * cls.SQ_METERS_PER_ACRE) + (float(gunthas) * cls.SQ_METERS_PER_GUNTHA)
        return cls.from_sq_meters(total_sqm)

    @classmethod
    def from_bigha_biswa(cls, bigha: float, biswa: float) -> LandArea:
        total_bigha = float(bigha) + (float(biswa) / 20.0)
        total_sqm = total_bigha * cls.SQ_METERS_PER_PUCCA_BIGHA
        return cls.from_sq_meters(total_sqm)
