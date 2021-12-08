#!/usr/bin/env python

from __future__ import print_function

import base64
import json
import os
import urllib.parse
import urllib.request


def notify(event, context):

    slack_url = os.environ["SLACK_WEBHOOK_URL"]
    slack_channel = os.environ["SLACK_CHANNEL"]
    slack_username = os.environ["SLACK_USERNAME"]
    slack_emoji = os.environ["SLACK_EMOJI"]

    print(
        """Function triggered by messageId {} published at {} to {} """.format(
            context.event_id, context.timestamp, context.resource["name"]
        )
    )

    if "data" in event:
        pubsub_message = base64.b64decode(event["data"]).decode("utf-8")

        # print(pubsub_message)
        json_data = json.loads(pubsub_message)
        findings = json_data["Findings"]

        payload = {
            "channel": slack_channel,
            "username": slack_username,
            "icon_emoji": slack_emoji,
            "attachments": [],
            "text": json_data["Subject"],
        }

        slack_message = {"fallback": "A new message", "fields": [{"title": "Vulnerable domains"}]}

        for finding in findings:

            try:
                cname = finding["CNAME"]
                print(f"VULNERABLE: {finding['Domain']}  CNAME  {cname} in GCP Project {finding['Project']}")
                slack_message["fields"].append(
                    {
                        "value": finding["Domain"] + "  CNAME  " + cname + " in GCP Project " + finding["Project"],
                        "short": False,
                    }
                )

            except:
                print(f"VULNERABLE: {finding['Domain']} in GCP Project {finding['Project']}")
                slack_message["fields"].append(
                    {"value": finding["Domain"] + " in GCP Project " + finding["Project"], "short": False}
                )

        payload["attachments"].append(slack_message)

        data = urllib.parse.urlencode({"payload": json.dumps(payload)}).encode("utf-8")
        req = urllib.request.Request(slack_url)
        urllib.request.urlopen(req, data)
