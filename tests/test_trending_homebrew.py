#!/usr/bin/env python

"""Tests for `trending_homebrew` package."""

from click.testing import CliRunner

from trending_homebrew import trending_homebrew
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


def test_trending_homebrew():
    """Test trending_homebrew."""
    assert trending_homebrew.DATA_DAY_RANGES == ["365", "90", "30"]
