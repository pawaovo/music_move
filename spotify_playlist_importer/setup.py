#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name="spotify-playlist-importer",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "spotipy>=2.19.0",
        "click>=8.0.0",
    ],
    entry_points={
        "console_scripts": [
            "spotify-playlist-importer=spotify_playlist_importer.__main__:main",
        ],
    },
) 