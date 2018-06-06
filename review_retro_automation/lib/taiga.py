#! /usr/bin/env python


# The lib does not cover everything. So we'll do calls the old
# fashioned way
import requests


class TaigaHelper(object):
    def __init__(self, password, user=None, project_slug=None):
        self.user = user or 'SFbot0'
        self.password = password
        self.base_url = 'https://api.taiga.io/api/v1/'
        self.project_slug = project_slug or 'morucci-software-factory'
        self._project_id = None
        self._bearer_token = None

    @property
    def bearer_token(self):
        if not self._bearer_token:
            user_json = {'type': 'normal',
                         'username': self.user,
                         'password': self.password}
            user_info = requests.post(
                self.base_url + 'auth',
                json=user_json,
                headers={'Content-Type': 'application/json'})
            if user_info.status_code >= 400:
                raise Exception('Authentication failure: %s' % user_info.text)
            ui_json = user_info.json()
            self._bearer_token = ui_json['auth_token']
        return self._bearer_token

    @property
    def project_id(self):
        if not self._project_id:
            url = self.base_url + 'resolver?project=%s' % self.project_slug
            project_info = self.get(url=url)
            self._project_id = project_info.json()['project']
        return self._project_id

    def _prepare(self, kwargs):
        token = self.bearer_token
        headers = {'Authorization': 'Bearer %s' % token,
                   'Content-Type': 'application/json'}
        if 'headers' in kwargs:
            kwargs['headers'].update(headers)
        else:
            kwargs['headers'] = headers

    def get(self, **kwargs):
        self._prepare(kwargs)
        return requests.get(**kwargs)

    def post(self, **kwargs):
        self._prepare(kwargs)
        return requests.post(**kwargs)

    def put(self, **kwargs):
        self._prepare(kwargs)
        return requests.put(**kwargs)

    def patch(self, **kwargs):
        self._prepare(kwargs)
        return requests.patch(**kwargs)

    def create_sprint(self, board_name, start, finish):
        sprint_json = {
            "estimated_finish": finish.strftime("%Y-%m-%d"),
            "estimated_start": start.strftime("%Y-%m-%d"),
            "name": board_name,
            "project": self.project_id,
        }
        url = self.base_url + 'milestones'
        return self.post(url=url, json=sprint_json).json()['id']

    def get_epic_id(self, epic):
        url = self.base_url + 'epics?project=%s' % self.project_id
        epics = self.get(url=url)
        e_json = epics.json()
        candidates = [e for e in e_json if e['subject'] == epic]
        if not len(candidates) == 1:
            raise Exception('Wrong amount of results: %s' % len(candidates))
        return (candidates[0]['id'], candidates[0]['ref'])

    def create_user_story(self, title, description, sprint_id):
        url = self.base_url + 'userstories'
        us_json = {'subject': title,
                   'project': self.project_id,
                   'description': description,
                   'milestone': sprint_id}
        result = self.post(url=url, json=us_json)
        result = result.json()
        return result['id'], result['ref']

    def add_task(self, us_id, title, description):
        url = self.base_url + 'tasks'
        task_json = {'subject': title,
                     'description': description,
                     'user_story': us_id,
                     'project': self.project_id}
        return self.post(url=url, json=task_json).json()

    def create_story_in_epic_and_sprint(
            self, epic, title, description, sprint_id):
        epic_id, epic_ref = self.get_epic_id(epic)
        us_id, us_ref = self.create_user_story(title, description, sprint_id)
        url = self.base_url + 'epics/%s/related_userstories' % epic_id
        us_json = {'epic': epic_id,
                   'user_story': us_id}
        self.post(url=url, json=us_json)
        return us_id, us_ref
