#! /usr/bin/python


"""Very simple exporter from our storyboard instance to the public taiga.io
board. New stories and tasks get added if they don't already exist in taiga.

This script is not really intended to be cron-ed (very little need to as
storyboard is barely used anymore) but should be run manually from time to
time. A mysql dump of the storyboard database can be converted with the
enclosed script 'mysql2sqlite'.

This script depends on python-taiga to run."""


from taiga import TaigaAPI
import sqlite3
import argparse
import logging
import sys


link = '(was https://softwarefactory-project.io/storyboard/#!/story/%s )\n\n'

LOGGER = logging.getLogger('storyboard2taiga')
LOGGER.setLevel(logging.DEBUG)

console = logging.StreamHandler()
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console.setFormatter(formatter)
LOGGER.addHandler(console)

parser = argparse.ArgumentParser(description="storyboard2taiga")
parser.add_argument('--password', '-p', metavar='XXX',
                    help="SFBot0's password")
parser.add_argument('--project', '-P', metavar='morucci-software-factory',
                    help="the taiga project to synchronize")
parser.add_argument('--dump', '-d',
                    help='the sqlite3 dump of the storyboard db')
parser.add_argument('--verbose', '-v', default=False, action='store_true',
                    help='Run in debug mode')

args = parser.parse_args()
if args.verbose:
    console.setLevel(logging.DEBUG)
else:
    console.setLevel(logging.INFO)
if not args.password or not args.dump or not args.project:
    sys.exit('Missing argument(s)')

api = TaigaAPI()
api.auth(username='sfbot0', password=args.password)
sf_dfg = api.projects.get_by_slug(args.project)

db = sqlite3.connect(args.dump)
c = db.cursor()

for story_data in c.execute("select id, title, description from stories "
                            "where id in (select story_id from tasks where "
                            "status != 'merged' and status != 'invalid') "
                            "group by id"):
    id, title, description = story_data
    LOGGER.info("#%s - %s" % (id, title))
    description = (link % id) + description
    # search for existing US on taiga
    search = api.search(project=sf_dfg.id, text=(link % id))
    user_story = None
    if len(search.user_stories) == 1:
        LOGGER.info('- found on taiga')
        user_story = sf_dfg.get_userstory_by_ref(search.user_stories[0].ref)
    elif len(search.user_stories) > 1:
        LOGGER.info('- found multiple occurrences')
        for u in search.user_stories:
            # refine search a bit
            _ = sf_dfg.get_userstory_by_ref(u.ref)
            if link % id in _.description:
                LOGGER.info('- found it')
                user_story = _
                break
    else:
        LOGGER.info('- not found on taiga, creating')
    if user_story is None:
        user_story = sf_dfg.add_user_story(title, description=description)
    existing_tasks_subjects = [x.subject for x in user_story.list_tasks()]
    c2 = db.cursor()
    us_tag = None
    for task_data in c2.execute("select title, name from tasks "
                                "left outer join projects on "
                                "tasks.project_id = projects.id where "
                                "status != 'merged' and status != 'invalid' "
                                "and story_id = %s" % id):
        task_title, tag = task_data
        if '/' in tag:
            us_tag, task_tag = tag.split('/')
        else:
            task_tag = tag
        if task_tag == 'dlrn':
            us_tag = 'dlrn'
        if task_title not in existing_tasks_subjects:
            LOGGER.info("\t%s on %s, %s" % (task_title, task_tag, us_tag))
            task = user_story.add_task(task_title, sf_dfg.task_statuses[0].id)
            if task_tag:
                task.tags += [[task_tag, None], ]
            task.update()
    c2.close()
    if us_tag:
        user_story.tags += [[us_tag, None], ]
    user_story.update()
c.close()
