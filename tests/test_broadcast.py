import pytest

import broadcast


def test_parses_valid_entries_and_skips_invalid_entries(capsys):
    entries = broadcast.build_entries(
        " Creative Server | 25565, Missing port, |25566, Out of range|65536, Survival|25555 "
    )

    assert entries == [("Creative Server", 25565), ("Survival", 25555)]
    assert capsys.readouterr().out.count("[WARN]") == 3


def test_empty_broadcast_input_returns_no_entries():
    assert broadcast.build_entries(" , ") == []


@pytest.mark.parametrize("value", ["abc", "0", "-1", "nan", "inf"])
def test_rejects_invalid_or_non_positive_intervals(value):
    with pytest.raises(ValueError, match="positive number"):
        broadcast.parse_interval(value)


def test_accepts_positive_finite_interval():
    assert broadcast.parse_interval("0.5") == 0.5


def test_cli_options_override_environment(monkeypatch):
    monkeypatch.setenv("BROADCASTS", "Ignored|25565")
    monkeypatch.setenv("BROADCAST_INTERVAL_SECONDS", "10")

    args = broadcast.parse_args(["--broadcast", "CLI|25566", "--interval", "0.5"])

    assert args.entries == [("CLI", 25566)]
    assert args.interval_seconds == 0.5
