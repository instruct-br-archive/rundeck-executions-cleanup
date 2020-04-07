import pytest
import vcr as vcr_lib

from rundeck_executions_cleanup.rundeck_api import RundeckAPI

vcr = vcr_lib.VCR(
    serializer='json',
    cassette_library_dir='tests/fixtures/cassettes',
    record_mode='once',
    match_on=['uri', 'method'],
)


@pytest.fixture
def client():
    return RundeckAPI(
        base_url='http://172.20.0.112:4440/api',
        api_version=34,
        auth_token='gSe7qynWEPNa4eEdyja6PXpKR3obDNlx',
        max_executions_for_request=1000,
    )


@vcr.use_cassette()
def test_get_projects(client):
    project_names = client.get_project_names()

    assert set(project_names) == set(['teste'])


@vcr.use_cassette()
def test_get_job_ids(client):
    job_ids = client.get_job_ids_for_project('teste')
    expected_ids = [
        '5fbf41d5-14a3-4dcf-85b6-7746f1e50f99',
        '6000c4d1-64be-4052-9bf8-701920b368b4',
        '0be76142-7f33-427b-a5a5-84efb199013a',
    ]

    assert set(job_ids) == set(expected_ids)


@vcr.use_cassette()
def test_get_executions_for_job(client):
    job_id = '6000c4d1-64be-4052-9bf8-701920b368b4'
    expected_data = [88, 108]

    executions = client.get_executions_for_job(job_id=job_id)

    assert set(executions) == set(expected_data)


@vcr.use_cassette()
def test_get_executions_for_project_with_date_filter(client):
    filters = {'olderFilter': '0d'}
    expected_data = [88, 92, 108]

    executions = client.get_executions_for_project(
        project_name='teste', filters=filters
    )

    assert len(executions) == 3
    assert set(executions) == set(expected_data)


@vcr.use_cassette()
def test_delete_execution(client):
    execution_id = 84

    assert client.delete_execution(execution_id=execution_id) == 204


@vcr.use_cassette()
def test_bulk_delete_executions(client):
    execution_ids = [96, 100, 104]

    assert client.bulk_delete_executions(execution_ids=execution_ids) == 200
