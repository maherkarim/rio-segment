"""
Created on Thu Feb  2 12:09:18 2017

Watershed segmentation and graph based merging.

@author: Matthew Parker
"""

import click
from rio_segment import (
       sort_filetype,  edges_from_raster_and_shp,
       watershed_segment, rag_merge_threshold, write_segments
       )


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help', '--usage'])


@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument('input-files', nargs=-1, required=True, metavar='INPUTS...')
@click.argument('output-shapefile', nargs=1, required=True, metavar='OUTPUT')
@click.option('--no-data', default=None, required=False, type=int,
              help='Overrides nodata value for raster files')
@click.option('--shapefile-weight', required=False, default=150,
              help=('Weighting to give edges from shapefile compared to edges'
                    'detected from rasters. A value between 0 and 255'))
@click.option('--fill-holes/--no-fill-holes', required=False, default=False,
              help=('Try to fill holes in raster layers using info from '
                    'shapefiles. If there is no shapefile input this will '
                    'raise an error. Will not be successful unless there '
                    'are polygons overlapping with the masked region of'
                    'the raster. Default: False'))
@click.option('--size-pen', required=False, default=10,
              help=('Factor to penalise segments by size on merging. Set to '
                    'ero to turn off this behaviour. Default: 10'))
@click.option('--rescale-perc', default=(0, 98), nargs=2, required=False,
              help='Percentiles to rescale each gtiff band to. default: 0 98')
@click.option('--footprint', default=2, required=False,
              help=('Size of footprint for determining seeds '
                    'for watershed segmentation. Default: 2'))
@click.option('--threshold', default=40, required=False,
              help='Percentile threshold to merge segments at. Default: 40')
@click.option('--output-raster/--no-output-raster',
              default=True, required=False,
              help='Output a raster of segments as well as a shapefile')
def segment(input_files, output_shapefile,
            no_data, shapefile_weight, fill_holes,
            size_pen, rescale_perc,
            footprint, threshold, output_raster):
    '''
    Segment an raster or set of rasters using watershed and RAG boundary
    merging. Input is a set of one or more rasters. Shapefiles can also be
    specified in the inputs and are used to inform the segmentation. Output is
    in the form of a single shapefile of segments.
    '''
    input_raster, input_shapefile = sort_filetype(input_files)

    if fill_holes and not input_shapefile:
        raise ValueError('cannot fill raster holes without some shapes')

    edges, mask, crs, meta = edges_from_raster_and_shp(input_raster,
                                                       input_shapefile,
                                                       shapefile_weight,
                                                       fill_holes,
                                                       rescale_perc,
                                                       no_data)
    labels = watershed_segment(edges, footprint)
    refined_labels = rag_merge_threshold(edges, labels, threshold, size_pen)
    write_segments(output_shapefile, refined_labels,
                   mask, crs, meta, output_raster)
    click.echo('complete')

if __name__ == '__main__':
    segment()
