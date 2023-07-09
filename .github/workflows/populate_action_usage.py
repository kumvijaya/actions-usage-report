#!/usr/bin/python

import os
import requests
import argparse

parser = argparse.ArgumentParser(
    description="""
        Gets the actions usage
        Usage:
            python populate_action_usage.py --org 'my-org'
            python populate_action_usage.py --user 'my-user'

    """
)

parser.add_argument(
    "-o",
    "--org",
    required=False,
    help="The org name to check for, ex: 'my-org'",
)

parser.add_argument(
    "-u",
    "--user",
    required=False,
    help="The user to check for, ex: 'my-user'",
)

args = parser.parse_args()
org_name = args.org
user_name = args.user
if not org_name and not user_name:
    raise Exception(
        f"Either org or user to be provided as input"
    )

github_access_token = os.environ['GH_TOKEN']

def get(url, headers=None):
    """Process get request

    Args:
        url (str): request url
        headers (dict): request headers

    Returns:
        dict: response json
    """
    session = requests.session()
    if headers:
        session.headers.update(headers)
    response = session.get(url)
    reponse_json = None
    if response.status_code not in [200]:
        status = response.status_code
        content = response.content
        raise Exception(
            f"Received error response ({status}) for url request {url}. Error Response: {content}"
        )
    else:
        reponse_json = response.json()
    return reponse_json

def get_usage_info_url():
    type_info = ''
    if org_name:
        type_info = f'/orgs/{org_name}'
    if user_name:
        type_info = f'/users/{user_name}'
    return f'https://api.github.com/{type_info}/settings/billing/actions'

def set_output(name, value):
    """Sets github action output

    Args:
        name (str): key
        value (str): value
    """
    with open(os.environ["GITHUB_OUTPUT"], "a") as fh:
        print(f"{name}={value}", file=fh)

def set_env(name, value):
    """Sets github action env var

    Args:
        name (str): key
        value (str): value
    """
    env_file = os.getenv("GITHUB_ENV")
    with open(env_file, "a") as file:
        file.write(f"{name}={value}")

def populate_usage_info():
    """Populates usage info
    """
    url = get_usage_info_url()
    response = get(url)
    set_output('TOTAL_MINUTES_USED', response["total_minutes_used"])
    # set_output('TOTAL_PAID_MINUTES_USED', response["total_paid_minutes_used"])
    set_output('INCLUDED_MINUTES', response["included_minutes"])
    
populate_usage_info()
