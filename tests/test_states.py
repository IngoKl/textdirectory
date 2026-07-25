"""Tests for saving and loading aggregation states (checkpoints)."""

import pytest


def test_save_aggregation_state(td):
    """Loading files creates the initial checkpoint; filters add more."""
    assert len(td.aggregation_states) == 1

    td.filter_by_max_chars(50)

    assert len(td.aggregation_states) == 2


def test_load_aggregation_state_roundtrip(td):
    """A previous aggregation state can be restored."""
    files_before = len(td.aggregation)

    td.filter_by_max_chars(50)
    assert len(td.aggregation) < files_before

    td.load_aggregation_state(0)

    assert len(td.aggregation) == files_before
    assert td.current_state == 0


def test_load_aggregation_state_invalid_raises(td):
    """Loading a non-existent state raises a ValueError."""
    with pytest.raises(ValueError):
        td.load_aggregation_state(99)


def test_print_saved_states(td, capsys):
    """print_saved_states lists the saved checkpoints."""
    td.filter_by_max_chars(50)
    td.print_saved_states()

    out, err = capsys.readouterr()
    assert 'Saved States:' in out
    assert '[0]' in out
    assert '[1]' in out
