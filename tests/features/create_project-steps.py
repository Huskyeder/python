# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2014 BigML
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import os
import time
import json
from datetime import datetime, timedelta
from urllib import urlencode
from lettuce import step, world

from bigml.api import HTTP_CREATED, HTTP_ACCEPTED
from bigml.api import FINISHED
from bigml.api import FAULTY
from bigml.api import UPLOADING
from bigml.api import get_status


@step(r'I create a project with name "(.*)"$')
def i_create_project(step, name):
    resource = world.api.create_project({"name": name})
    # update status
    world.status = resource['code']
    world.location = resource['location']
    world.project = resource['object']
    # save reference
    world.projects.append(resource['resource'])


@step(r'I wait until the project status code is either (\d) or (\d) less than (\d+)')
def wait_until_project_status_code_is(step, code1, code2, secs):
    start = datetime.utcnow()
    step.given('I get the project "{id}"'.format(id=world.project['resource']))
    status = get_status(world.project)
    while (status['code'] != int(code1) and
           status['code'] != int(code2)):
        time.sleep(3)
        assert datetime.utcnow() - start < timedelta(seconds=int(secs))
        step.given('I get the project "{id}"'.format(id=world.project['resource']))
        status = get_status(world.project)
    assert status['code'] == int(code1)


@step(r'I wait until the project is ready less than (\d+)')
def the_project_is_finished(step, secs):
    wait_until_project_status_code_is(step, FINISHED, FAULTY, secs)


@step(r'I update the project name with "(.*)"')
def i_update_project_name_with(step, name=""):
    resource = world.api.update_project(world.project.get('resource'), {"name": name})
    world.status = resource['code']
    assert world.status == HTTP_ACCEPTED
    world.project = resource['object']


@step(r'I check that the project\'s name is "(.*)"')
def i_check_project_name(step, name=""):
    updated_name = world.project.get("name", "")
    if updated_name == name:
        assert True
    else:
        assert False, "Project name: %s, expected name: %s" % (updated_name, name)
