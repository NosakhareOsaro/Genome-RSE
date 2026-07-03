import numpy as np
import pytest

from app.features import (
    ALPHABET,
    FEATURE_LENGTH,
    SEQUENCE_LENGTH,
    UnknownSymbolError,
    encode_sequence,
    encode_sequences,
)


def test_encode_sequence_shape_and_dtype() -> None:
    sequence = "A" * SEQUENCE_LENGTH
    encoded = encode_sequence(sequence)
    assert encoded.shape == (FEATURE_LENGTH,)
    assert encoded.dtype == np.float32


def test_encode_sequence_one_hot_per_position() -> None:
    sequence = "AC" + "G" * (SEQUENCE_LENGTH - 2)
    encoded = encode_sequence(sequence).reshape(SEQUENCE_LENGTH, len(ALPHABET))
    assert encoded[0, ALPHABET.index("A")] == 1.0
    assert encoded[0].sum() == 1.0
    assert encoded[1, ALPHABET.index("C")] == 1.0
    assert encoded[2, ALPHABET.index("G")] == 1.0


def test_encode_sequence_is_case_insensitive() -> None:
    upper = encode_sequence("A" * SEQUENCE_LENGTH)
    lower = encode_sequence("a" * SEQUENCE_LENGTH)
    assert np.array_equal(upper, lower)


def test_encode_sequence_handles_ambiguity_codes() -> None:
    sequence = "N" + "A" * (SEQUENCE_LENGTH - 1)
    encoded = encode_sequence(sequence).reshape(SEQUENCE_LENGTH, len(ALPHABET))
    assert encoded[0, ALPHABET.index("N")] == 1.0


def test_encode_sequence_wrong_length_raises() -> None:
    with pytest.raises(ValueError, match="expected a 60-nucleotide sequence"):
        encode_sequence("ACGT")


def test_encode_sequence_unknown_symbol_raises() -> None:
    sequence = "X" + "A" * (SEQUENCE_LENGTH - 1)
    with pytest.raises(UnknownSymbolError, match="not in the known alphabet"):
        encode_sequence(sequence)


def test_encode_sequences_batch() -> None:
    sequences = ["A" * SEQUENCE_LENGTH, "C" * SEQUENCE_LENGTH]
    encoded = encode_sequences(sequences)
    assert encoded.shape == (2, FEATURE_LENGTH)
