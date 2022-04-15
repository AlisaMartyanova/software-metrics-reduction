import datetime
import os
import requests
import shutil
import statistics
from openpyxl import load_workbook

# GitHub credentials
login = 'email'
token = 'token'

# collect metrics before this date
date = '2022-02-24T00:00:00Z'


# count commits in default branch
def commits_repo(git_folder):
    os.system('cd repo/' + git_folder + ' && git rev-list --count HEAD > ../temp.txt')
    f = open('repo/temp.txt')
    commits = int(f.readlines()[0])
    f.close()

    return commits


# count total number of files and number of .md files
def count_files_repo(git_folder):
    os.system('cd repo/' + git_folder + ' && git ls-files | wc -l > ../temp.txt')
    f = open('repo/temp.txt')
    files = f.read()
    f.close()

    os.system('cd repo/' + git_folder + ' && git ls-files | grep .*.md$ | wc -l > ../temp.txt')
    f = open('repo/temp.txt')
    md = f.read()
    f.close()

    return int(files), int(md)


# count insertions and deletions in main
def lines_added_and_deleted_repo(git_folder, num):
    os.system('cd repo/' + git_folder + ' && git log -n ' + str(num) + ' --format=%H|head -n 1 > ../temp.txt')
    f = open('repo/temp.txt')
    lines = f.readlines()
    last_commit = [line.rstrip() for line in lines][0]
    f.close()

    os.system('cd repo/' + git_folder + ' && git rev-list --max-parents=0 HEAD > ../temp.txt')
    f = open('repo/temp.txt')
    lines = f.readlines()
    first_commit = [line.rstrip() for line in lines][0]
    f.close()

    os.system('cd repo/' + git_folder + ' && git diff --stat ' + first_commit + ' ' + last_commit + ' > ../temp.txt')
    f = open('repo/temp.txt')
    changes = f.readlines()
    if len(changes) > 0:
        changes = changes[-1].split(',')
    else:
        return 0, 0

    insertions = [i.split(' ')[1] for i in changes if i.__contains__('insertions')]
    deletions = [i.split(' ')[1] for i in changes if i.__contains__('deletions')]
    if len(insertions) > 0:
        insertions = int(insertions[0])
    else:
        insertions = 0
    if len(deletions) > 0:
        deletions = int(deletions[0])
    else:
        deletions = 0
    f.close()

    return insertions, deletions


# count number of days from first commit
def days_from_first_commit_repo(git_folder):
    os.system('cd repo/' + git_folder + ' && git log --reverse | grep "Date*" > ../temp.txt')
    f = open('repo/temp.txt')
    commit = f.readlines()[0][12:-7]
    f.close()
    age = (datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%SZ') -
           datetime.datetime.strptime(commit, '%b %d %H:%M:%S %Y')).days

    return age


# count number of days from last commit
def days_from_last_commit_repo(git_folder):
    os.system('cd repo/' + git_folder + ' && git log --name-status HEAD^..HEAD | grep "Date*" > ../temp.txt')
    f = open('repo/temp.txt')
    commit = f.readlines()[0][12:-7]
    f.close()
    age = (datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%SZ') -
           datetime.datetime.strptime(commit, '%b %d %H:%M:%S %Y')).days

    return age


# count README.md length in lines
def readme_length(git_folder):
    os.system('cd repo/' + git_folder + ' && git ls-files | grep ^README.md$ | xargs wc -l > ../temp.txt')
    f = open('repo/temp.txt')
    r_len = f.readlines()[0].split('README.md')[0]

    return int(r_len)


# helper function to get all the pages from request
def get_page(repo_name, link):
    res = requests.get('https://api.github.com/repos/' + repo_name + link + '?per_page=100&state=all', auth=(login, token))
    data = res.json()
    while 'next' in res.links.keys():
        res = requests.get(res.links['next']['url'], auth=(login, token))
        data.extend(res.json())

    return data


# count number of releases and number of unique developers created releases
def count_dev_releases(repo_name):
    releases = get_page(repo_name, '/releases')
    releases_num = len(releases)
    if releases_num < 1:
        return 0, 0

    developers = []
    for r in releases:
        if r['author'] is not None:
            if not developers.__contains__(r['author']['login']):
                developers.append(r['author']['login'])

    return releases_num, len(developers)


# count number of deployments and number of unique developers created deployments
def count_dev_deployments(repo_name):
    deployments = get_page(repo_name, '/deployments')
    deployments_num = len(deployments)
    if deployments_num < 1:
        return 0, 0

    developers = []
    for r in deployments:
        if r['creator'] is not None:
            if not developers.__contains__(r['creator']['login']):
                developers.append(r['creator']['login'])

    return deployments_num, len(developers)


# count number of tags
def count_tags(repo_name):
    tags = get_page(repo_name, '/tags')

    return len(tags)


# count number of branches
def count_branches(repo_name):

    return len(get_page(repo_name, '/branches'))


# count number of contributors
def count_contributors(repo_name):

    return len(get_page(repo_name, '/contributors'))


# count repo size in Kbytes
def repo_size(repo_page):
    size = repo_page['size']

    return size


# count number of languages used
def repo_languages(repo_name):
    response = requests.get('https://api.github.com/repos/' + repo_name + '/languages', auth=(login, token)).json()
    languages = len(response)

    return languages


# count number of watchers
def count_subscribers(repo_page):
    subscribers = repo_page['subscribers_count']

    return subscribers


# count milestones
def count_milestones(repo_name):
    milestones = len(get_page(repo_name, '/milestones'))

    return milestones


# count labels
def count_labels(repo_name):
    labels = len(get_page(repo_name, '/labels'))

    return labels


# count stars
def count_stars(repo_page):
    stars = repo_page['stargazers_count']

    return stars


# count forks
def count_forks(repo_page):
    forks = repo_page['forks']

    return forks


# count topics
def count_topics(repo_page):
    topics = len(repo_page['topics'])

    return topics


# calculate repo age
def repo_age(repo_page):
    creation = repo_page['created_at']
    creation_date_time = datetime.datetime.strptime(creation, '%Y-%m-%dT%H:%M:%SZ')
    now = datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%SZ')
    age = (now - creation_date_time).days

    return age


# count average time to close issues and pull requests
def time_to_close_issues(repo_name):
    closed_issues = get_page(repo_name, '/issues')
    time_issues = []
    time_pulls = []
    iss_res = 0
    pull_res = 0

    for i in closed_issues:
        # print(i['number'])
        if datetime.datetime.strptime(i['closed_at'], '%Y-%m-%dT%H:%M:%SZ') < \
                datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%SZ'):

            time = (datetime.datetime.strptime(i['closed_at'], '%Y-%m-%dT%H:%M:%SZ') -
                    datetime.datetime.strptime(i['created_at'], '%Y-%m-%dT%H:%M:%SZ')).days
            if 'pull_request' in i:
                time_pulls.append(time)
            else:
                time_issues.append(time)
    if len(time_issues) > 0:
        iss_res = statistics.mean(time_issues)
    if len(time_pulls) > 0:
        pull_res = statistics.mean(time_pulls)

    return iss_res, pull_res


# count average number of assets, mentions, and reactions per release
def releases_data(repo_name):
    releases = get_page(repo_name, '/releases')
    if len(releases) < 1:
        return 0, 0, 0

    rel_count = 0
    assets = 0
    mentions = 0
    reactions = 0

    for r in releases:
        if datetime.datetime.strptime(r['created_at'], '%Y-%m-%dT%H:%M:%SZ') < \
                datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%SZ'):
            rel_count += 1
            if 'assets' in r:
                assets += len(r['assets'])
            if 'reactions' in r:
                reactions += r['reactions']['total_count']
            if 'mentions_count' in r:
                mentions += r['mentions_count']
    if rel_count < 1:
        return 0, 0, 0

    assets /= rel_count
    mentions /= rel_count
    reactions /= rel_count

    return assets, mentions, reactions


# get repo owner account type: organization or user
def owner_type(repo_page):

    return repo_page['owner']['type']


# count percentage of usage of main language
def percent_main_lang(repo_name):
    language = requests.get('https://api.github.com/repos/' + repo_name, auth=(login, token)).json()['language']
    langs = get_page(repo_name, '/languages')
    usage = langs[language] / sum([langs[l] for l in langs])

    return usage


# count percentage of signed commits
def signed_commits(git_folder, branch):
    os.system('cd repo/' + git_folder + ' && git checkout `git rev-list -n 1 --before="2022-02-24 00:00" ' + branch + '`')
    os.system('cd repo/' + git_folder + ' && git rev-list --count HEAD > ../temp.txt')
    f = open('repo/temp.txt')
    all_commits = int(f.readlines()[0])
    f.close()

    os.system('cd repo/' + git_folder + ' && git log --show-signature | grep "gpg: Signature made" | wc -l > ../temp.txt')
    f = open('repo/temp.txt')
    signed_commits = int(f.readlines()[0])
    f.close()

    return signed_commits/all_commits


# count number of permissions, conditions and limitations in license
def license_info(repo_page):
    if repo_page['license'] is None or repo_page['license']['url'] is None:
        return '-', '-', '-'

    license = requests.get(repo_page['license']['url'], auth=(login, token)).json()
    permissions = len(license['permissions'])
    conditions = len(license['conditions'])
    limitations = len(license['limitations'])

    return permissions, conditions, limitations


# count percentage of prereleases in releases
def prerelease_percentage(repo_name):
    releases = get_page(repo_name, '/releases')
    if len(releases) < 1:
        return 0

    rel_count = 0
    prerel = 0
    for r in releases:
        if datetime.datetime.strptime(r['created_at'], '%Y-%m-%dT%H:%M:%SZ') < \
                datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%SZ'):
            rel_count += 1
            if r['prerelease']:
                prerel += 1
    if rel_count < 1:
        return 0

    return prerel/rel_count


def main():
    repos = open('repo-list.txt')
    lines = repos.readlines()

    os.mkdir('repo')
    open('repo/temp.txt', 'a').close()

    repo_count = 2
    for line in lines:
        repo_url = line.rstrip()                            # https://github.com/owner/repo
        git_repo = repo_url + '.git'                        # https://github.com/owner/repo.git
        repo_name = repo_url[19:]                           # owner/repo
        git_folder = git_repo.split('/')[-1].split('.git')[0]  # repo
        repo_api = 'https://api.github.com/repos/' + repo_name
        repo_page = requests.get(repo_api, auth=(login, token)).json()

        print(repo_name)
        ####### work with git clone #######

        # clone current repo
        os.system('cd repo && ' + 'git clone ' + git_repo)
        branch = repo_page['default_branch']
        os.system('cd repo/' + git_folder + ' && git checkout ' + branch)

        files, md = count_files_repo(git_folder)
        commits = commits_repo(git_folder)
        rels, dev_r = count_dev_releases(repo_name)
        depls, dev_d = count_dev_deployments(repo_name)
        tags = count_tags(repo_name)
        branches = count_branches(repo_name)
        contributors = count_contributors(repo_name)
        size = repo_size(repo_page)
        subscribers = count_subscribers(repo_page)
        languages = repo_languages(repo_name)
        milestones = count_milestones(repo_name)
        labels = count_labels(repo_name)
        stars = count_stars(repo_page)
        topics = count_topics(repo_page)
        forks = count_forks(repo_page)
        age = repo_age(repo_page)
        days_first_com = days_from_first_commit_repo(git_folder)
        days_last_com = days_from_last_commit_repo(git_folder)
        readme_len = readme_length(git_folder)
        time_to_close_issue, time_to_close_pull = time_to_close_issues(repo_name)
        assets, mentions, reactions = releases_data(repo_name)
        account_type = owner_type(repo_page)
        main_language = percent_main_lang(repo_name)
        percentage_signed_commits = signed_commits(git_folder, branch)
        permissions, conditions, limitations = license_info(repo_page)
        pre_releases = prerelease_percentage(repo_name)

        sheet_name = 'metrics.xlsx'
        wb = load_workbook(sheet_name)

        ### save metrics to file

        wb.save(sheet_name)
        shutil.rmtree('repo/' + git_folder)
        repo_count += 1


main()
