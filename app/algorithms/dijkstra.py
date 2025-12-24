import json
import heapq
import re
from bisect import bisect_left
from pathlib import Path
from typing import Dict, List, Tuple, Optional

TIME_SUFFIX_RE = re.compile(r"\s*\d{1,2}:\d{2}\s*$")

def clean_station(name: str) -> str:
    if not name:
        return ""
    s = str(name).replace("\u3000", " ").strip()
    return TIME_SUFFIX_RE.sub("", s).strip()

def hhmm_to_min(hhmm: str) -> int:
    h, m = hhmm.split(":")
    return int(h) * 60 + int(m)

def min_to_hhmm(minutes: int) -> str:
    minutes %= 1440
    return f"{minutes // 60:02d}:{minutes % 60:02d}"

def build_by_origin(conns: List[dict], seat_type: Optional[str]):
    by_origin = {}
    for c in conns:
        if seat_type and c.get("seat_type") != seat_type:
            continue

        o = clean_station(c["origin"])
        d = clean_station(c["destination"])

        item = dict(c)
        item["origin"] = o
        item["destination"] = d
        item["dep_min"] = hhmm_to_min(c["dep"])
        item["arr_min"] = hhmm_to_min(c["arr"])

        if item["arr_min"] < item["dep_min"]:
            item["arr_min"] += 1440

        by_origin.setdefault(o, []).append(item)

    for k in by_origin:
        by_origin[k].sort(key=lambda x: x["dep_min"])
    return by_origin

def earliest_arrival_dijkstra(
    by_origin,
    origin,
    destination,
    start_min,
    transfer_buffer_min=8,
):
    INF = 10**15
    start_state = (origin, None)

    dist = {start_state: start_min}
    parent = {}
    pq = [(start_min, start_state)]

    best_state = None
    best_time = INF

    while pq:
        cur_time, (u, last_train) = heapq.heappop(pq)
        if cur_time != dist.get((u, last_train), INF):
            continue

        if u == destination and cur_time < best_time:
            best_time = cur_time
            best_state = (u, last_train)

        for e in by_origin.get(u, []):
            train = e["train_no"]
            buffer = 0 if train == last_train else transfer_buffer_min
            if e["dep_min"] < cur_time + buffer:
                continue

            v = e["destination"]
            arr = e["arr_min"]
            state = (v, train)

            if arr < dist.get(state, INF):
                dist[state] = arr
                parent[state] = ((u, last_train), e)
                heapq.heappush(pq, (arr, state))

    if not best_state:
        return None, []

    path = []
    cur = best_state
    while cur != start_state:
        prev, edge = parent[cur]
        path.append(edge)
        cur = prev
    path.reverse()
    return best_time, path

def compress_segments(path):
    if not path:
        return []
    merged = [dict(path[0])]
    for e in path[1:]:
        if e["train_no"] == merged[-1]["train_no"]:
            merged[-1]["destination"] = e["destination"]
            merged[-1]["arr"] = e["arr"]
        else:
            merged.append(dict(e))
    return merged
