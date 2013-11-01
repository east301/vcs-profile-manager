#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import argparse
import ConfigParser
import os
import sys
import yaml


DEFAULT_PROFILE_DIRECTORIES = (
    os.path.dirname(os.path.abspath(__file__)),
    os.path.expanduser('~/.vcsprofile'),
)


def vcs_name(text):
    name = text.lower()
    if name in ('git', 'mercurial'): return name

    raise ValueError('Unsupported VCS name "{}" specified.'.format(name))


def _main():
    """DOCUMENT ME"""

    # parses command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--profile-directory')
    parser.add_argument('--profile-prefix')

    sub_parsers = parser.add_subparsers()
    sub_parser = sub_parsers.add_parser('change')
    sub_parser.set_defaults(which='change')
    sub_parser.add_argument('vcs', type=vcs_name)
    sub_parser.add_argument('template')
    sub_parser.add_argument('profile')
    sub_parser.add_argument('output')

    sub_parser = sub_parsers.add_parser('list')
    sub_parser.set_defaults(which='list')
    sub_parser.add_argument('vcs', type=vcs_name)
    args = parser.parse_args()

    # loads profiles for the specified VCS
    profiles = _find_available_profiles(args.vcs, args.profile_directory, args.profile_prefix)

    #
    if args.which == 'change':
        config = _load_template(args.template)
        profile_name, profile = _find_profile_by_name(profiles, args.profile)

        print 'Applying the profile "{}"...'.format(profile_name)
        _apply_profile(config, profile)
        _write_config(config, args.output)

    elif args.which == 'list':
        if profiles:
            print 'The following profiles are available for {}.'.format(args.vcs)

            for key in profiles.keys():
                print '* {}'.format(key)

        else:
            print 'No profile is available for {}'.format(args.vcs)


def _find_available_profiles(vcs, profile_directory, profile_prefix):
    """DOCUMENT ME"""

    if profile_directory:
        profile_dirs = [profile_directory]
    else:
        profile_dirs = DEFAULT_PROFILE_DIRECTORIES

    if profile_prefix is None:
        profile_prefix = ''

    profiles = {}
    for profile_dir in profile_dirs:
        if not os.path.exists(profile_dir): continue

        for file_name in os.listdir(profile_dir):
            file_path = os.path.join(profile_dir, file_name)
            file_ext = os.path.splitext(file_path)[1].lower()

            if (file_ext in ('.yml', '.yaml')) and file_name.startswith(profile_prefix):
                profiles.update(_load_profiles_from_file(file_path))

    return profiles


def _load_profiles_from_file(path):
    """DOCUMENT ME"""

    with open(path) as fin:
        profiles = yaml.load(fin.read().decode('UTF-8'))

    if profiles is None:
        return {}

    if not isinstance(profiles, dict):
        raise ValueError('Top level component of VCS profile must be dict.')

    return profiles


def _load_template(path):
    """DOCUMENT ME"""

    with open(path) as fin:
        cp = ConfigParser.ConfigParser()
        cp.readfp(fin)
        return cp


def _find_profile_by_name(profiles, name):
    """DOCUMENT ME"""

    for key, value in profiles.items():
        if key.startswith(name):
            return key, value

    raise ValueError('The specified profile "{}" is not found.'.format(name))


def _apply_profile(config, profile):
    """DOCUMENT ME"""

    for section, pairs in profile.items():
        for key, value in pairs.items():
            if not config.has_section(section):
                config.add_section(section)

            config.set(section, key, value)


def _write_config(config, path):
    """DOCUMENT ME"""

    with open(path, 'w') as fout:
        config.write(fout)


if __name__ == '__main__':
    _main()
