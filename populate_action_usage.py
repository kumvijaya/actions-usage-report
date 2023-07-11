#!/usr/bin/python

import os
import requests
import argparse

parser = argparse.ArgumentParser(
    description="""
        Gets the actions usage info and populates to Github Output
        Usage:
            python populate_action_usage.py --org 'my-org'
            python populate_action_usage.py --user 'my-user'

    """
)

parser.add_argument(
    "-o",
    "--org",
    required=False,
    help="The github org name to check for, ex: 'my-org'",
)

parser.add_argument(
    "-u",
    "--user",
    required=False,
    help="The github user to check for, ex: 'my-user'",
)

args = parser.parse_args()
org_name = args.org
user_name = args.user
if not org_name and not user_name:
    raise Exception(
        f"Either org or user to be provided as input"
    )

github_access_token = os.environ['GH_TOKEN']

def get_auth_header(access_token):
    """Gets the auth header

    Args:
        access_token (str): access token

    Returns:
        dict: header
    """
    return {"Authorization": f"token {access_token}"}

def get(url, headers=None):
    """Process get request

    Args:
        url (str): request url
        headers (dict): request headers

    Returns:
        dict: response json
    """
    session = requests.session()
    headers = get_auth_header(github_access_token)
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
    """Gets actions minutes usage info API Url

    Returns:
        str: GitHub API url
    """
    account_path = ''
    if org_name:
        account_path = f'orgs/{org_name}'
    if user_name:
        account_path = f'users/{user_name}'
    return f'https://api.github.com/{account_path}/settings/billing/actions'

def set_output(name, value):
    """Sets github action output

    Args:
        name (str): key
        value (str): value
    """
    with open(os.environ["GITHUB_OUTPUT"], "a") as fh:
        print(f"{name}={value}", file=fh)

def populate_usage_info():
    """Populates usage info
    """
    url = get_usage_info_url()
    response = get(url)
    total_minutes_used = response["total_minutes_used"]
    included_minutes = response["included_minutes"]
    total_paid_minutes_used = response["total_paid_minutes_used"]
    total_minutes_used = 1500.00
    usage_percentage = 0
    if included_minutes > 0:
        usage_percentage = (total_minutes_used / included_minutes) * 100
    set_output('TOTAL_MINUTES_USED', total_minutes_used)
    set_output('TOTAL_PAID_MINUTES_USED', total_paid_minutes_used)
    set_output('INCLUDED_MINUTES', included_minutes)
    set_output('USAGE_PERCENTAGE', usage_percentage)
    
populate_usage_info()