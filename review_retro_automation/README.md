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

Runs pads2summaries.py interactively, publishes a review summary to www.softwarefactory-project.io

### Usage

```./tc3000.sh```

## pads2summaries.py

Fetches our pads and prepares or publishes them to Mojo.

### Usage

```bash
./pads2summaries.py SPRINT_NAME prepare
./pads2summaries.py SPRINT_NAME publish
```

### Limitations

Sadly the Mojo API requires a new OTP password each time it is called.
