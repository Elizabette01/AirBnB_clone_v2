#!/usr/bin/python3
import os
from fabric.api import *
from datetime import datetime
from fabric.decorators import runs_once
from fabric.operations import run, put, sudo

env.hosts = ['18.234.80.200', '3.83.18.58']
env.user = 'ubuntu'
env.key_filename = '~/.ssh/school'


"""Fabric script that generates a .tgz archive
from the contents of the web_static folder."""


def do_pack():
    """Generates .tgz archive from the contents of the web_static folder."""
    local("mkdir -p versions")
    path = "versions/web_static_{}.tgz".format(
            datetime.strftime(datetime.now(), "%Y%m%d%H%M%S"))
    result = local("tar -czf {} web_static".format(path))
    if result.failed:
        return None
    return path


"""Fabric script (based on the file 1-pack_web_static.py)
that distributes an archive to your web servers, using the function do_deploy.
"""


def do_deploy(archive_path):
    """Distributes an archive to your web servers."""

    if os.path.isfile(archive_path) is False:
        return False
    try:
        archive = archive_path.split("/")[-1]
        t_stamp = archive.split(".")[0]
        path = "/data/web_static/releases/"

        # Upload archive to web server
        put(archive_path, '/tmp/')

        # Creating target directory.
        run('sudo mkdir -p {}{}/'.format(path, t_stamp))

        # Uncompressing and deleting the archive to the newly created folder.
        run('sudo tar -xzf /tmp/{} -C {}{}/'.format(archive, path, t_stamp))
        run('sudo rm /tmp/{}'.format(archive))
        run('sudo mv {0}{1}/web_static/* {0}{1}/'.format(path, t_stamp))
        run('sudo rm -rf {}{}/web_static'.format(path, t_stamp))

        # Deleting symbolic link from the web server
        run('sudo rm -rf /data/web_static/current')

        # Creating new symbolic link
        run('sudo ln -s {}{}/ /data/web_static/current'.format(path, t_stamp))
        return True
    except Exception:
        return False


def deploy():
    """creates and distributes an archive to my wb servers"""

    archive_path = do_pack()
    if archive_path is None:
        return False
    return do_deploy(archive_path)
