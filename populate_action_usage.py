#!/usr/bin/python

"""Gets the actions usage info and populates to Github Output
"""
import os
import requests


def get_auth_header():
    """Gets the auth header

    Args:
        access_token (str): access token

    Returns:
        dict: header
    """
    access_token = os.environ["GH_TOKEN"]
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
    session.headers.update(get_auth_header())
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


def get_owner_type():
    """Gets the github repo owner type"""
    org_repo_name = os.environ["GITHUB_REPOSITORY"]
    url = f"https://api.github.com/repos/{org_repo_name}"
    response = get(url)
    return response["owner"]["type"]


def get_actions_billing_url():
    """Gets actions billing info API Url

    Returns:
        str: GitHub actions billing API url
    """
    owner_type = get_owner_type()
    owner_name = os.environ["GITHUB_REPOSITORY_OWNER"]
    account_type = "users" if owner_type == "User" else "orgs"
    return (
        f"https://api.github.com/{account_type}/{owner_name}/settings/billing/actions"
    )


def set_output(name, value):
    """Sets github action output

    Args:
        name (str): key
        value (str): value
    """
    with open(os.environ["GITHUB_OUTPUT"], "a") as fh:
        print(f"{name}={value}", file=fh)


def populate_actions_usage_info():
    """Populates actions usage info"""
    url = get_actions_billing_url()
    response = get(url)
    total_minutes_used = response["total_minutes_used"]
    included_minutes = response["included_minutes"]
    total_paid_minutes_used = response["total_paid_minutes_used"]
    total_minutes_used = 1500.00
    usage_percentage = 0
    if included_minutes > 0:
        usage_percentage = round((total_minutes_used / included_minutes) * 100)
    set_output("TOTAL_MINUTES_USED", total_minutes_used)
    set_output("TOTAL_PAID_MINUTES_USED", total_paid_minutes_used)
    set_output("INCLUDED_MINUTES", included_minutes)
    set_output("USAGE_PERCENTAGE", usage_percentage)


populate_actions_usage_info()
