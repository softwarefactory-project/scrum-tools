#!/usr/bin/python


import requests
import re


class JSONObject(object):
    fields = []

    def to_dict(self):
        j = {}
        for x in self.fields:
            if getattr(self, x) is not None:
                try:
                    j[x] = getattr(self, x).to_dict()
                except:
                    j[x] = getattr(self, x)
        return j


class Attachment(JSONObject):
    fields = ['doUpload', 'url', 'contentType']

    def __init__(self, url, contentType=None):
        self.doUpload = True
        self.url = url
        if contentType:
            self.contentType = contentType


class Content(JSONObject):
    fields = ['text', 'type']

    def __init__(self, text):
        self.type = "text/html"
        self.text = text


class Post(JSONObject):
    fields = ['attachments', 'content', 'parent', 'subject', 'type',
              'tags', 'categories']

    def __init__(self, subject, content,
                 categories=None, tags=None, attachments=None, **kwargs):
        self.attachments = attachments or []
        self.content = Content(re.sub('&', 'and', content))
        self.parent = "https://mojo.redhat.com/api/core/v3/places/1414977"
        self.subject = subject or "Yet another blog post"
        self.type = "post"
        self.tags = tags or []
        self.categories = categories or []


class MojoSFDFG(object):
    def __init__(self, user, password):
        self.user = user
        self.password = password
        self.base_url = "https://mojo.redhat.com/api/core/v3/places/1414977/"

    def post_blog(self, post):
        payload = post.to_dict()
        url = self.base_url + "contents"
        headers = {'Content-type': 'application/json;charset=utf-8'}
        x = requests.post(url, json=payload, auth=(self.user, self.password),
                          headers=headers)
        print "POST status: %s" % x.status_code
        if x.status_code >= 400:
            print x.text
            print payload
