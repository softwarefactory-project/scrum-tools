# TC and UA toolkit

Some scripts to automate boring tasks as much as possible. You must be
on the Red Hat VPN to run them.

## retro_moderators.py

Randomizes attendees list and assigns each to a retrospective topic.

### Usage

```bash
./retro_moderators.py NAME1 NAME2 ... NAMEn
./retro_moderators.py NAME1,NAME2,...,NAMEn
```

## tc3000.sh

TL;DR just run this script after the retrospective to automate most post
ceremonies actions.

### What it does

* Fetch the retro, review and daily pads
* Fill templates based on the pads contents. The templates are:

  * Mojo blog article: Daily Minutes
  * Mojo blog article: Retrospective
  * Mojo blog article: Review
  * review summary email to openstack-status mailing list
  * review summary email to softwarefactory-dev mailing list (public elements)
  * www.softwarefactory-project.io blog article: Review (public elements)

* Wait for user corrections & validation
* Push final drafts to Mojo, gmail, www.sf code review
* Create a new sprint in taiga
* Create impediments story in new sprint and related epic
* Create Retro actions story and tasks in new sprint and related epic

### What you need to do manually

* Save the etherpads
* Clean the etherpads for the next iteration

### Usage

```./tc3000.sh```

## pads2summaries.py

Fetches our pads and prepares or publishes them to Mojo. Also creates a new
sprint on taiga.

### Usage

```bash
./pads2summaries.py SPRINT_NAME prepare
./pads2summaries.py SPRINT_NAME publish
```

### Limitations

Sadly the Mojo API requires a new OTP password each time it is called.
