# rio-chop

<p align="center">
  <em>🔪🔪🔪 Split a dataset into smaller COGs</em>
</p>
<p align="center">
  <a href="https://github.com/cogeotiff/rio-chop/actions?query=workflow%3ACI" target="_blank">
      <img src="https://github.com/cogeotiff/rio-chop/workflows/CI/badge.svg" alt="Test">
  </a>
  <a href="https://codecov.io/gh/cogeotiff/rio-chop" target="_blank">
      <img src="https://codecov.io/gh/cogeotiff/rio-chop/branch/master/graph/badge.svg" alt="Coverage">
  </a>
  <a href="https://pypi.org/project/rio-chop" target="_blank">
      <img src="https://img.shields.io/pypi/v/rio-chop?color=%2334D058&label=pypi%20package" alt="Package version">
  </a>
  <a href="https://pypistats.org/packages/rio-chop" target="_blank">
      <img src="https://img.shields.io/pypi/dm/rio-chop.svg" alt="Downloads">
  </a>
  <a href="https://github.com/cogeotiff/rio-chop/blob/master/LICENSE" target="_blank">
      <img src="https://img.shields.io/github/license/cogeotiff/rio-chop.svg" alt="Downloads">
  </a>
</p>

---

**Source Code**: <a href="https://github.com/cogeotiff/rio-chop" target="_blank">https://github.com/cogeotiff/rio-chop</a>

---

`rio-chop` is a simple [rasterio](https://github.com/rasterio/rasterio) plugin for creating smaller COGs from an input dataset.

## Installation

```bash
$ pip install pip -U

# From Pypi
$ pip install rio-chop

# Or from source
$ pip install git+http://github.com/cogeotiff/rio-chop
```

## GDAL >3.1

`rio-cho` is using the new `COG` driver, thus GDAL >=3.1 is required.

## Usage
```
$ rio chop --help
Usage: rio chop [OPTIONS] INPUT

  Split a dataset into smaller COGs

Options:
  --prefix TEXT                   output file prefix.  [required]
  -w, --width INTEGER             Chop width (default: 5000px)
  -h, --height INTEGER            Chop height (default: 5000px)
  -p, --cog-profile [jpeg|webp|zstd|lzw|deflate|packbits|lzma|lerc|lerc_deflate|lerc_zstd|raw]
                                  CloudOptimized GeoTIFF profile (default:
                                  deflate).

  --blocksize INTEGER             Overwrite profile's tile size.
  --overview-level INTEGER        Overview level (if not provided, appropriate
                                  overview level will be selected until the
                                  smallest overview is smaller than the value
                                  of the internal blocksize)

  --overview-resampling [nearest|bilinear|cubic|cubic_spline|lanczos|average|mode|gauss|rms]
                                  Overview creation resampling algorithm
                                  (default: nearest).

  --overview-blocksize TEXT       Overview's internal tile size (default
                                  defined by GDAL_TIFF_OVR_BLOCKSIZE env or
                                  128)

  -w, --web-optimized             Create COGEO optimized for Web.
  --zoom-level-strategy [lower|upper|auto]
                                  Strategy to determine zoom level. (default:
                                  auto).

  --aligned-levels INTEGER        Number of overview levels for which GeoTIFF
                                  tile and tiles defined in the tiling scheme
                                  match.

  -r, --resampling [nearest|bilinear|cubic|cubic_spline|lanczos|average|mode|max|min|med|q1|q3|sum|rms]
                                  Resampling algorithm (default: nearest).
                                  Will only be applied with the `--web-
                                  optimized` option.

  --co, --profile NAME=VALUE      Driver specific creation options. See the
                                  documentation for the selected output driver
                                  for more information.

  --config NAME=VALUE             GDAL configuration options.
  --help                          Show this message and exit.
```

### Examples

```
$ rio chop world_cog.tif --prefix "world" -p jpeg --blocksize 256
  [####################################]  100%

$ ls -1 world*
world_0_0.tif
world_0_10000.tif
world_0_5000.tif
world_10000_0.tif
world_10000_10000.tif
world_10000_5000.tif
world_15000_0.tif
world_15000_10000.tif
world_15000_5000.tif
world_20000_0.tif
world_20000_10000.tif
world_20000_5000.tif
world_5000_0.tif
world_5000_10000.tif
world_5000_5000.tif
world_cog.tif
```

## Contribution & Development

See [CONTRIBUTING.md](https://github.com/cogeotiff/rio-chop/blob/main/CONTRIBUTING.md)

## Changes

See [CHANGES.md](https://github.com/cogeotiff/rio-chop/blob/main/CHANGES.md).

## License

See [LICENSE](https://github.com/cogeotiff/rio-chop/blob/main/LICENSE)

