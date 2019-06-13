#!/usr/bin/env python

#  Copyright 2019 Palo Alto Networks, Inc
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}


DOCUMENTATION = '''
---
module: panos_application_group
short_description: create an application group
description:
    - Create an application group
author: "Netzer Rom (@pixelicous)"
version_added: "2.3"
requirements:
    - pan-python can be obtained from PyPI U(https://pypi.python.org/pypi/pan-python)
    - pandevice can be obtained from PyPI U(https://pypi.python.org/pypi/pandevice)
notes:
    - Panorama is supported.
    - Checkmode is supported.
extends_documentation_fragment:
    - panos.transitional_provider
    - panos.vsys
    - panos.device_group
    - panos.state
options:
    name:
        description:
            - name of the application group
        required: true
    applications:
        description:
            - List of applications in the group
        type: list
    commit:
        description:
            - commit if changed
        default: True
        type: bool
'''


EXAMPLES = '''
- name: Create application group 'app-group'
  panos_application_group:
    provider: '{{ provider }}'
    name: 'app-group'
    applications: ["dns","paloalto-apreture"]

- name: Remove application group 'app-group'
  panos_application_group:
    provider: '{{ provider }}'
    name: 'app-group'
    applications: ["dns","paloalto-apreture"]
    state: 'absent'
'''

RETURN = '''
# Default return values
'''


from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.network.panos.panos import get_connection


try:
    from pandevice.objects import ApplicationGroup
    from pandevice.errors import PanDeviceError
except ImportError:
    pass


def main():
    helper = get_connection(
        vsys=True,
        device_group=True,
        with_classic_provider_spec=True,
        with_state=True,
        argument_spec=dict(
            name=dict(type='str', required=True),
            applications=dict(type="list", required=True),
            commit=dict(type='bool', default=True)
        ),
    )

    module = AnsibleModule(
        argument_spec=helper.argument_spec,
        required_one_of=helper.required_one_of,
        supports_check_mode=True
    )

    # Verify libs are present, build the pandevice object tree.
    parent = helper.get_pandevice_parent(module)

    spec = {
        'name': module.params['name'],
        'value': module.params['applications'],
    }

    # Other info.
    commit = module.params['commit']

    # Retrieve current profiles.
    try:
        listing = ApplicationGroup.refreshall(parent, add=False)
    except PanDeviceError as e:
        module.fail_json(msg='Failed refresh: {0}'.format(e))

    obj = ApplicationGroup(**spec)
    parent.add(obj)

    # Apply the state.
    changed = helper.apply_state(obj, listing, module)

    # Optional commit.
    if changed and commit:
        helper.commit(module)

    module.exit_json(changed=changed, msg='done')


if __name__ == '__main__':
    main()

