import sys, random, json
sys.path.insert(0, sys.argv[1])
from src.agent import edge
random.seed(1)
recs = []
for i in range(60):
    price = random.uniform(0.2, 0.8)           # Buchpreis = implizite W'keit der eigenen Seite
    est = min(0.97, price + 0.12)              # Agent glaubt systematisch +12 pp Vorteil
    won = random.random() < price              # Wahrheit: Buch hat recht
    recs.append({"ts": f"2026-10-{1+i%28:02d}T10:00:00Z", "price": price, "est_prob": est, "side": "yes",
                 "outcome": {"won": won, "settled_time": f"2026-11-{1+i%28:02d}T10:00:00Z"}})
r = edge.edge_report(recs, "2026-11-30")
print(json.dumps(r, indent=1, default=str)[:1500])
