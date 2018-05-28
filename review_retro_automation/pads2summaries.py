#! /usr/bin/python


import sys
from datetime import datetime, timedelta
import os
from jinja2 import Environment, FileSystemLoader
from collections import OrderedDict
import getpass
import codecs

FILE_PATH = os.path.dirname(os.path.abspath(__file__))

os.sys.path.append(FILE_PATH)
from lib import etherpad, mojo, gmail


TEMPLATE_DIR = FILE_PATH + "/templates/"

def datetimeformat(value, format='%Y-%m-%d %H:%M'):
    return value.strftime(format)


def prepare_templates(sprint_id):
    try:
        sprint_end = datetime.strptime(sprint_id + ' Thu', '%Y-%W %a')
        sprint_start = sprint_end - timedelta(days=14)
        next_sprint_end = sprint_end + timedelta(days=14)
    except:
        sys.exit('That sprint name does not look right...')
    publish_date = datetime.now()
    j2_env = Environment(loader=FileSystemLoader(TEMPLATE_DIR),
                         trim_blocks=True,
                         extensions=['jinja2.ext.loopcontrols'])
    j2_env.filters['datetimeformat'] = datetimeformat
    # Review
    review_pad = etherpad.ReviewPadParser('sfdfg-review')
    topics = review_pad.parse()

    kwargs = {'sprint_id': sprint_id,
              'sprint_end': sprint_end,
              'sprint_start': sprint_start,
              'next_sprint_end': next_sprint_end,
              'topics': topics,
              'publish_date': publish_date}
    # internal
    with open('/tmp/%s_review_email_internal.txt' % sprint_id, 'w') as f:
        f.write(
            j2_env.get_template('review_email_internal.txt.j2').render(
                **kwargs).encode('utf-8')
            )
    with open('/tmp/%s_review_blog_internal.html' % sprint_id, 'w') as f:
        f.write(
            j2_env.get_template('review_blog_internal.html.j2').render(
                **kwargs).encode('utf-8')
            )
    # public
    public_topics = {'Software Factory': [],
                     'our contributions to Zuul and Nodepool': []}
    for t in ('SF for OSP', 'Software Factory in general', 'RepoXplorer'):
        public_topics['Software Factory'] += topics[t]
    for t in ('openstack-infra', ):
        public_topics['our contributions to Zuul and Nodepool'] += topics[t]
    kwargs['topics'] = public_topics

    with open('/tmp/%s_review_email_public.txt' % sprint_id, 'w') as f:
        f.write(
            j2_env.get_template('review_email_public.txt.j2').render(
                **kwargs).encode('utf-8')
            )
    with open('/tmp/%s_review_blog_public.rst' % sprint_id, 'w') as f:
        f.write(
            j2_env.get_template('review_blog_public.rst.j2').render(
                **kwargs).encode('utf-8')
            )
    # retro
    retro_pad = etherpad.RetroPadParser('sfdfg-retro')
    topics = retro_pad.parse()
    kwargs = {'topics': topics, }
    with open('/tmp/%s_retro_blog_internal.html' % sprint_id, 'w') as f:
        f.write(
            j2_env.get_template('retro_blog_internal.html.j2').render(
                kwargs).encode('utf-8')
            )
    # daily
    daily_pad = etherpad.DailyPadParser('sfdfg-daily')
    days = daily_pad.parse()
    tabled_days = {}
    for day in days:
        _table = {'headers': ['Type', 'Author', 'Component', '-'],
                  'rows': []}
        for entry in days[day]:
            _table['rows'].append(
                [entry['type'], entry['author'],
                 entry['subject'] or '-', entry['data'], ])
        tabled_days[day] = _table

    kwargs = {'days': OrderedDict(sorted(tabled_days.items(),
                                         key=lambda x: x[0]))}
    with open('/tmp/%s_daily_blog_internal.html' % sprint_id, 'w') as f:
        f.write(
            j2_env.get_template('daily_blog_internal.html.j2').render(
                kwargs).encode('utf-8')
            )


def publish(sprint_id, user):
    # password = getpass.getpass('OTP password (Kerberos + PIN): ')
    # publisher = mojo.MojoSFDFG(user, password)
    # # review
    # with codecs.open('/tmp/%s_review_blog_internal.html' % sprint_id,
    #                  encoding="utf-8") as f:
    #     post = mojo.Post(
    #         subject="Sprint %s Review" % sprint_id,
    #         content=f.read(),
    #         categories=["Dailies and retrospectives"]
    #     )
    #     publisher.post_blog(post)
    # # retro
    # password = getpass.getpass('OTP password (Kerberos + PIN): ')
    # publisher = mojo.MojoSFDFG(user, password)
    # with codecs.open('/tmp/%s_retro_blog_internal.html' % sprint_id,
    #                  encoding="utf-8") as f:
    #     post = mojo.Post(
    #         subject="Sprint %s Retrospective" % sprint_id,
    #         content=f.read(),
    #         categories=["Dailies and retrospectives"]
    #     )
    #     publisher.post_blog(post)
    # # daily
    # password = getpass.getpass('OTP password (Kerberos + PIN): ')
    # publisher = mojo.MojoSFDFG(user, password)
    # with codecs.open('/tmp/%s_daily_blog_internal.html' % sprint_id,
    #                  encoding="utf-8") as f:
    #     post = mojo.Post(
    #         subject="Sprint %s Daily Minutes" % sprint_id,
    #         content=f.read(),
    #         categories=["Dailies and retrospectives"]
    #     )
    #     publisher.post_blog(post)
    # TODO don't assume where the gmail secrets are
    G = gmail.GmailHelper('/tmp/gmail_secret.json')
    # os-status
    with codecs.open('/tmp/%s_review_email_internal.txt' % sprint_id,
                     encoding="utf-8") as f:
        G.send_message('me', f.read())
    # softwarefactory-dev
    with codecs.open('/tmp/%s_review_email_public.txt' % sprint_id,
                     encoding="utf-8") as f:
        G.send_message('me', f.read())


if __name__ == "__main__":
    sprint_id = sys.argv[1]
    if sys.argv[2] == 'prepare':
        prepare_templates(sprint_id)
    elif sys.argv[2] == 'publish':
        if len(sys.argv) > 3:
            user = sys.argv[3]
        else:
            user = raw_input("MOJO Username: ")
        publish(sprint_id, user)
    else:
        sys.exit('I can only "prepare" or "publish" !')
