import json
import requests
from openpyxl import Workbook, load_workbook
import shutil
from github import Github
import datetime
import statistics

# GitHub credentials (several accounts are required to exceed the limitation - 5000 requests per hour)
accounts = [
    ('email-1', 'token-1'),
    ('email-2', 'token-2'),
    ('email-3', 'token-3')
]

account = 0
num_req = 0


# helper function to get all the pages from request
def get_page(repo_name, link):
    global account, num_req
    res = requests.get('https://api.github.com/repos/' + repo_name + link + '?per_page=100&state=all',
                       auth=(accounts[account][0], accounts[account][1]))
    data = res.json()
    num_req += 1
    while 'next' in res.links.keys():
        num_req += 1
        print(num_req)
        res = requests.get(res.links['next']['url'], auth=(accounts[account][0], accounts[account][1]))
        data.extend(res.json())
        if num_req % 4990 == 0:
            account = (account + 1) % len(accounts)
            num_req = 0
            print("Switch acc", accounts[account][0])
    return data


# get all issues and pull requests
def get_issues_pulls(repo_name):
    return get_page(repo_name, '/issues')


# Check create and closed at dates
def check_dates(create_date, closed_date=None):
    check_date = datetime.datetime(2022, 2, 23)
    create_date = datetime.datetime.strptime(create_date, "%Y-%m-%d")
    if create_date > check_date:
        return False

    if closed_date:
        closed_at = datetime.datetime.strptime(closed_date, "%Y-%m-%d")
        return closed_at < check_date

    return True


def parse_closed_at_date(string):
    if string == "null":
        return None
    return string[:10]


# get closed pull requests and its number of comments
def get_closed_pulls(issues_pulls):
    closed_pulls = []
    closed_pulls_comments = 0
    for pull in issues_pulls:
        if pull['state'] == 'closed' and 'pull_request' in pull:
            closed_at = parse_closed_at_date(pull['closed_at'])
            if check_dates(pull['created_at'][:10], closed_at):
                closed_pulls.append(pull)
                closed_pulls_comments += int(pull['comments'])

    return closed_pulls, closed_pulls_comments


# get closed issues and its number of comments
def get_closed_issues(issues_pulls):
    closed_issues = []
    closed_issues_comments = 0
    for issue in issues_pulls:
        if issue['state'] == 'closed' and 'pull_request' not in issue:
            closed_at = parse_closed_at_date(issue['closed_at'])
            if check_dates(issue['created_at'][:10], closed_at):
                closed_issues.append(issue)
                closed_issues_comments += int(issue['comments'])

    return closed_issues, closed_issues_comments


# get open pull requests and its number of comments
def get_opened_pulls(issues_pulls):
    open_pulls = []
    open_pulls_comments = 0
    for pull in issues_pulls:
        if pull['state'] == 'open' and 'pull_request' in pull:
            if check_dates(pull['created_at'][:10]):
                open_pulls.append(pull)
                open_pulls_comments += int(pull['comments'])

    return open_pulls, open_pulls_comments


# get open issues and its number of comments
def get_opened_issues(issues_pulls):
    open_issues = []
    open_issues_comments = 0
    for issue in issues_pulls:
        if issue['state'] == 'open' and 'pull_request' not in issue:
            if check_dates(issue['created_at'][:10]):
                open_issues.append(issue)
                open_issues_comments += int(issue['comments'])

    return open_issues, open_issues_comments


# get list of developers closed issues
def developers_closed_issues(closed_issues):
    global num_req, account
    dev_closed_issues_set = set()
    for i in closed_issues:
        closed_by = requests.get(i['url'], auth=(accounts[account][0], accounts[account][1])).json()['closed_by']
        if closed_by is not None:
            closed_by = closed_by['login']
            dev_closed_issues_set.add(closed_by)
        num_req += 1
        if num_req % 100 == 0:
            account = (account + 1) % len(accounts)
            num_req = 0
            print("Switch acc", accounts[account][0])

    return list(dev_closed_issues_set)


# get list of developers opened issues
def developers_opened_issues(opened_issues, closes_issues):
    dev_opened_issues = set()
    for i in opened_issues:
        dev_opened_issues.add(i['user']['login'])
    for i in closes_issues:
        dev_opened_issues.add(i['user']['login'])

    return list(dev_opened_issues)


# get list of developers closed pull requests
def developers_closed_pulls(closed_pulls):
    global num_req, account
    dev_closed_pulls = set()
    for i in closed_pulls:
        closed_by = requests.get(i['url'], auth=(accounts[account][0], accounts[account][1])).json()['closed_by']
        if closed_by is not None:
            closed_by = closed_by['login']
            dev_closed_pulls.add(closed_by)
        num_req += 1
        print(num_req)
        if num_req % 4990 == 0:
            account = (account + 1) % len(accounts)
            num_req = 0
            print("Switch acc", accounts[account][0])

    return list(dev_closed_pulls)


# get list of developers opened pull requests
def developers_opened_pulls(opened_pulls, closed_pulls):
    dev_opened_pulls = set()
    for i in opened_pulls:
        dev_opened_pulls.add(i['user']['login'])
    for i in closed_pulls:
        dev_opened_pulls.add(i['user']['login'])

    return list(dev_opened_pulls)


# get percentage of closed issues
def percentage_of_closed_issues(closed_issues, opened_issues):
    percentage = closed_issues[i] / (closed_issues[i] + opened_issues[i])

    return percentage


# count number of comments in issues and pull requests
def count_issue_comments(repo_name):
    comments = get_page(repo_name, '/issues/comments')
    iss_com = 0
    pull_com = 0
    flag = 0
    for c in comments:
        if c == 'message':
            flag = 1
            print("FLAG")
            continue
        if datetime.datetime.strptime(c['created_at'], '%Y-%m-%dT%H:%M:%SZ') < \
                datetime.datetime.strptime('2022-02-24T00:00:00Z', '%Y-%m-%dT%H:%M:%SZ'):
            if '/pull/' in c['html_url']:
                pull_com += 1
            else:
                iss_com += 1

    return flag, iss_com, pull_com


# count number of reactions in opened and closed issues
def issue_reactions(opened_issues, closed_issues):
    oi_reactions = 0
    ci_reactions = 0
    for oi in opened_issues:
        oi_reactions += oi['reactions']['total_count']
    for ci in closed_issues:
        ci_reactions += ci['reactions']['total_count']

    return oi_reactions, ci_reactions


# count number of reactions in opened and closed pulls
def pulls_reactions(opened_pulls, closed_pulls):
    op_reactions = 0
    cp_reactions = 0
    for op in opened_pulls:
        op_reactions += op['reactions']['total_count']
    for cp in closed_pulls:
        cp_reactions += cp['reactions']['total_count']

    return op_reactions, cp_reactions


# count percentage of merged pulls among closed
def percent_merged_pulls(closed_pulls):
    mp = 0
    for c in closed_pulls:
        if c['merged_at'] is not None:
            mp += 1

    return mp/len(closed_pulls)


def main():
    repos = open('repo-list.txt')
    lines = repos.readlines()

    repo_count = 2

    for line in lines:
        repo_url = line.rstrip()  # https://github.com/owner/repo
        repo_name = repo_url[19:]  # owner/repo
        print(repo_name)

        pulls_issues = get_issues_pulls(repo_name)
        opened_issues, opened_issues_comments = get_opened_issues(pulls_issues)
        closed_issues,  closed_issues_comments = get_closed_issues(pulls_issues)
        closed_pulls, closed_pulls_comments = get_closed_pulls(pulls_issues)
        open_pulls, open_pulls_comments = get_opened_pulls(pulls_issues)
        devs_opened_issues = developers_opened_issues(opened_issues, closed_issues)
        devs_closed_issues = developers_closed_issues(closed_issues)
        devs_opened_pulls = developers_opened_pulls(open_pulls, closed_pulls)
        devs_closed_pulls = developers_closed_pulls(closed_pulls)
        oi_reactions, ci_reactions = issue_reactions(opened_issues, closed_issues)
        op_reactions, cp_reactions = pulls_reactions(open_pulls, closed_pulls)
        merged_pulls = percent_merged_pulls(closed_pulls)

        sheet_name = 'metrics.xlsx'
        wb = load_workbook(sheet_name)

        ### save metrics to file

        wb.save(sheet_name)
        repo_count += 1


main()
