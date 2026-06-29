"""Tests for pymice.help."""

from __future__ import annotations

import pytest

from pymice import help, help_topics, mice


def test_help_package_overview(capsys):
    text = help(print_=False)
    assert "pymice(package)" in text
    assert "Description" in text
    assert "mice" in text


def test_help_dataset_nhanes():
    text = help("nhanes", print_=False)
    assert "nhanes(dataset)" in text
    assert "age" in text
    assert "chl" in text


def test_help_function_mice():
    text = help("mice", print_=False)
    assert "mice(function)" in text
    assert "maxit" in text


def test_help_callable_topic():
    text = help(mice, print_=False)
    assert "mice(function)" in text


def test_help_question_mark_alias():
    text = help("?boys", print_=False)
    assert "boys(dataset)" in text


def test_help_ampute():
    text = help("ampute", print_=False)
    assert "ampute(function)" in text
    assert "MCAR" in text


def test_help_unknown_raises():
    with pytest.raises(KeyError):
        help("not_a_topic", print_=False)


def test_help_topics_sorted():
    topics = help_topics()
    assert "nhanes" in topics
    assert "mice" in topics
    assert topics == sorted(topics, key=str.lower)


def test_help_prints_to_stdout(capsys):
    help("nhanes")
    captured = capsys.readouterr()
    assert "nhanes(dataset)" in captured.out
