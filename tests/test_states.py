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


def test_saved_state_holds_the_post_filter_aggregation(td):
    """A checkpoint records the files the filter selected, labelled with that filter."""
    td.filter_by_max_chars(50)

    state = td.aggregation_states[1]

    assert len(state.aggregation) == len(td.aggregation) == 5
    assert state.applied_filters == ['filter_by_max_chars']


def test_current_state_is_a_valid_index(td):
    """current_state always addresses an existing state, so it can be reloaded."""
    td.filter_by_max_chars(50)

    assert td.current_state == len(td.aggregation_states) - 1

    # Reloading the current state is a no-op rather than an error
    td.load_aggregation_state(td.current_state)
    assert len(td.aggregation) == 5


def test_loaded_state_is_not_aliased(td):
    """Filtering after restoring a state does not rewrite the saved state."""
    td.filter_by_max_chars(500)
    labels_before = list(td.aggregation_states[1].applied_filters)

    td.load_aggregation_state(1)
    td.filter_by_min_chars(1)

    assert td.aggregation_states[1].applied_filters == labels_before


def test_failed_filter_records_no_state(testdata_dir):
    """A filter that raises leaves the checkpoint history untouched."""
    from textdirectory.textdirectory import TextDirectory

    td = TextDirectory(directory=testdata_dir, disable_tqdm=True)
    td.load_files(recursive=True, filetype='txt', fast=True)
    states_before = len(td.aggregation_states)

    with pytest.raises(ValueError):
        td.filter_by_max_chars(1)

    assert len(td.aggregation_states) == states_before
    assert td.applied_filters == []


def test_aggregation_state_is_tuple_compatible(td):
    """States still support the [aggregation, applied_filters] indexing used before 0.4.1."""
    td.filter_by_max_chars(50)
    state = td.aggregation_states[1]

    assert state[0] == state.aggregation
    assert state[1] == state.applied_filters


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
