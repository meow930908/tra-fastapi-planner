MOCK_STATIONS = [
    {"id": "1000", "name": "臺北"},
    {"id": "1020", "name": "板橋"},
    {"id": "1100", "name": "臺中"},
    {"id": "1210", "name": "臺南"},
    {"id": "1230", "name": "高雄"},
]
# app/mock_data.py

MOCK_STATIONS = [
    {"id": "1000", "name": "臺北"},
    {"id": "1020", "name": "板橋"},
    {"id": "1100", "name": "臺中"},
    {"id": "1210", "name": "臺南"},
    {"id": "1230", "name": "高雄"},
]

MOCK_TRAINS = [
    # 臺北 -> 臺中
    {"train_no": "111", "origin": "臺北", "destination": "臺中", "dep": "08:10", "arr": "10:00", "seat_type": "reserved", "fare": 375},
    {"train_no": "113", "origin": "臺北", "destination": "臺中", "dep": "08:30", "arr": "10:35", "seat_type": "reserved", "fare": 375},
    {"train_no": "201", "origin": "臺北", "destination": "臺中", "dep": "08:20", "arr": "11:10", "seat_type": "non_reserved", "fare": 241},

    # 臺北 -> 臺南
    {"train_no": "121", "origin": "臺北", "destination": "臺南", "dep": "09:00", "arr": "12:20", "seat_type": "reserved", "fare": 738},
    {"train_no": "221", "origin": "臺北", "destination": "臺南", "dep": "09:10", "arr": "13:30", "seat_type": "non_reserved", "fare": 477},

    # 臺北 -> 高雄
    {"train_no": "131", "origin": "臺北", "destination": "高雄", "dep": "10:00", "arr": "14:40", "seat_type": "reserved", "fare": 843},
    {"train_no": "231", "origin": "臺北", "destination": "高雄", "dep": "10:20", "arr": "16:10", "seat_type": "non_reserved", "fare": 542},
]
