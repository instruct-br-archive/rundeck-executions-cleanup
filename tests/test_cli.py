from click.testing import CliRunner

from rundeck_executions_cleanup import main


def test_executions_cleanup_cli(mocker):
    token = 'rundeck123'
    url = 'http://example.com/api'
    version = 34
    older_execution_days = '30d'
    projects = 'rundeck_project,rundeck_test'
    projects_output = projects.split(',')

    mock_bulk_delete_executions = mocker.patch(
        'rundeck_executions_cleanup.rundeck_api.RundeckAPI.bulk_delete_executions'  # noqa: E501
    )
    mock_get_executions_for_project = mocker.patch(
        'rundeck_executions_cleanup.rundeck_api.RundeckAPI.get_executions_for_project'  # noqa: E501
    )
    mock_get_project = mocker.patch(
        'rundeck_executions_cleanup.rundeck_api.RundeckAPI.get_project'
    )
    mock_get_project_names = mocker.patch(
        'rundeck_executions_cleanup.rundeck_api.RundeckAPI.get_project_names'
    )

    mock_bulk_delete_executions.return_value = None
    mock_get_executions_for_project.return_value = [1, 2, 3, 4]
    mock_get_project.return_value = 'rundeck_project'
    mock_get_project_names.return_value = projects

    params = [
        '--api_token',
        token,
        '--api_url',
        url,
        '--api_version',
        version,
        '--older_execution_days',
        older_execution_days,
        '--projects',
        projects,
    ]
    expected_output = (
        f'Connect Rundeck API {url} version {version}.\n'
        f'Executions of {older_execution_days} ago will be deleted in the projects: {projects_output}.\n'  # noqa: E501
        '4 executions have been deleted.\n'
    )

    runner = CliRunner()
    result = runner.invoke(main, params)

    assert result.exit_code == 0
    assert result.output == expected_output
