from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

"""Tests for code_tasks."""

import numpy as np
import tensorflow as tf

from research.brain_coder.single_task import code_tasks  # brain coder
from research.brain_coder.single_task import defaults  # brain coder


def pad(string, pad_length, pad_char):
    return string + pad_char * (pad_length - len(string))


class CodeTasksTest(tf.test.TestCase):

    def assertClose(self, a, b):
        self.assertTrue(
            np.isclose(a, b, atol=1e-5),
            'Expecting approximately equal values. Got: %s, %s' % (a, b))

    def testMultiIOTaskManager(self):
        maxlen = 100
        padchr = '['
        task = code_tasks.make_task(
            'print', do_code_simplification=False)
        reward_fns = task.rl_batch(1)
        r = reward_fns[0]
        self.assertClose(
            r(pad('++++++++.---.+++++++...', maxlen, padchr)).episode_rewards[-1],
            0.2444)
        self.assertClose(
            r(pad('++++++++.---.+++++++..+++.',
                  maxlen, padchr)).episode_rewards[-1],
            1.0)

        task = code_tasks.make_task(
            'print', do_code_simplification=True)
        reward_fns = task.rl_batch(1)
        r = reward_fns[0]
        self.assertClose(
            r('++++++++.---.+++++++...').episode_rewards[-1],
            0.2444)
        self.assertClose(
            r('++++++++.---.+++++++..+++.').episode_rewards[-1],
            0.935)
        self.assertClose(
            r(pad('++++++++.---.+++++++..+++.',
                  maxlen, padchr)).episode_rewards[-1],
            0.75)

        task = code_tasks.make_task(
            'reverse', do_code_simplification=False)
        reward_fns = task.rl_batch(1)
        r = reward_fns[0]
        self.assertClose(
            r(pad('>,>,>,.<.<.<.', maxlen, padchr)).episode_rewards[-1],
            0.1345)
        self.assertClose(
            r(pad(',[>,]+[,<.]', maxlen, padchr)).episode_rewards[-1],
            1.0)

        task = code_tasks.make_task(
            'reverse', do_code_simplification=True)
        reward_fns = task.rl_batch(1)
        r = reward_fns[0]
        self.assertClose(r('>,>,>,.<.<.<.').episode_rewards[-1], 0.1324)
        self.assertClose(r(',[>,]+[,<.]').episode_rewards[-1], 0.9725)
        self.assertClose(
            r(pad(',[>,]+[,<.]', maxlen, padchr)).episode_rewards[-1],
            0.75)

    def testMakeTask(self):
        maxlen = 100
        padchr = '['
        config = defaults.default_config_with_updates(
            'env=c(config_for_iclr=False,fixed_string=[8,5,12,12,15])')
        task = code_tasks.make_task(config.env, 'print')
        reward_fns = task.rl_batch(1)
        r = reward_fns[0]
        self.assertClose(
            r('++++++++.---.+++++++...').episode_rewards[-1],
            0.2444)
        self.assertClose(
            r('++++++++.---.+++++++..+++.').episode_rewards[-1],
            0.935)
        self.assertClose(
            r(pad('++++++++.---.+++++++..+++.',
                  maxlen, padchr)).episode_rewards[-1],
            0.75)

    def testKnownCodeBaseTask(self):
        maxlen = 100
        padchr = '['
        task = code_tasks.make_task(
            'shift-left', do_code_simplification=False)
        reward_fns = task.rl_batch(1)
        r = reward_fns[0]
        self.assertClose(
            r(pad(',>,[.,]<.,.', maxlen, padchr)).episode_rewards[-1],
            1.0)


if __name__ == '__main__':
    tf.test.main()
