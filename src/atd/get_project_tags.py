'''
Created on Apr 5, 2020

@author: Samir Deeb
'''

import base64
import json
import os
import urllib.request
import getpass

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
            except Exception as e:
                print("Tags Request failed for %s: %s" % (url, str(e)))
                break

            data = json.loads(data_str)
            for tag in data:
                tag_name = tag["name"]
                commit_url = tag["commit"]["url"]
                req = self._auth_req(commit_url)
                try:
                    with self.opener.open(req) as response:
                        data_str = response.read()
                except Exception as e:
                    print("Request failed for %s: %s" % (commit_url, str(e)))
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
    curr_dir = os.path.dirname(__file__)
    data_dir = os.path.join(os.pardir, os.pardir, "dataset")
    data_dir = os.path.normpath(data_dir)
    passwd = getpass.getpass("Please enter github password:")

    comm = GitHubComm(passwd)
    fp = open(os.path.join(data_dir, "project_releases.csv"), "a")
    for project in projects:
        print("handing project:", project)
        tags = comm.get_tags(project)
        for project, tag_name, commit_date in tags:
            fp.write("%s,%s,%s\n" % (project, tag_name, commit_date))
        fp.flush()
    fp.close()
