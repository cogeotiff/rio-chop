"""tests rio_chop.cli."""

import os

import rasterio
from rio_cogeo import cog_validate, utils

from rio_chop.scripts.cli import chop

PREFIX = os.path.join(os.path.dirname(__file__), "fixtures")


def test_rio_chop_cli(runner):
    """Should work as expected."""
    with runner.isolated_filesystem():
        src_path = os.path.join(PREFIX, "image.tif")
        result = runner.invoke(
            chop,
            [
                src_path,
                "--prefix",
                "test",
                "--width",
                "500",
                "--height",
                "500",
                "--blocksize",
                "256",
            ],
        )
        assert not result.exception
        assert result.exit_code == 0
        assert os.path.exists("test_0_0.tif")
        assert os.path.exists("test_0_500.tif")
        assert os.path.exists("test_500_0.tif")
        assert os.path.exists("test_500_500.tif")

        # make sure we create valid COG
        assert cog_validate("test_500_500.tif")

    # Colormap
    with runner.isolated_filesystem():
        src_path = os.path.join(PREFIX, "image_colormap.tif")
        result = runner.invoke(
            chop,
            [
                src_path,
                "--prefix",
                "test_colormap",
                "--width",
                "500",
                "--height",
                "500",
                "--blocksize",
                "256",
            ],
        )
        assert not result.exception
        assert result.exit_code == 0
        assert os.path.exists("test_colormap_0_0.tif")
        assert os.path.exists("test_colormap_0_500.tif")
        assert os.path.exists("test_colormap_500_0.tif")
        assert os.path.exists("test_colormap_500_500.tif")

        # make sure we create valid COG
        assert cog_validate("test_colormap_500_500.tif")

        with rasterio.open(src_path) as src, rasterio.open(
            "test_colormap_500_500.tif"
        ) as cog:
            assert cog.colormap(1) == src.colormap(1)
            assert cog.crs == src.crs

    # Tags
    with runner.isolated_filesystem():
        src_path = os.path.join(PREFIX, "image_tags.tif")
        result = runner.invoke(
            chop,
            [
                src_path,
                "--prefix",
                "test_tags",
                "--width",
                "500",
                "--height",
                "500",
                "--blocksize",
                "256",
            ],
        )
        assert not result.exception
        assert result.exit_code == 0
        assert os.path.exists("test_tags_0_0.tif")
        assert os.path.exists("test_tags_0_500.tif")
        assert os.path.exists("test_tags_500_0.tif")
        assert os.path.exists("test_tags_500_500.tif")

        # make sure we create valid COG
        assert cog_validate("test_tags_0_0.tif")

        with rasterio.open(src_path) as src, rasterio.open("test_tags_0_0.tif") as cog:
            assert cog.tags()["DatasetName"] == cog.tags()["DatasetName"]

    with runner.isolated_filesystem():
        src_path = os.path.join(PREFIX, "image.tif")
        result = runner.invoke(
            chop,
            [
                src_path,
                "--prefix",
                "test_web",
                "--width",
                "500",
                "--height",
                "500",
                "--blocksize",
                "256",
                "-w",
            ],
        )
        assert not result.exception
        assert result.exit_code == 0
        assert os.path.exists("test_web_0_0.tif")
        assert os.path.exists("test_web_0_500.tif")
        assert os.path.exists("test_web_500_0.tif")
        assert os.path.exists("test_web_500_500.tif")

        # make sure we create valid COG
        assert cog_validate("test_web_500_500.tif")

        with rasterio.open("test_web_500_500.tif") as cog:
            assert cog.crs.to_epsg() == 3857

    with runner.isolated_filesystem():
        src_path = os.path.join(PREFIX, "image_rgb_mask.tif")
        result = runner.invoke(
            chop,
            [
                src_path,
                "--prefix",
                "test_mask",
                "--width",
                "500",
                "--height",
                "500",
                "--blocksize",
                "256",
                "-p",
                "jpeg",
            ],
        )
        assert not result.exception
        assert result.exit_code == 0
        assert os.path.exists("test_mask_0_0.tif")
        assert os.path.exists("test_mask_0_500.tif")
        assert os.path.exists("test_mask_500_0.tif")
        assert os.path.exists("test_mask_500_500.tif")

        # make sure we create valid COG
        assert cog_validate("test_mask_500_500.tif")

        with rasterio.open("test_mask_500_500.tif") as cog:
            assert utils.has_mask_band(cog)
            assert cog.profile["compress"] == "jpeg"
