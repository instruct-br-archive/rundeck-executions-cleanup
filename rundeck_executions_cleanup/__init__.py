import logging

import click
import click_log

from rundeck_executions_cleanup.rundeck_api import RundeckAPI

__version__ = '0.1.1'

LOGGER = logging.getLogger(__name__)
click_log.basic_config(LOGGER)


@click.command()
@click.option(
    '--api_token', required=True, type=str, help='Rundeck API token.',
)
@click.option('--api_url', required=True, type=str, help='Rundeck API url.')
@click.option(
    '--api_version', required=True, type=int, help='Rundeck API version.',
)
@click.option(
    '--older_execution_days',
    required=True,
    type=str,
    help=(
        'Days that previous executions will be deleted. '
        'Example: 30d. Check olderFilter in Rundeck documentation for more '
        'details: '
        'https://docs.rundeck.com/docs/api/rundeck-api.html#execution-query'
    ),
)
@click.option(
    '--projects',
    default='all',
    type=str,
    help='Rundeck projects that will delete executions.',
)
@click.option(
    '--max_executions_for_request',
    default=1000,
    help='Maximum number of API requests',
    type=int,
)
@click_log.simple_verbosity_option(LOGGER)
def main(
    api_token,
    api_url,
    api_version,
    max_executions_for_request,
    older_execution_days,
    projects,
):
    rapi = RundeckAPI(
        base_url=api_url,
        api_version=api_version,
        auth_token=api_token,
        max_executions_for_request=max_executions_for_request,
    )
    LOGGER.info(f'Connect Rundeck API {api_url} version {api_version}.')

    if projects == 'all':
        LOGGER.warning(
            'No projects was specified, so cleaning will be in all Rundeck projects.'  # noqa: E501
        )
        projects = rapi.get_project_names()
    else:
        projects = projects.split(',')
        for project in projects:
            if not rapi.get_project(project):
                return
    LOGGER.info(
        f'Executions of {older_execution_days} ago will be deleted in the projects: {projects}.'  # noqa: E501
    )

    execution_ids = 0
    for project in projects:
        execution_ids = rapi.get_executions_for_project(
            project_name=project,
            filters={'olderFilter': older_execution_days},
        )

        rapi.bulk_delete_executions(execution_ids=execution_ids)
    LOGGER.info(f'{str(len(execution_ids))} executions have been deleted.')
