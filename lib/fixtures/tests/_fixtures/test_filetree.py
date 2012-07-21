#  fixtures: Fixtures with cleanups for testing and convenience.
#
# Copyright (c) 2012, Robert Collins <robertc@robertcollins.net>
#
# Licensed under either the Apache License, Version 2.0 or the BSD 3-clause
# license at the users choice. A copy of both licenses are available in the
# project source as Apache-2.0 and BSD. You may not use this file except in
# compliance with one of these two licences.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under these licenses is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  See the
# license you chose for the specific language governing permissions and
# limitations under that license.

import os

from testtools import TestCase
from testtools.matchers import (
    DirContains,
    DirExists,
    FileContains,
    Not,
    )

from fixtures import FileTree
from fixtures._fixtures.filetree import (
    normalize_entry,
    normalize_shape,
    )
from fixtures.tests.helpers import NotHasattr


class TestFileTree(TestCase):

    def test_no_path_at_start(self):
        # FileTree fixture doesn't create a path at the beginning.
        fixture = FileTree([])
        self.assertThat(fixture, NotHasattr('path'))

    def test_creates_directory(self):
        # It creates a temporary directory once set up.  That directory is
        # removed at cleanup.
        fixture = FileTree([])
        fixture.setUp()
        try:
            self.assertThat(fixture.path, DirExists())
        finally:
            fixture.cleanUp()
            self.assertThat(fixture.path, Not(DirExists()))

    def test_creates_files(self):
        # When given a list of file specifications, it creates those files
        # underneath the temporary directory.
        fixture = FileTree([('a', 'foo'), ('b', 'bar')])
        with fixture:
            path = fixture.path
            self.assertThat(path, DirContains(['a', 'b']))
            self.assertThat(os.path.join(path, 'a'), FileContains('foo'))
            self.assertThat(os.path.join(path, 'b'), FileContains('bar'))

    def test_creates_directories(self):
        # When given directory specifications, it creates those directories.
        fixture = FileTree([('a/', None), ('b/',)])
        with fixture:
            path = fixture.path
            self.assertThat(path, DirContains(['a', 'b']))
            self.assertThat(os.path.join(path, 'a'), DirExists())
            self.assertThat(os.path.join(path, 'b'), DirExists())

    def test_simpler_directory_syntax(self):
        # Directory specifications don't have to be tuples. They can be single
        # strings.
        fixture = FileTree(['a/'])
        with fixture:
            path = fixture.path
            self.assertThat(path, DirContains(['a']))
            self.assertThat(os.path.join(path, 'a'), DirExists())

    def test_out_of_order(self):
        # If a file or a subdirectory is listed before its parent directory,
        # that doesn't matter.  We'll create the directory first.
        fixture = FileTree(['a/b/', 'a/'])
        with fixture:
            path = fixture.path
            self.assertThat(path, DirContains(['a']))
            self.assertThat(os.path.join(path, 'a'), DirContains(['b']))
            self.assertThat(os.path.join(path, 'a', 'b'), DirExists())


class TestNormalizeEntry(TestCase):

    def test_file_as_tuple(self):
        # A tuple of filenames and contents is already normalized.
        entry = normalize_entry(('foo', 'foo contents'))
        self.assertEqual(('foo', 'foo contents'), entry)

    def test_directories_as_tuples(self):
        # A tuple of directory name and None is already normalized.
        directory = normalize_entry(('foo/', None))
        self.assertEqual(('foo/', None), directory)

    def test_directories_as_singletons(self):
        # A singleton tuple of directory name is normalized to a 2-tuple of
        # the directory name and None.
        directory = normalize_entry(('foo/',))
        self.assertEqual(('foo/', None), directory)

    def test_directories_as_strings(self):
        # If directories are just given as strings, then they are normalized
        # to tuples of directory names and None.
        directory = normalize_entry('foo/')
        self.assertEqual(('foo/', None), directory)

    def test_filenames_as_strings(self):
        # If file names are just given as strings, then they are normalized to
        # tuples of filenames and made-up contents.
        entry = normalize_entry('foo')
        self.assertEqual(('foo', "The file 'foo'."), entry)


class TestNormalizeShape(TestCase):

    def test_empty(self):
        # The normal form of an empty list is the empty list.
        empty = normalize_shape([])
        self.assertEqual([], empty)

    def test_sorts_entries(self):
        # The normal form a list of entries is the sorted list of normal
        # entries.
        entries = normalize_shape(['a/b/', 'a/'])
        self.assertEqual([('a/', None), ('a/b/', None)], entries)
