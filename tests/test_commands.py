#! /usr/bin/python3
# -*- coding: utf-8 -*-

##############################################################################
#    Copyright (C) 2021-current alexpdev
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
##############################################################################
"""
Testing functions for the sub-action commands from command line args.
"""
import os
import sys
from hashlib import sha1  # nosec
from urllib.parse import quote_plus

import pyben
import pytest

from tests import dir1, metafile, rmpath, tfile
from torrentfile.cli import execute
from torrentfile.commands import info, magnet


def test_fix():
    """
    Test dir1 fixture is not None.
    """
    assert dir1 and metafile and tfile


def test_magnet_uri(metafile):
    """
    Test create magnet function digest.
    """
    magnet_link = magnet(metafile)
    meta = pyben.load(metafile)
    announce = meta["announce"]
    assert quote_plus(announce) in magnet_link


def test_magnet_hex(metafile):
    """
    Test create magnet function digest.
    """
    magnet_link = magnet(metafile)
    meta = pyben.load(metafile)
    info = meta["info"]
    binfo = sha1(pyben.dumps(info)).hexdigest().upper()
    assert binfo in magnet_link


def test_magnet(metafile):
    """
    Test create magnet function scheme.
    """
    magnet_link = magnet(metafile)
    assert magnet_link.startswith("magnet")


def test_magnet_no_announce_list(metafile):
    """
    Test create magnet function scheme.
    """
    meta = pyben.load(metafile)
    del meta["announce-list"]
    pyben.dump(meta, metafile)
    magnet_link = magnet(metafile)
    assert magnet_link.startswith("magnet")


def test_magnet_empty():
    """
    Test create magnet function scheme.
    """
    try:
        magnet("file_that_does_not_exist")
    except FileNotFoundError:
        assert True


@pytest.mark.parametrize(
    "field",
    ["name", "announce", "source", "comment", "private", "announce-list"],
)
def test_info(field, tfile):
    """
    Test the info_command action from the Command Line Interface.
    """
    args = [
        "torrentfile",
        "create",
        "-t",
        "url1",
        "url2",
        "url3",
        "--private",
        "--comment",
        "ExampleComment",
        "--source",
        "examplesource",
        str(tfile),
    ]
    sys.argv = args
    execute()

    class Space:
        """
        Stand in substitution for argparse.Namespace object.
        """

        metafile = str(tfile) + ".torrent"

    output = info(Space)
    assert field in output
    rmpath(str(tfile) + ".torrent")


def test_magnet_cli(metafile):
    """
    Test magnet creation through CLI interface.
    """
    sys.argv[1:] = ["m", str(metafile)]
    uri = execute()
    assert "magnet" in uri


def test_create_unicode_name(tfile):
    """
    Test Unicode information in CLI args.
    """
    parent = os.path.dirname(tfile)
    filename = os.path.join(parent, "丂七万丈三与丏丑丒专且丕世丗両丢丣两严丩个丫丬中丮丯.torrent")
    args = [
        "torrentfile",
        "-v",
        "create",
        "-a",
        "tracker_url.com/announce_3456",
        "tracker_url.net/announce_3456",
        "--source",
        "sourcetext",
        "--comment",
        "filename is 丂七万丈三与丏丑丒专且丕世丗両丢丣两严丩个丫丬中丮丯.torrent",
        "-o",
        str(filename),
        str(tfile),
    ]
    sys.argv = args
    execute()
    assert os.path.exists(filename)
