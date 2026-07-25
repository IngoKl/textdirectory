# -*- coding: utf-8 -*-

"""Console script for textdirectory."""
from email.policy import default
import sys
import os
import click

sys.path.insert(0, os.path.abspath('..'))
from textdirectory import textdirectory
from textdirectory import transformations
import textdirectory.helpers as helpers


available_filters = helpers.get_available_filters()
available_transformations = helpers.get_available_transformations()

@click.command()
@click.option('--directory', help='The directory containing text files', type=str)
@click.option('--output_file', help='The file to aggregate to', type=str)
@click.option('--filetype', help='The file type to look for.', default='txt', type=str)
@click.option('--encoding', help='The encoding of the files.', default='utf8', type=str)
@click.option('--recursive', help='Recursion', type=bool)
@click.option('--disable_tqdm', help='Disable progress bar', default=False, type=bool)
@click.option('--filters', help=f'The filters you want to apply. Filters: {available_filters}', type=str)
@click.option('--transformations', help=f'The transformations you want to apply. '
                                        f'Tranformations: {available_transformations}', type=str)
def main(directory, output_file, filetype, encoding, recursive, disable_tqdm, filters, transformations):
    """Console script for textdirectory."""
    if not directory:
        click.echo('Welcome to TextDirectory!\nRun textdirectory --help for further information.')
        click.echo('Example (Basic Aggregation): textdirectory --directory testdata --output_file aggregated.txt --filetype txt')
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

    if disable_tqdm or not output_file:
        disable_tqdm = True
    else:
        disable_tqdm = False

    try:
        td = textdirectory.TextDirectory(directory=directory, encoding=encoding, disable_tqdm=disable_tqdm)
        td.load_files(recursive=recursive, filetype=filetype)
    except NotADirectoryError:
        click.echo('The directory could not be found.')
        sys.exit()    
    except FileNotFoundError:
        click.echo('There seem to be no files. Maybe you want to run with --recursive True.')
        sys.exit()
        
    if filters and len(filters_list) > 0:
        td.run_filters(filters_list)

    if transformations and len(transformations_list) > 0:
        for transformation in transformations_list:
            td.stage_transformation(transformation)

    if output_file:
        td.print_aggregation()
        td.aggregate_to_file(output_file)
    else:
        print(td.aggregate_to_memory())

    return 0


if __name__ == "__main__":
    sys.exit(main())
