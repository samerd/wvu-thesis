'''
Created on Apr 5, 2020

@author: Samir Deeb
'''

import base64
import getpass
import json
import os
from urllib.error import URLError
import urllib.request

from thesis import get_dataset_dir

projects = [
    "accumulo",
    "ambari",
    "atlas",
    "aurora",
    "batik",
    "commons-bcel",
    "beam",
    "commons-beanutils",
    "cocoon",
    "commons-codec",
    "commons-collections",
    "commons-cli",
    "commons-exec",
    "commons-fileupload",
    "commons-io",
    "commons-jelly",
    "commons-jexl",
    "commons-configuration",
    "commons-daemon",
    "commons-dbcp",
    "commons-dbutils",
    "commons-digester",
    "felix",
    "httpcomponents-client",
    "httpcomponents-core",
    "commons-jxpath",
    "commons-net",
    "commons-ognl",
    "santuario",
    "mina-sshd",
    "commons-validator",
    "commons-vfs",
    "zookeeper",
]


class GitHubComm:

    def __init__(self, pwd):
        self.base_url = "https://api.github.com/repos/apache/"
        credentials = ('%s:%s' % ("samerd", pwd))
        self.encoded_credentials = base64.b64encode(
            credentials.encode('ascii'))

        self.opener = urllib.request.build_opener()

    def _auth_req(self, url):
        req = urllib.request.Request(url)
        req.add_header('Authorization',
                       'Basic %s' % self.encoded_credentials.decode("ascii"))
        return req

    def get_tags(self, project):
        page = 1
        done = False
        tags = list()
        while not done:
            git_project = project
            if project == "santuario":
                git_project = "santuario-java"
            url = self.base_url + "%s/tags?page=%d" % (git_project, page)
            req = self._auth_req(url)
            try:
                with self.opener.open(req) as response:
                    data_str = response.read()
            except URLError as exc:
                print("Tags Request failed for %s: %s" % (url, str(exc)))
                break

            data = json.loads(data_str)
            for tag in data:
                tag_name = tag["name"]
                commit_url = tag["commit"]["url"]
                req = self._auth_req(commit_url)
                try:
                    with self.opener.open(req) as response:
                        data_str = response.read()
                except URLError as exc:
                    print("Request failed for %s: %s" % (commit_url, str(exc)))
                    continue
                commit_data = json.loads(data_str)
                commit_date = commit_data["commit"]["author"]["date"]
                tags.append((project, tag_name, commit_date))
            if not data:
                done = True
            else:
                page += 1
        return tags


if __name__ == "__main__":
    data_dir = get_dataset_dir()
    passwd = getpass.getpass("Please enter github password:")

    comm = GitHubComm(passwd)
    filep = open(os.path.join(data_dir, "project_releases.csv"), "a")
    for proj in projects:
        print("handing project:", proj)
        g_tags = comm.get_tags(proj)
        for _, g_tag_name, g_commit_date in g_tags:
            filep.write("%s,%s,%s\n" % (proj, g_tag_name, g_commit_date))
        filep.flush()
    filep.close()
