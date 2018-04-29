# -*- coding: utf-8 -*-

"""Console script for textdirectory."""
import sys
import os
import click

sys.path.insert(0, os.path.abspath('..'))
from textdirectory import textdirectory
from textdirectory import transformations


available_filters = [filter for filter in dir(textdirectory.TextDirectory) if 'filter_by' in filter]
available_transformations = [transformation for transformation in dir(transformations)
                             if 'transformation' in transformation]

@click.command()
@click.option('--directory', help='The directory containing text files', type=str)
@click.option('--output_file', help='The file to aggregate to', type=str)
@click.option('--filetype', help='The file type to look for.', default='txt', type=str)
@click.option('--recursive', help='Recursion', type=bool)
@click.option('--filters', help=f'The filters you want to apply. Filters: {available_filters}', type=str)
@click.option('--transformations', help=f'The transformations you want to apply. '
                                        f'Tranformations: {available_transformations}', type=str)
def main(directory, output_file, filetype, recursive, filters, transformations):
    """Console script for textdirectory."""
    if not directory or not output_file:
        click.echo('Welcome to TextDirectory!\nRun textdirectory --help for further information.')
        sys.exit()

    if filters:
        filters_list = []
        filters = filters.split('/')
        for filter in filters:
            filters_list.append(filter.split(','))

    if transformations:
        transformations_list = []
        transformations = transformations.split('/')
        for transformation in transformations:
            transformations_list.append(transformation.split(','))

    td = textdirectory.TextDirectory(directory=directory)
    td.load_files(recursive, filetype)
    if filters and len(filters_list) > 0:
        td.run_filters(filters_list)
    if transformations and len(transformations_list) > 0:
        for transformation in transformations_list:
            td.stage_transformation(transformation)
    td.print_aggregation()
    td.aggregate_to_file(output_file)

    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
