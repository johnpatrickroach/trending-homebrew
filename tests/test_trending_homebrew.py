#!/usr/bin/env python

"""Tests for `trending_homebrew` package."""

import pytest

from click.testing import CliRunner

from trending_homebrew import trending_homebrew
from trending_homebrew import longest
from trending_homebrew import cli

def test_command_line_interface():
    """Test the CLI."""
    runner = CliRunner()
    result = runner.invoke(cli.main)
    assert result.output == '()\n'
    assert result.exit_code == 0
    assert 'trending_homebrew.cli.main' in result.output
    help_result = runner.invoke(cli.main, ['--help'])
    assert help_result.exit_code == 0
    assert '--help  Show this message and exit.' in help_result.output


def test_longest():
    assert longest([b'a', b'bc', b'abc']) == b'abc'
