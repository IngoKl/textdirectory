"""Console script for textdirectory."""

import sys
from typing import Any

import click

from textdirectory import helpers, textdirectory
from textdirectory import transformations as td_transformations

available_filters = helpers.get_available_filters()
available_transformations = helpers.get_available_transformations()


@click.command()
@click.version_option(package_name='textdirectory')
@click.option('--directory', help='The directory containing text files', type=str)
@click.option('--output_file', help='The file to aggregate to', type=str)
@click.option('--filetype', help='The file type to look for.', default='txt', type=str)
@click.option('--encoding', help='The encoding of the files.', default='utf8', type=str)
@click.option('--recursive', help='Recursion', type=bool)
@click.option('--disable_tqdm', help='Disable progress bar', default=False, type=bool)
@click.option('--filters', help=f'The filters you want to apply. Filters: {available_filters}', type=str)
@click.option(
    '--transformations',
    help=f'The transformations you want to apply. Tranformations: {available_transformations}',
    type=str,
)
def main(
    directory: str | None,
    output_file: str | None,
    filetype: str,
    encoding: str,
    recursive: bool,
    disable_tqdm: bool,
    filters: str | None,
    transformations: str | None,
) -> int:
    """Console script for textdirectory."""
    if not directory:
        click.echo('Welcome to TextDirectory!\nRun textdirectory --help for further information.')
        click.echo(
            'Example (Basic Aggregation): textdirectory --directory testdata --output_file aggregated.txt --filetype txt'
        )
        sys.exit()

    if filters:
        filters_list: list[list[Any]] = []
        for filter in filters.split('/'):
            name, *filter_args = filter.split(',')

            # Coerce string arguments (e.g. '100') to the types the filter expects
            filter_method = getattr(textdirectory.TextDirectory, name, None)
            if filter_method is not None and name in available_filters:
                filter_args = helpers.coerce_args_by_signature(filter_method, filter_args)

            filters_list.append([name, *filter_args])

    if transformations:
        transformations_list: list[list[Any]] = []
        for transformation in transformations.split('/'):
            name, *transformation_args = transformation.split(',')

            # Coerce string arguments (e.g. 'False') to the types the transformation expects
            transformation_function = getattr(td_transformations, name, None)
            if transformation_function is not None and name in available_transformations:
                transformation_args = helpers.coerce_args_by_signature(transformation_function, transformation_args)

            transformations_list.append([name, *transformation_args])

    if disable_tqdm or not output_file:
        disable_tqdm = True
    else:
        disable_tqdm = False

    try:
        td = textdirectory.TextDirectory(directory=directory, encoding=encoding, disable_tqdm=disable_tqdm)
        td.load_files(recursive=recursive, filetype=filetype)
    except NotADirectoryError:
        click.echo('The directory could not be found.')
        sys.exit(1)
    except FileNotFoundError:
        click.echo('There seem to be no files. Maybe you want to run with --recursive True.')
        sys.exit(1)

    try:
        if filters and len(filters_list) > 0:
            td.run_filters(filters_list)

        if transformations and len(transformations_list) > 0:
            for staged_transformation in transformations_list:
                td.stage_transformation(staged_transformation)
    except NameError as e:
        click.echo(str(e))
        sys.exit(1)

    if output_file:
        td.print_aggregation()
        td.aggregate_to_file(output_file)
    else:
        click.echo(td.aggregate_to_memory())

    return 0


if __name__ == '__main__':
    sys.exit(main())
