from kandor.widgets.temporal_kg import _esm_source


def test_widget_esm_is_loaded_from_package_resources() -> None:
    source = _esm_source()

    assert "d3" in source
