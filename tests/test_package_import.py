import kandor


def test_package_exports_public_api() -> None:
    assert "WorldBuilder" in kandor.__all__
    assert "SimulationRunner" in kandor.__all__
