from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.time_utils import RamadanCalendar


def test_ramadan_calendar():
    test_date = datetime(2026, 3, 1)
    assert RamadanCalendar.is_ramadan(test_date, 2026) == True
    
    day = RamadanCalendar.get_ramadan_day(test_date, 2026)
    assert day is not None
    print(f"✅ Ramadan calendar works: Day {day}")
    
    non_ramadan_date = datetime(2026, 1, 1)
    assert RamadanCalendar.is_ramadan(non_ramadan_date, 2026) == False
    print("✅ Non-Ramadan dates correctly identified")
    
    ramadan_start = datetime(2026, 2, 17)
    day_1 = RamadanCalendar.get_ramadan_day(ramadan_start, 2026)
    assert day_1 == 1
    print(f"✅ First day of Ramadan: Day {day_1}")
    
    ramadan_end = datetime(2026, 3, 18)
    day_30 = RamadanCalendar.get_ramadan_day(ramadan_end, 2026)
    assert day_30 == 30
    print(f"✅ Last day of Ramadan: Day {day_30}")


if __name__ == "__main__":
    test_ramadan_calendar()
    print("\n✅ All preprocessing tests passed")
