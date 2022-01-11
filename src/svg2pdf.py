"""
Based on https://github.com/Kozea/CairoSVG/issues/200#issuecomment-709015462
"""
import sys
import os

import cairocffi
import click
from cairosvg.parser import Tree
from cairosvg.surface import PDFSurface


VERSION = "0.0.1"


class RecordingPDFSurface(PDFSurface):
    surface_class = cairocffi.RecordingSurface

    def _create_surface(self, width, height):
        cairo_surface = cairocffi.RecordingSurface(
            cairocffi.CONTENT_COLOR_ALPHA, (0, 0, width, height)
        )
        return cairo_surface, width, height


def convert_list(urls, write_to, dpi=72):
    surface = cairocffi.PDFSurface(write_to, 1, 1)
    context = cairocffi.Context(surface)
    for url in urls:
        image_surface = RecordingPDFSurface(Tree(url=url), None, dpi)
        surface.set_size(image_surface.width, image_surface.height)
        context.set_source_surface(image_surface.cairo, 0, 0)
        context.paint()
        surface.show_page()
    surface.finish()


@click.command()
@click.argument("input_files", nargs=-1, type=str)
@click.option("--output", "-o", type=str, help="Specify output file")
@click.option("--dpi", "-d", type=int, default=72, help="Specify DPI (default 72)")
@click.option("--version", "-v", is_flag=True, help="Display version number")
def run(input_files, output, dpi, version):
    if version:
        print(f"{os.path.basename(__file__)} version {VERSION}")
        return
    if len(input_files) == 0:
        print("No input file(s) specified")
        sys.exit(1)
    input_ok = True
    for input_file in input_files:
        if not os.path.exists(input_file):
            input_ok = False
            print(f"Input file {input_file} cannot be read")
    if not input_ok:
        sys.exit(1)
    if not output:
        print("No output file specified")
        sys.exit(1)
    output_dir = os.path.dirname(output) or "."
    if not os.access(output_dir, os.W_OK):
        print(f"Output file {output} cannot be written")
        sys.exit(1)
    convert_list(input_files, output, dpi)


if __name__ == "__main__":
    run()
