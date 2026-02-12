from datetime import datetime


class RamadanCalendar:
    RAMADAN_2024 = (datetime(2024, 3, 11), datetime(2024, 4, 9))
    RAMADAN_2025 = (datetime(2025, 2, 28), datetime(2025, 3, 29))
    RAMADAN_2026 = (datetime(2026, 2, 17), datetime(2026, 3, 18))
    
    @staticmethod
    def is_ramadan(timestamp, year=2026):
        calendars = {
            2024: RamadanCalendar.RAMADAN_2024,
            2025: RamadanCalendar.RAMADAN_2025,
            2026: RamadanCalendar.RAMADAN_2026,
        }
        
        start, end = calendars.get(year, RamadanCalendar.RAMADAN_2026)
        return start <= timestamp <= end
    
    @staticmethod
    def get_ramadan_day(timestamp, year=2026):
        calendars = {
            2024: RamadanCalendar.RAMADAN_2024,
            2025: RamadanCalendar.RAMADAN_2025,
            2026: RamadanCalendar.RAMADAN_2026,
        }
        
        start, end = calendars.get(year, RamadanCalendar.RAMADAN_2026)
        
        if not (start <= timestamp <= end):
            return None
        
        return (timestamp - start).days + 1
