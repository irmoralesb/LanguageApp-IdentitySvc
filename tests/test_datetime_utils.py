"""Unit tests for core.datetime_utils."""
from datetime import datetime, timezone

import pytest

from core.datetime_utils import parse_mssql_datetime


def test_parse_none() -> None:
    assert parse_mssql_datetime(None) is None


def test_parse_naive_datetime_to_utc() -> None:
    dt = datetime(2026, 1, 2, 3, 4, 5)
    out = parse_mssql_datetime(dt)
    assert out.tzinfo == timezone.utc
    assert out.year == 2026


def test_parse_tz_aware_to_utc() -> None:
    from datetime import timedelta

    dt = datetime(2026, 1, 2, 3, 4, 5, tzinfo=timezone(timedelta(hours=2)))
    out = parse_mssql_datetime(dt)
    assert out.tzinfo == timezone.utc
    assert out.hour == 1  # 03:00+02 → 01:00 UTC


def test_parse_string_truncates_fractional_digit() -> None:
    s = "2026-02-18 04:02:12.2285367 +00:00"
    out = parse_mssql_datetime(s)
    assert out.microsecond == 228536
    assert out.tzinfo == timezone.utc


def test_parse_string_normalizes_space_before_offset() -> None:
    s = "2026-02-18 04:02:12.228536 +00:00"
    out = parse_mssql_datetime(s)
    assert out.tzinfo == timezone.utc


def test_invalid_type_raises() -> None:
    with pytest.raises(ValueError, match="Cannot parse"):
        parse_mssql_datetime(12345)  # type: ignore[arg-type]
