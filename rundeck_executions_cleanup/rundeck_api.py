import json
import logging

import requests

LOGGER = logging.getLogger(__name__)


class RundeckAPI:
    def __init__(
        self,
        api_version,
        auth_token,
        base_url,
        max_executions_for_request=1000,
    ):
        self.api_version = api_version
        self.auth_token = auth_token
        self.base_url = base_url
        self.max_executions_for_request = max_executions_for_request
        self.url = f'{self.base_url}/{self.api_version}/'

        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'X-Rundeck-Auth-Token': self.auth_token,
        }

    def _get(self, url_path, params=None):
        return requests.get(
            f'{self.url}{url_path}', headers=self.headers, params=params,
        )

    def _delete(self, url_path):
        return requests.delete(f'{self.url}{url_path}', headers=self.headers)

    def _post(self, url_path, data):
        return requests.post(
            f'{self.url}{url_path}', data=data, headers=self.headers,
        )

    def get_project_names(self):
        response = self._get(url_path='projects')
        if response.status_code == 200:
            return [project['name'] for project in response.json()]

        LOGGER.error('No project created')
        return []

    def get_project(self, name):
        response = self._get(url_path=f'project/{name}/')
        if response.status_code == 200:
            return response.json()

        LOGGER.error('%s project does not exist', name)
        return ''

    def get_job_ids_for_project(self, project_name):
        params = {'project': project_name}
        response = self._get(url_path='jobs', params=params)

        if response.status_code == 200:
            return [job['id'] for job in response.json()]

        LOGGER.error('No jobs for the %s project found', project_name)
        return []

    def get_executions_for_job(self, job_id):
        response = self._get(url_path=f'job/{job_id}/executions/')

        if response.status_code == 200:
            executions = response.json()['executions']
            return [execution['id'] for execution in executions]

        LOGGER.error('No executions for the %s job found', job_id)
        return []

    def get_executions_for_project(self, project_name, filters=None):
        if filters:
            params = filters

        response = self._get(
            url_path=f'project/{project_name}/executions/', params=params,
        )
        if response.status_code == 200:
            executions = response.json()['executions']
            return [execution['id'] for execution in executions]

        LOGGER.error(
            'No executions for the %s project with the parameters %s found',
            project_name,
            filters,
        )
        return []

    def delete_execution(self, execution_id):
        response = self._delete(url_path=f'execution/{execution_id}')

        return response.status_code

    def bulk_delete_executions(self, execution_ids):
        response = self._post(
            url_path='executions/delete/',
            data=json.dumps({'ids': execution_ids}),
        )

        return response.status_code
