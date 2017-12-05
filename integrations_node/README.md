# Integrations node playbook

This playbook is intended to quickly deploy and manage a node dedicated to integration with 3rd party services used by the team.

So far it supports:

* taiga.io integration with gerrit events, through firehooks
* taiga.io + github synchronization for rdopkg issues

# How to run this playbook

**prerequisite**: make sure you have SSH access to the integrations node.

* Clone this directory on the install server
* modify inventory, projects.json according to your needs
* as root, run:

```bash
ansible-playbook -i inventory -u centos integrations.yml --extra-vars "@project.json"
```
