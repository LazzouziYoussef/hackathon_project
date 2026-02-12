from datetime import datetime


class RamadanCalendar:
    RAMADAN_2024 = (datetime(2024, 3, 11), datetime(2024, 4, 9))
    RAMADAN_2025 = (datetime(2025, 2, 28), datetime(2025, 3, 29))
    RAMADAN_2026 = (datetime(2026, 2, 17), datetime(2026, 3, 18))
    
    CALENDARS = {
        2024: RAMADAN_2024,
        2025: RAMADAN_2025,
        2026: RAMADAN_2026,
    }
    
    @staticmethod
    def is_ramadan(timestamp, year=2026):
        start, end = RamadanCalendar.CALENDARS.get(year, RamadanCalendar.RAMADAN_2026)
        return start <= timestamp <= end
    
    @staticmethod
    def get_ramadan_day(timestamp, year=2026):
        start, end = RamadanCalendar.CALENDARS.get(year, RamadanCalendar.RAMADAN_2026)
        
        if not (start <= timestamp <= end):
            return None
        
        return (timestamp - start).days + 1
