"""Tests for :func:`validkit.clamp`."""

import pytest

from validkit import clamp


class TestClamp:
    """Normal, boundary and error cases for clamp."""

    @pytest.mark.parametrize(
        ("value", "low", "high", "expected"),
        [
            (5, 0, 10, 5),
            (-3, 0, 10, 0),
            (15, 0, 10, 10),
            (2.5, 1, 3, 2.5),
        ],
    )
    def test_clamps_into_interval(
        self, value: float | int, low: float | int, high: float | int, expected: float | int
    ) -> None:
        assert clamp(value, low, high) == expected

    def test_int_stays_int(self) -> None:
        result = clamp(5, 0, 10)
        assert result == 5
        assert isinstance(result, int)

        result = clamp(-3, 0, 10)
        assert result == 0
        assert isinstance(result, int)

        result = clamp(15, 0, 10)
        assert result == 10
        assert isinstance(result, int)

    def test_float_stays_float(self) -> None:
        result = clamp(2.5, 1, 3)
        assert result == 2.5
        assert isinstance(result, float)

    @pytest.mark.parametrize(
        ("value", "low", "high", "expected"),
        [
            (0, 0, 10, 0),  # value equals low
            (10, 0, 10, 10),  # value equals high
            (1, 1, 3, 1),  # low equals value
            (3, 1, 3, 3),  # high equals value
            (1, 1, 1, 1),  # single-point interval
            (-10, -10, -10, -10),  # negative single-point interval
            (0, -5, 0, 0),
        ],
    )
    def test_boundary_values(
        self, value: float | int, low: float | int, high: float | int, expected: float | int
    ) -> None:
        assert clamp(value, low, high) == expected

    @pytest.mark.parametrize(
        "args",
        [
            ("5", 0, 10),
            (5, "0", 10),
            (5, 0, "10"),
            (True, 0, 10),
            (5, True, 10),
            (5, 0, True),
            (None, 0, 10),
            (5, None, 10),
            (5, 0, None),
            ([5], 0, 10),
            (5.0, [0], 10),
        ],
    )
    def test_non_numeric_raises_type_error(self, args: tuple) -> None:
        with pytest.raises(TypeError):
            clamp(*args)  # type: ignore[arg-type]

    @pytest.mark.parametrize(("low", "high"), [(5, 3), (1, 0), (0.5, 0.0), (3, -2)])
    def test_low_greater_than_high_raises_value_error(
        self, low: float | int, high: float | int
    ) -> None:
        with pytest.raises(ValueError):
            clamp(1, low, high)

    def test_error_messages_do_not_leak_input(self) -> None:
        with pytest.raises(TypeError) as excinfo:
            clamp("5", 0, 10)  # type: ignore[arg-type]
        assert "5" not in str(excinfo.value)

        with pytest.raises(ValueError) as excinfo:
            clamp(1, 5, 3)
        assert "5" not in str(excinfo.value)
        assert "3" not in str(excinfo.value)
