from collections import defaultdict
import time

class Cart:
    def __init__(self, debounce_seconds=1.0):
        self.items = defaultdict(int)
        self.last_seen = {}
        self.debounce_seconds = debounce_seconds

    def add(self, item_name):
        now = time.time()
        last = self.last_seen.get(item_name, 0)
        if now - last >= self.debounce_seconds:
            self.items[item_name] += 1
            self.last_seen[item_name] = now
            return True
        return False

    def reset(self):
        self.items = defaultdict(int)
        self.last_seen = {}

    def to_list(self, price_map=None):
        out = []
        total = 0.0
        if price_map is None:
            price_map = {}
        for k, v in self.items.items():
            unit = float(price_map.get(k, 0.0))
            tot = unit * v
            total += tot
            out.append({"name": k, "count": v, "unit_price": unit, "total_price": tot})
        return {"items": out, "grand_total": total}
