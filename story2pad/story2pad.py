#!/usr/bin/env python
# Licensed under the Apache License, Version 2.0

import argparse
import pickle
import re
import os

import requests

from pysflib.sfauth import get_cookie
from pysflib.sfstoryboard import SFStoryboard

pad_cats = {}


def usage():
    parser = argparse.ArgumentParser(description="SF scrum master")
    parser.add_argument('--url', '-u', metavar='https://sf.dom',
                        default='https://softwarefactory-project.io',
                        help='The URL of your SF instance')
    parser.add_argument('--api-key', '-a', metavar='APIKEY',
                        default=os.environ.get('SF_APIKEY'),
                        help=('API key to use to perform these operations. '
                              'The user should be authorized for these'))
    parser.add_argument('--pad-url', help=('The etherpad to update'),
                        default='https://softwarefactory-project.io/etherpad/'
                                'p/sf-backlog')
    return parser.parse_args()


def get_category_position(cat):
    for idx in range(len(pad_content)):
        if pad_content[idx].startswith("# Project Backlog:"):
            pad_cat = pad_content[idx].split(':', 1)[-1].strip()
            # Look for inbox
            for sub_idx in range(idx + 1, len(pad_content)):
                if pad_content[sub_idx] == "## Inbox":
                    break
                if pad_content[sub_idx].startswith("# Project Backlog:"):
                    print("Inbox not found for %s" % pad_cat)
                    pad_content.insert(sub_idx, "## Inbox")
                    sub_idx += 1
                    break
            pad_cats[pad_cat] = sub_idx
    if cat not in pad_cats:
        # Add category
        print("Adding missing category %s" % cat)
        pad_content.append("# Project Backlog: %s" % cat)
        pad_content.append("## Inbox")
        pad_cats[cat] = len(pad_content) - 1
    return pad_cats[cat]


def load_stories():
    client = SFStoryboard(args.url + "/storyboard_api",
                          get_cookie(args.url, api_key=args.api_key))
    projects = {}
    # First set all project name
    for project in client.projects.list():
        projects[project.id] = project.name
    # Then replace project name by project group
    for project_group in client.project_groups.list():
        for project in project_group.projects.list():
            projects[project.id] = project_group.name
    stories = []
    for story in client.stories.list():
        story_dict = story.to_dict()
        story_dict["projects"] = set()
        story_dict["task_count"] = 0
        for task in story.tasks.list():
            if task.status in ('invalid', 'merged'):
                continue
            story_dict["task_count"] += 1
            story_dict["projects"].add(projects.get(task.project_id,
                                                    "UNKNOWN PROJECT"))
        stories.append(story_dict)
    pickle.dump(stories, open("stories.pkl", "wb"))
    return stories


args = usage()
export_url = args.pad_url + "/export/txt"
print("Reading pad %s" % export_url)
pad_content = requests.get(export_url).text.split('\n')
pad_content_len = len(pad_content)

PKL_FILE = "stories.pkl"
if os.path.isfile(PKL_FILE):
    print("Re-using %s file" % PKL_FILE)
    stories = pickle.load(open("stories.pkl"))
else:
    print("Reading stories from %s" % args.url)
    stories = load_stories()

for story in stories:
    found = False
    pos = 0
    for pad_line in pad_content:
        if pad_line.startswith("%d:" % story['id']):
            found = True
            break
        pos += 1

    if story['status'] == 'active':
        # Make sure it's in the pad
        story_content = [
            "%d: %s" % (story['id'], story['title']),
            "  URL: %s/storyboard/#!/story/%d" % (args.url, story['id']),
            "  TASK COUNT: %d" % story['task_count'],
        ]
        if story['tags']:
            story_content.append("  TAGS: %s" % " ".join(sorted(
                list(story['tags']))))
        if len(story['projects']) > 1:
            cat = "CROSS-PROJECT"
        else:
            cat = list(story['projects'])[0]
        if not found:
            print("Adding missing story %s" % story["title"])
            pad_pos = get_category_position(cat)
            pad_content.insert(pad_pos + 1, "\n".join(story_content))
        else:
            print("Updating story %s" % story["title"])
            start_pos = pos
            pad_content[pos] = story_content[0]
            for pos in range(start_pos + 1, len(pad_content)):
                if not re.match(r"  [A-Z ]+: .*$", pad_content[pos]):
                    break
                meta = pad_content[pos].split(':')[0].strip()
                if meta == 'TASK COUNT':
                    pad_content[pos] = "  TASK COUNT: %d" % story['task_count']
                elif meta == 'TAGS':
                    if story['tags']:
                        pad_content[pos] = "  TAGS: %s" % " ".join(sorted(
                            list(story['tags'])))


if pad_content_len != len(pad_content):
    print("Updating content from %d to %d lines" % (
        pad_content_len, len(pad_content)))

    import_url = args.pad_url + "/import"
    print("%s: updating..." % import_url)
    files = {'file': ('content.txt', "\n".join(pad_content), "text/plain")}
    r = requests.post(import_url, files=files)
    print("=> %s" % r)
    # print("\n".join(pad_content))
