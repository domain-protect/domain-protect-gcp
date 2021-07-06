#!/usr/bin/env python

from __future__ import print_function
import os, json, base64
import urllib.request, urllib.parse

def notify(event, context):

    slack_url = os.environ['SLACK_WEBHOOK_URL']
    slack_channel = os.environ['SLACK_CHANNEL']
    slack_username = os.environ['SLACK_USERNAME']
    slack_emoji = os.environ['SLACK_EMOJI']

    print("""Function triggered by messageId {} published at {} to {} """.format(context.event_id, context.timestamp, context.resource["name"]))

    if 'data' in event:
        pubsub_message = base64.b64decode(event['data']).decode('utf-8')

        #print(pubsub_message)
        json_data = json.loads(pubsub_message)
        findings = json_data['Findings']
        subject = json_data['Subject']

        payload = {"channel": slack_channel, "username": slack_username, "icon_emoji": slack_emoji, "attachments": [],
                   'text': subject}

        slack_message = {
            "fallback": "A new message",
            "fields": [{"title": "Vulnerable domains"}]
        }

        for finding in findings:
            project = finding['Project']
            domain = finding['Domain']

            try:
                cname = finding['CNAME']
                print("VULNERABLE: " + domain + "  CNAME  " + cname + " in GCP Project " + project)
                slack_message['fields'].append({"value": domain + "  CNAME  " + cname + " in GCP Project " + project, "short": False} )

            except:
                print("VULNERABLE: " + domain + " in GCP Project " + project)
                slack_message['fields'].append({"value": domain + " in GCP Project " + project, "short": False} )


        payload['attachments'].append(slack_message)

        data = urllib.parse.urlencode({"payload": json.dumps(payload)}).encode("utf-8")
        req = urllib.request.Request(slack_url)
        urllib.request.urlopen(req, data)
