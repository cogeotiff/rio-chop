"""Chop."""

import math
import os
import sys
import warnings

import click
import morecantile
import rasterio
from rasterio.dtypes import _gdal_typename
from rasterio.enums import ColorInterp
from rasterio.enums import Resampling as ResamplingEnums
from rasterio.env import GDALVersion
from rasterio.rio import options
from rasterio.shutil import copy
from rasterio.warp import SUPPORTED_RESAMPLING as WarpResampling
from rasterio.windows import Window
from rio_cogeo import cog_profiles, utils

OverviewResampling = [r for r in ResamplingEnums if r.value < 8]
if GDALVersion.runtime().at_least("3.3"):
    OverviewResampling.append(ResamplingEnums.rms)


def dims(total, chop):
    """Given a total number of pixels, chop into equal chunks.

    Last one gets truncated so that sum of sizes == total.
    yeilds (offset, size) tuples
    >>> list(dims(512, 256))
    [(0, 256), (256, 256)]
    >>> list(dims(502, 256))
    [(0, 256), (256, 246)]
    >>> list(dims(522, 256))
    [(0, 256), (256, 256), (512, 10)]
    """
    for a in range(int(math.ceil(total / chop))):
        offset = a * chop
        diff = total - offset
        if diff <= chop:
            size = diff
        else:
            size = chop
        yield offset, size


@click.command()
@options.file_in_arg
@click.option(
    "--prefix", type=str, required=True, help="output file prefix.",
)
@click.option(
    "--width", "-w", type=int, default=5000, help="Chop width (default: 5000px)",
)
@click.option(
    "--height", "-h", type=int, default=5000, help="Chop height (default: 5000px)"
)
@click.option(
    "--cog-profile",
    "-p",
    "cogeo_profile",
    type=click.Choice(cog_profiles.keys(), case_sensitive=False),
    default="deflate",
    help="CloudOptimized GeoTIFF profile (default: deflate).",
)
@click.option("--blocksize", type=int, help="Overwrite profile's tile size.")
@click.option(
    "--overview-level",
    type=int,
    help="Overview level (if not provided, appropriate overview level will be "
    "selected until the smallest overview is smaller than the value of the "
    "internal blocksize)",
)
@click.option(
    "--overview-resampling",
    help="Overview creation resampling algorithm (default: nearest).",
    type=click.Choice([it.name for it in OverviewResampling]),
    default="nearest",
)
@click.option(
    "--overview-blocksize",
    default=lambda: os.environ.get("GDAL_TIFF_OVR_BLOCKSIZE", 128),
    help="Overview's internal tile size (default defined by "
    "GDAL_TIFF_OVR_BLOCKSIZE env or 128)",
)
@click.option(
    "--web-optimized", "-w", is_flag=True, help="Create COGEO optimized for Web."
)
@click.option(
    "--zoom-level-strategy",
    type=click.Choice(["lower", "upper", "auto"], case_sensitive=False),
    default="auto",
    help="Strategy to determine zoom level. (default: auto).",
)
@click.option(
    "--aligned-levels",
    type=int,
    help="Number of overview levels for which GeoTIFF tile and tiles defined in the tiling scheme match.",
)
@click.option(
    "--resampling",
    "-r",
    help="Resampling algorithm (default: nearest). Will only be applied with the `--web-optimized` option.",
    type=click.Choice([it.name for it in WarpResampling]),
    default="nearest",
)
@options.creation_options
@click.option(
    "--config",
    "config",
    metavar="NAME=VALUE",
    multiple=True,
    callback=options._cb_key_val,
    help="GDAL configuration options.",
)
def chop(
    input,
    prefix,
    width,
    height,
    cogeo_profile,
    blocksize,
    overview_level,
    overview_resampling,
    overview_blocksize,
    web_optimized,
    zoom_level_strategy,
    aligned_levels,
    resampling,
    creation_options,
    config,
):
    """Chop and COG"""
    output_profile = cog_profiles.get(cogeo_profile)
    output_profile.update(dict(BIGTIFF=os.environ.get("BIGTIFF", "IF_SAFER")))
    if creation_options:
        output_profile.update(creation_options)

    if blocksize:
        output_profile["blockxsize"] = blocksize
        output_profile["blockysize"] = blocksize

    if web_optimized:
        overview_blocksize = blocksize or 512

    config.update(
        dict(
            GDAL_NUM_THREADS="ALL_CPUS",
            GDAL_TIFF_INTERNAL_MASK=os.environ.get("GDAL_TIFF_INTERNAL_MASK", True),
            GDAL_TIFF_OVR_BLOCKSIZE=str(overview_blocksize),
        )
    )

    tms = morecantile.tms.get("WebMercatorQuad")

    tilesize = min(int(output_profile["blockxsize"]), int(output_profile["blockysize"]))

    with rasterio.Env(**config):
        with rasterio.open(input) as src:
            w, h = src.meta["width"], src.meta["height"]

            mask = utils.has_mask_band(src)

            winds = [
                (coff, wd, roff, ht)
                for roff, ht in dims(h, height)
                for coff, wd in dims(w, width)
            ]
            with click.progressbar(
                winds, length=len(winds), file=sys.stderr, show_percent=True
            ) as blocks:
                for col_off, w, row_off, h in blocks:

                    window = Window(col_off, row_off, w, h)
                    data = src.read(window=window)

                    # We are using GDAL MEM driver to create a new dataset from the numpy array
                    # ref: https://github.com/rasterio/rasterio/blob/master/rasterio/_io.pyx#L1946-L1955
                    info = {
                        "DATAPOINTER": data.__array_interface__["data"][0],
                        "PIXELS": w,
                        "LINES": h,
                        "BANDS": src.count,
                        "DATATYPE": _gdal_typename(data.dtype.name),
                    }
                    dataset_options = ",".join(
                        f"{name}={val}" for name, val in info.items()
                    )
                    datasetname = f"MEM:::{dataset_options}"

                    with rasterio.open(datasetname, "r+") as w_dst:
                        w_dst.transform = src.window_transform(window)
                        w_dst.crs = src.crs
                        if src.colorinterp[0] is ColorInterp.palette:
                            try:
                                w_dst.write_colormap(1, src.colormap(1))
                            except ValueError:
                                pass

                        if mask:
                            w_dst.write_mask(
                                src.dataset_mask(window=window).astype("uint8")
                            )

                        w_dst.update_tags(**src.tags())
                        w_dst._set_all_scales([src.scales[b - 1] for b in src.indexes])
                        w_dst._set_all_offsets(
                            [src.offsets[b - 1] for b in src.indexes]
                        )

                        output_profile["driver"] = "COG"
                        if web_optimized:
                            output_profile["TILING_SCHEME"] = (
                                "GoogleMapsCompatible"
                                if tms.identifier == "WebMercatorQuad"
                                else tms.identifier
                            )

                            if mask and output_profile.get("compress", "") != "JPEG":
                                warnings.warn(
                                    "With GDAL COG driver, mask band will be translated to an alpha band."
                                )

                        output_profile["zoom_level_strategy"] = zoom_level_strategy
                        output_profile["overview_resampling"] = overview_resampling
                        output_profile["warp_resampling"] = resampling
                        if aligned_levels is not None:
                            output_profile["aligned_levels"] = aligned_levels

                        output_profile["blocksize"] = tilesize
                        output_profile.pop("blockxsize", None)
                        output_profile.pop("blockysize", None)
                        output_profile.pop("tiled", None)
                        output_profile.pop("interleave", None)
                        output_profile.pop("photometric", None)

                        copy(
                            w_dst, f"{prefix}_{col_off}_{row_off}.tif", **output_profile
                        )
