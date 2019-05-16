import os
import shutil
import subprocess
import argparse
from read_gremlins_logs import parse_line
from multiprocessing import Pool
from time import sleep


parser = argparse.ArgumentParser()

parser.add_argument(
    "--url",
    help="echo the url you use here")
parser.add_argument(
    "--ngen",
    default=10,
    help="echo the number of generations you use here")
parser.add_argument(
    "--npop",
    default=2,
    help="echo the number of population you use here")
parser.add_argument(
    "--nchromo",
    default=2,
    help="echo the number of chromosomes you use here")
parser.add_argument(
    "--headless",
    default=1,
    help="headless evaluation; 0 for no, 1 for yes")



args = parser.parse_args()


def create_if_not_exists(dir):
    if os.path.exists(dir):
        return
    os.mkdir(dir)


def open_file_replace(file_path, old, new):
    with open(file_path, "r") as f:
        content = f.read()
        print(content)
    f.close()

    new_content = content.replace(old, new)

    with open(file_path, "w") as f:
        f.write(new_content)
        print(new_content)
    f.close()


def init_gremlins(blackbox_url, instances, headless, devtools, timeout):
    # clone repo
    repo_url = "https://github.com/karthik3583/gremlinsmonkey"
    gremlins_dir = "gremlinsmonkey"
    print("RUN: {}".format("Locating Gremlins Puppet Repository"))
    if not os.path.exists(gremlins_dir):
        clone_cmd = "git clone {}".format(repo_url)
        print("RUN: {}".format(clone_cmd))
        os.system(clone_cmd)
    else:
        print("Gremlins Puppet Repository Found")

    # start logs flask server
    flask_cmd = "pip install -r requirements.txt && export FLASK_APP=app.py && nohup flask run > noflask.out &"
    print("RUN: {}".format(flask_cmd))
    os.system(flask_cmd)

    # npm install
    chdir_cmd = "cd {} && git pull origin master".format(gremlins_dir)
    install_cmd = "{} && npm install && npm audit fix".format(chdir_cmd)
    print("RUN: {}".format(install_cmd))
    os.system(install_cmd)

    # edit configs
    default_configs_path = "{}/config.default".format(gremlins_dir)
    custom_configs_path = "{}/config".format(gremlins_dir)

    shutil.rmtree(custom_configs_path, ignore_errors=True)
    shutil.copytree(default_configs_path, custom_configs_path)

    # page config file
    page_config_path = "{}/config/page.js".format(gremlins_dir)
    open_file_replace(page_config_path, "http://localhost:8888/home", blackbox_url)

    # gremlins config file
    page_config_path = "{}/config/gremlins.js".format(gremlins_dir)
    open_file_replace(page_config_path, "instances: 100000,", "instances: {},".format(instances))
    open_file_replace(page_config_path, "timeout: 100000,", "timeout: {},".format(timeout))

    # browser config file
    if headless:
        page_config_path = "{}/config/browser.js".format(gremlins_dir)
        open_file_replace(page_config_path, "headless: false,", "headless: true,")

    if devtools:
        page_config_path = "{}/config/browser.js".format(gremlins_dir)
        open_file_replace(page_config_path, "devtools: false,", "devtools: true,")

    # run gremlins
    run_cmd = "{} && nohup npm run start --url {} &".format(chdir_cmd, blackbox_url)
    print("RUN: {}".format(run_cmd))

    p = subprocess.call(run_cmd, shell=True)

    # run evolutionary
    run_cmd = "python utils.py --url {} --ngen {} --npop {}--nchromo {}--headless {}".format(args.url, args.ngen, args.npop, args.nchromo, args.headless)
    print("RUN: {}".format(run_cmd))
    sleep(5*60)
    os.system(run_cmd)


def main():
    init_gremlins(args.url,
                  instances=5,
                  headless=False,
                  devtools=False,
                  timeout=60*60*1)


if __name__ == "__main__":
    main()
