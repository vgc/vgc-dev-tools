#!/usr/bin/env python3
#
# Queries and prints the date and time at which GitHub stars were received.
# The output can for example be imported in spreadsheet software for plotting.
#
# $ python3 stars.py
# 2017-11-09 01:17:23
# 2017-11-09 07:55:53
# 2017-11-11 22:10:10
# ...


import requests
import json
import re


def get_page(url, headers, per_page, page):
    url_with_params = url + f'?per_page={per_page}&page={page}'
    return requests.get(url_with_params, headers=headers)


def get_all_pages(url, headers, per_page=100):
    json = []
    page = 1
    while page:
        response = get_page(url, headers, per_page, page)
        json += response.json()
        next_page = re.search('page=(\d+)>; rel="next"', response.headers['link'])
        if next_page:
            page = int(next_page[1])
        else:
            page = None
    return json


if __name__ == "__main__":
    url = "https://api.github.com/repos/vgc/vgc/stargazers"
    headers = {"Accept": "application/vnd.github.v3.star+json"}
    json = get_all_pages(url, headers)
    stars = [x['starred_at'] for x in json]
    for x in stars:
        print(x[:19].replace('T', ' '))
