import numpy as np
import pytest

from lib.sign_lookup import (
    FEATURE_DIM,
    cosine_distance,
    resample_sequence,
    sequence_to_feature,
    top_k_matches,
)


def test_resample_sequence_preserves_length_and_endpoints():
    seq = np.stack([np.full(FEATURE_DIM, v) for v in [0.0, 1.0, 2.0, 3.0, 4.0]])
    resampled = resample_sequence(seq, length=30)
    assert resampled.shape == (30, FEATURE_DIM)
    assert resampled[0, 0] == pytest.approx(0.0)
    assert resampled[-1, 0] == pytest.approx(4.0)


def test_resample_sequence_empty_input_returns_zeros():
    empty = resample_sequence(np.zeros((0, FEATURE_DIM)))
    assert empty.shape == (30, FEATURE_DIM)
    assert np.all(empty == 0)


def test_resample_sequence_single_frame_repeats():
    single = np.full((1, FEATURE_DIM), 7.0)
    resampled = resample_sequence(single, length=10)
    assert resampled.shape == (10, FEATURE_DIM)
    assert np.all(resampled == 7.0)


def test_sequence_to_feature_shape():
    seq = np.random.rand(12, FEATURE_DIM)
    feature = sequence_to_feature(seq)
    assert feature.shape == (30 * FEATURE_DIM,)


def test_cosine_distance_identical_vectors_is_zero():
    a = np.array([1.0, 0.0, 0.0])
    assert cosine_distance(a, a) == pytest.approx(0.0)


def test_cosine_distance_orthogonal_vectors_is_one():
    a = np.array([1.0, 0.0, 0.0])
    b = np.array([0.0, 1.0, 0.0])
    assert cosine_distance(a, b) == pytest.approx(1.0)


def test_cosine_distance_zero_vector_does_not_crash():
    a = np.zeros(3)
    b = np.array([1.0, 0.0, 0.0])
    assert cosine_distance(a, b) == 1.0


def test_top_k_matches_ranks_closest_first():
    query = np.array([1.0, 0.0, 0.0])
    reference = {
        "hello": [np.array([0.9, 0.1, 0.0])],
        "thanks": [np.array([0.0, 1.0, 0.0])],
        "yes": [np.array([1.0, 0.0, 0.0])],
    }
    ranked = top_k_matches(query, reference, k=3)
    assert ranked[0][0] == "yes"
    assert ranked[0][1] == pytest.approx(0.0)
    assert [label for label, _ in ranked] == ["yes", "hello", "thanks"]


def test_top_k_matches_uses_best_example_per_label():
    # A label with multiple example clips should be scored by its closest
    # example, not averaged or by the first one in the list.
    query = np.array([1.0, 0.0, 0.0])
    reference = {
        "mixed": [np.array([0.0, 1.0, 0.0]), np.array([1.0, 0.0, 0.0])],
    }
    ranked = top_k_matches(query, reference, k=1)
    assert ranked[0] == ("mixed", pytest.approx(0.0))


def test_top_k_matches_respects_k():
    query = np.array([1.0, 0.0, 0.0])
    reference = {f"label{i}": [np.array([1.0, 0.0, 0.0])] for i in range(10)}
    ranked = top_k_matches(query, reference, k=3)
    assert len(ranked) == 3
