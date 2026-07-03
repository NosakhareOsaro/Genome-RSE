"""Sequence -> feature vector encoding.

Lives in ``app/`` (not ``training/``) even though it's used by both,
because the *serving* container only ships the ``app`` package (see
``.dockerignore`` / ``Dockerfile``) and must be able to turn an incoming
request's raw sequence into the exact same feature vector shape the model
was trained on, with no MLflow/pandas dependency. ``training/train.py``
imports from here rather than re-implementing the encoding, so training
and serving can never silently drift apart.
"""

from __future__ import annotations

import numpy as np

SEQUENCE_LENGTH = 60

# The observed alphabet in the UCI splice-junction dataset: the four
# standard nucleotides plus four IUPAC ambiguity codes that appear in a
# handful of instances (see data/DATA_SOURCE.md). Fixed and sorted so
# encoding is deterministic across training and inference.
ALPHABET = ("A", "C", "D", "G", "N", "R", "S", "T")
_SYMBOL_INDEX = {symbol: index for index, symbol in enumerate(ALPHABET)}

FEATURE_LENGTH = SEQUENCE_LENGTH * len(ALPHABET)


class UnknownSymbolError(ValueError):
    """Raised when a sequence contains a symbol outside ``ALPHABET``."""


def encode_sequence(sequence: str) -> np.ndarray:
    """One-hot encode a single 60-nucleotide sequence.

    Returns a flat ``float32`` vector of length ``FEATURE_LENGTH``
    (60 positions x 8 symbols), position-major: the one-hot block for
    position 0 comes first, then position 1, and so on.
    """
    sequence = sequence.upper()
    if len(sequence) != SEQUENCE_LENGTH:
        raise ValueError(f"expected a {SEQUENCE_LENGTH}-nucleotide sequence, got {len(sequence)}")
    encoded = np.zeros((SEQUENCE_LENGTH, len(ALPHABET)), dtype=np.float32)
    for position, symbol in enumerate(sequence):
        try:
            encoded[position, _SYMBOL_INDEX[symbol]] = 1.0
        except KeyError as exc:
            raise UnknownSymbolError(
                f"position {position}: symbol {symbol!r} is not in the "
                f"known alphabet {ALPHABET}"
            ) from exc
    return encoded.reshape(-1)


def encode_sequences(sequences: list[str]) -> np.ndarray:
    """One-hot encode a batch of sequences into a 2D feature matrix."""
    return np.stack([encode_sequence(sequence) for sequence in sequences])
