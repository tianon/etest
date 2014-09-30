# Copyright (C) 2014 by Alex Brandt <alunduil@alunduil.com>
#
# etest is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

import itertools
import logging
import os

from etest import overlay

logger = logging.getLogger(__name__)


class Test(object):
    def __init__(self, ebuild, test = False, **kwargs):
        pass


class Tests(object):
    def __init__(self, ebuild_filter = ()):
        self.overlay = overlay.Overlay()

        # NOTE: raises InvalidOverlayError when necessary
        logger.debug('self.overlay.directory: %s', self.overlay.directory)

        self.ebuild_filter = [ _.replace('.ebuild', '') for _ in ebuild_filter ]

        if not len(self.ebuild_filter):
            logger.debug('os.getcwd(): %s', os.getcwd())
            logger.debug('os.path.relpath(self.overlay.directory): %s', os.path.relpath(self.overlay.directory))

            _ = os.path.relpath(self.overlay.directory)

            if _.startswith('..'):
                self.ebuild_filter.append(os.getcwd().replace(self.overlay.directory, '').strip('/'))

    @property
    def tests(self):
        if not hasattr(self, '_tests'):
            logger.info('STARTING: populate tests')

            self._tests = []

            for ebuild in self.overlay.ebuilds:
                if not len(self.ebuild_filter) or any([ _ in ebuild.name for _ in self.ebuild_filter ]):
                    self._tests.extend(self._generate_tests(ebuild))

            logger.info('STOPPING: populate tests')

        return self._tests

    def _generate_tests(self, ebuild):
        '''Generate all tests for a given ebuild.

        Prepare all tests for a given ebuild so they are ready to be run.  This
        includes finding the powerset of the USE flags and creating a runtime
        for each combination among other things.  It also includes setting
        appropriate environment variables (i.e. PYTHON_TARGETS=PYTHON_COMPAT).

        .. note::
            Later, we will add support for a test specification file to modify
            the set of tests generated by this function.

        Arguments
        ---------

        :``ebuild``: Ebuild to inspect and create various test cases for

        Returns
        -------

        Tuple of Test objects.

        '''

        logger.info('STARTING: generate tests for %s', ebuild.name)

        tests = []

        use_flags = list(ebuild.use_flags)
        use_flags.remove('test')

        logger.debug('ebuild.use_flags: %s', ebuild.use_flags)

        for use_flags_combination in itertools.chain.from_iterable(itertools.combinations(use_flags, _) for _ in range(len(use_flags) + 1)):
            logger.info('adding %s[%s]', ebuild.name, ','.join(use_flags_combination))

            tests.append(Test(ebuild, use_flags = use_flags_combination))

            logger.info('adding %s[test,%s]', ebuild.name, ','.join(use_flags_combination))

            tests.append(Test(ebuild, test = True, use_flags = use_flags_combination))

        logger.info('STOPPING: generate tests for %s', ebuild.name)

        return tests
