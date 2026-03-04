import glob
import collections

def count(split):
    paths = glob.glob(f"datasets_3cls/{split}/labels/*.txt")
    c = collections.Counter()
    for p in paths:
        with open(p, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                cls = int(line.split()[0])
                c[cls] += 1
    return c, len(paths)

for split in ["train", "valid", "test"]:
    c, n = count(split)
    print(f"{split}: label_files={n}, class_counts={dict(sorted(c.items()))}")
