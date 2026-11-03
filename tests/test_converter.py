import pytest
from land.converter import LandAreaConverter

def test_hectare_are_conversion():
    # 1 Hectare = 10,000 sq.m
    area = LandAreaConverter.from_hectare_are(1.0, 0.0)
    assert area.sq_meters == 10000.0
    assert abs(area.acres - 2.471) < 0.01

def test_gunthas_to_acres():
    # 40 Gunthas is exactly 1 Acre
    area = LandAreaConverter.from_acres_gunthas(0.0, 40.0)
    assert abs(area.acres - 1.0) < 0.001
    assert abs(area.sq_meters - 4046.85) < 1.0

def test_bigha_biswa_conversion():
    # 1 Pucca Bigha in North India is ~2529.28 sq.m (~0.625 Acres)
    area = LandAreaConverter.from_bigha_biswa(1.0, 0.0)
    assert abs(area.sq_meters - 2529.28) < 1.0
    assert abs(area.acres - 0.625) < 0.01

    # 20 Biswa = 1 Bigha
    area_biswa = LandAreaConverter.from_bigha_biswa(0.0, 20.0)
    assert abs(area_biswa.bigha - 1.0) < 0.001
