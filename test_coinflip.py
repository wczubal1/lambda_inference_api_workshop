import os
import time
from datetime import datetime
import re
import pytest
import coinflip
import builtins

def test_validate_flips():
    # Valid coin flip string of exactly 10 chars, only H or T.
    valid_flip = "HTHTHTHTHT"
    assert coinflip.validate_flips(valid_flip) is True

    # Invalid: wrong length
    invalid_flip = "HTHTHTHTH"
    assert coinflip.validate_flips(invalid_flip) is False

    # Invalid: contains a bad character
    invalid_flip2 = "HTHTHTHXHT"
    assert coinflip.validate_flips(invalid_flip2) is False

def test_run_coin_flip_simulation(capsys, monkeypatch, tmp_path):
    # Monkeypatch datetime to generate a predictable filename.
    fixed_time = datetime(2023, 1, 1, 12, 0, 0)
    class DummyDatetime(datetime):
        @classmethod
        def now(cls):
            return fixed_time
    monkeypatch.setattr(coinflip, "datetime", DummyDatetime)

    # Redirect the file write to a temporary directory.
    temp_file_path = tmp_path / "coin_flip_results_20230101_12000000.txt"
    original_open = builtins.open  # Save original open

    def dummy_open(filename, mode):
        return original_open(temp_file_path, mode)

    monkeypatch.setattr(builtins, "open", dummy_open)

    # Run the simulation using the actual autogen implementation.
    coinflip.run_coin_flip_simulation()

    # Capture printed output.
    captured = capsys.readouterr().out

    # Check that there are 5 full response prints.
    full_response_matches = re.findall(r"Simulation \d+ full response:", captured)
    processed_result_matches = re.findall(r"Simulation \d+ processed result:", captured)
    assert len(full_response_matches) == 5
    assert len(processed_result_matches) == 5

    # Read the written file and check its contents.
    assert temp_file_path.exists()
    contents = temp_file_path.read_text()
    # Verify that the file contains coin flip details for 5 simulations.
    simulation_lines = re.findall(r"Simulation \d+.*", contents)
    # Expecting 5 entries (one per simulation) containing a coin flip sequence.
    validated_results = [line for line in simulation_lines if "HT" in line]
    assert len(validated_results) == 5