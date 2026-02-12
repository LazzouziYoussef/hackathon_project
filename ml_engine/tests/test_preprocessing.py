from datetime import datetime, timedelta
import sys
import os
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.time_utils import RamadanCalendar
from preprocessing.data_loader import MetricsDataLoader


class MockDBConnection:
    def __init__(self, rows):
        self.rows = rows
    
    def fetch_all(self, query, *args):
        return self.rows


def test_ramadan_calendar():
    # Test 2026 Ramadan dates
    test_date = datetime(2026, 3, 1)
    assert RamadanCalendar.is_ramadan(test_date, 2026) == True
    
    day = RamadanCalendar.get_ramadan_day(test_date, 2026)
    assert day is not None and day == 13
    print(f"✅ Ramadan 2026 mid-month: Day {day}")
    
    # Test boundaries for 2026
    ramadan_start_2026 = datetime(2026, 2, 17)
    assert RamadanCalendar.is_ramadan(ramadan_start_2026, 2026) == True
    assert RamadanCalendar.get_ramadan_day(ramadan_start_2026, 2026) == 1
    print("✅ Ramadan 2026 start: Day 1")
    
    ramadan_end_2026 = datetime(2026, 3, 18)
    assert RamadanCalendar.is_ramadan(ramadan_end_2026, 2026) == True
    assert RamadanCalendar.get_ramadan_day(ramadan_end_2026, 2026) == 30
    print("✅ Ramadan 2026 end: Day 30")
    
    before_ramadan_2026 = datetime(2026, 2, 16)
    assert RamadanCalendar.is_ramadan(before_ramadan_2026, 2026) == False
    assert RamadanCalendar.get_ramadan_day(before_ramadan_2026, 2026) is None
    print("✅ Before Ramadan 2026: Not Ramadan")
    
    after_ramadan_2026 = datetime(2026, 3, 19)
    assert RamadanCalendar.is_ramadan(after_ramadan_2026, 2026) == False
    assert RamadanCalendar.get_ramadan_day(after_ramadan_2026, 2026) is None
    print("✅ After Ramadan 2026: Not Ramadan")
    
    # Test 2024 boundaries
    ramadan_start_2024 = datetime(2024, 3, 11)
    assert RamadanCalendar.is_ramadan(ramadan_start_2024, 2024) == True
    assert RamadanCalendar.get_ramadan_day(ramadan_start_2024, 2024) == 1
    print("✅ Ramadan 2024 start: Day 1")
    
    before_ramadan_2024 = datetime(2024, 3, 10)
    assert RamadanCalendar.is_ramadan(before_ramadan_2024, 2024) == False
    assert RamadanCalendar.get_ramadan_day(before_ramadan_2024, 2024) is None
    
    # Test 2025 boundaries
    ramadan_start_2025 = datetime(2025, 2, 28)
    assert RamadanCalendar.is_ramadan(ramadan_start_2025, 2025) == True
    assert RamadanCalendar.get_ramadan_day(ramadan_start_2025, 2025) == 1
    print("✅ Ramadan 2025 start: Day 1")
    
    after_ramadan_2025 = datetime(2025, 3, 30)
    assert RamadanCalendar.is_ramadan(after_ramadan_2025, 2025) == False
    assert RamadanCalendar.get_ramadan_day(after_ramadan_2025, 2025) is None


def test_metrics_data_loader():
    # Test load_historical_metrics with mock data
    mock_rows = [
        (datetime(2026, 3, 1, 10, 0), 100.0),
        (datetime(2026, 3, 1, 10, 1), 105.0),
        (datetime(2026, 3, 1, 10, 2), 110.0),
    ]
    mock_db = MockDBConnection(mock_rows)
    loader = MetricsDataLoader(mock_db)
    
    df = loader.load_historical_metrics(
        tenant_id='test-tenant',
        start_date=datetime(2026, 3, 1),
        end_date=datetime(2026, 3, 2),
        metric_name='requests_per_minute'
    )
    
    assert len(df) == 3
    assert 'value' in df.columns
    assert df.index.name == 'time' or isinstance(df.index, pd.DatetimeIndex)
    assert df['value'].iloc[0] == 100.0
    print("✅ MetricsDataLoader.load_historical_metrics works")
    
    # Test empty result
    empty_db = MockDBConnection([])
    empty_loader = MetricsDataLoader(empty_db)
    empty_df = empty_loader.load_historical_metrics(
        tenant_id='test-tenant',
        start_date=datetime(2026, 3, 1),
        end_date=datetime(2026, 3, 2)
    )
    assert len(empty_df) == 0
    print("✅ MetricsDataLoader handles empty results")


def test_resample_to_minutely():
    # Test resampling with irregular timestamps
    dates = [
        datetime(2026, 3, 1, 10, 0),
        datetime(2026, 3, 1, 10, 0, 30),
        datetime(2026, 3, 1, 10, 1, 15),
        datetime(2026, 3, 1, 10, 3),
    ]
    df = pd.DataFrame({
        'value': [100, 102, 105, 120]
    }, index=pd.DatetimeIndex(dates))
    
    mock_db = MockDBConnection([])
    loader = MetricsDataLoader(mock_db)
    
    resampled = loader.resample_to_minutely(df)
    
    # Resampled should have one row per minute from 10:00 to 10:03 (4 minutes)
    assert len(resampled) == 4
    assert not resampled['value'].isna().all()
    # First minute should have mean of 100 and 102
    assert 100 <= resampled.iloc[0]['value'] <= 102
    print("✅ resample_to_minutely handles irregular timestamps")


def test_validate_data_quality():
    mock_db = MockDBConnection([])
    loader = MetricsDataLoader(mock_db)
    
    # Test with good data (no missing values)
    good_df = pd.DataFrame({
        'value': [100, 105, 110, 115, 120]
    })
    assert loader.validate_data_quality(good_df) == True
    print("✅ validate_data_quality accepts good data")
    
    # Test with acceptable missing data (< 20%)
    acceptable_df = pd.DataFrame({
        'value': [100, 105, None, 115, 120]
    })
    assert loader.validate_data_quality(acceptable_df) == True
    print("✅ validate_data_quality accepts <20% missing")
    
    # Test with too much missing data (> 20%)
    bad_df = pd.DataFrame({
        'value': [100, None, None, None, 120]
    })
    try:
        loader.validate_data_quality(bad_df)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Data quality too low" in str(e)
        print("✅ validate_data_quality rejects >20% missing")
    
    # Test with empty DataFrame
    empty_df = pd.DataFrame({'value': []})
    try:
        loader.validate_data_quality(empty_df)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "No data available" in str(e)
        print("✅ validate_data_quality rejects empty DataFrame")


if __name__ == "__main__":
    test_ramadan_calendar()
    test_metrics_data_loader()
    test_resample_to_minutely()
    test_validate_data_quality()
    print("\n✅ All preprocessing tests passed")
