#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""github issues to taiga user stories importer.

Load configuration from github2taiga.conf file. See *.example.

Without arguments, perform dry run. Commit changes using 'sync' argument.

Usage:
  github2taiga.py
  github2taiga.py sync

Options:
  -h --help     Show this screen.

"""
from __future__ import print_function
from docopt import docopt
import ConfigParser
from taiga import TaigaAPI
from pygithub3 import Github
import sys


DEFAULT_CONFIG = 'github2taiga.conf'


def github2taiga(dry_run=False):
    cfg = ConfigParser.ConfigParser()
    cfg.read(DEFAULT_CONFIG)
    # get github issues to import
    gh = Github()
    issues = gh.issues.list_by_repo(
        user=cfg.get('github', 'user'),
        repo=cfg.get('github', 'repo'),
        labels=cfg.get('github', 'labels')
    )
    # connect to taiga for import
    taiga = TaigaAPI()
    taiga.auth(
        username=cfg.get('taiga', 'username'),
        password=cfg.get('taiga', 'password'),
    )
    project = taiga.projects.get_by_slug(cfg.get('taiga', 'project'))
    user_stories = project.list_user_stories()
    tags = cfg.get('taiga', 'tags').split('.')
    tags_set = set(tags)

    for i in issues.iterator():
        print("\nIssue #%d %s" % (i.number, i.title))
        subj = i.title
        import_footer = "Auto imported from %s Issue: %s" % (
            cfg.get('github', 'repo'), i.html_url)
        desc = "%s\n\n%s" % (i.body, import_footer)

        found = False
        for us in user_stories:
            # for safety and speed, only check stories with requested tags
            if not (tags_set <= set([x for x, _ in us.tags])):
                continue
            # get user story details including description
            story = taiga.user_stories.get(us.id)
            if import_footer in story.description:
                found = True
                print("  - already imported: #%d %s" % (us.ref, us.subject))
                need_update = False
                if story.subject != subj:
                    print("  - updating subject")
                    story.subject = subj
                    need_update = True
                if story.description != desc:
                    print("  - updating description")
                    story.description = desc
                    need_update = True
                if need_update:
                    if dry_run:
                        print("  - DRY RUN: not really updated")
                    else:
                        story.update()
                else:
                    print("  - up to date")

        if not found:
            print("  - new issue")
            if dry_run:
                print("  - DRY RUN: not really created")
            else:
                # add taiga user story
                story = project.add_user_story(
                    subj,
                    description=desc,
                    # TODO: assign to proper assignee from the config
                    # taiga.users.get/list() was only throwing errors :-/
                    # assign_to = cfg.get('taiga', 'assign_to'),
                    tags=tags,
                )
                print("  - created new story: #%d %s" % (story.ref, subj))


def main():
    args = docopt(__doc__)
    dry_run = not args['sync']
    if dry_run:
        print("DRY RUN: I'm not really touching anything")
        print("(use `github2taiga.py sync` to execute the import)")
    return github2taiga(dry_run=dry_run)


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
