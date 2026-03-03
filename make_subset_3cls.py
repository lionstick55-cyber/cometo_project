import os
import shutil
from pathlib import Path
import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]  # cometo_project01
SRC = PROJECT_ROOT / "datasets"
DST = PROJECT_ROOT / "datasets_3cls"

# ✅ 최종 3클래스 이름(새 데이터셋의 클래스 순서)
TARGET_NAMES = ["person", "dog", "car"]  # new ids: person=0, dog=1, car=2

# ✅ 원본 names에서 이걸 같은 클래스로 취급(동의어 묶기)
ALIASES = {
    "person": {"person", "people", "persons", "Pedestrian", "Pedestrians", "Persona", "Pessoa"},
    "car": {"car", "Car"},
    "dog": {"dog"},
}

def load_yaml(p: Path) -> dict:
    with p.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def ensure_dirs():
    for split in ["train", "valid", "test"]:
        (DST / split / "images").mkdir(parents=True, exist_ok=True)
        (DST / split / "labels").mkdir(parents=True, exist_ok=True)

def build_id_map(src_names: list[str]) -> dict[int, int]:
    name_to_id = {n: i for i, n in enumerate(src_names)}
    new_id = {name: idx for idx, name in enumerate(TARGET_NAMES)}  # person=0,dog=1,car=2

    mapping: dict[int, int] = {}
    for new_name, alias_set in ALIASES.items():
        for alias in alias_set:
            if alias in name_to_id:
                mapping[name_to_id[alias]] = new_id[new_name]
    return mapping

def filter_label_file(src_label: Path, dst_label: Path, id_map: dict[int, int]) -> bool:
    kept = []
    with src_label.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            cls = int(parts[0])
            if cls in id_map:
                parts[0] = str(id_map[cls])
                kept.append(" ".join(parts))

    if not kept:
        return False

    with dst_label.open("w", encoding="utf-8") as f:
        f.write("\n".join(kept) + "\n")
    return True

def copy_image(src_img: Path, dst_img_dir: Path):
    shutil.copy2(src_img, dst_img_dir / src_img.name)

def process_split(split: str, id_map: dict[int, int]):
    src_img_dir = SRC / split / "images"
    src_lab_dir = SRC / split / "labels"
    dst_img_dir = DST / split / "images"
    dst_lab_dir = DST / split / "labels"

    if not src_img_dir.exists() or not src_lab_dir.exists():
        print(f"[SKIP] {split}: images/labels 폴더 없음")
        return

    imgs = list(src_img_dir.glob("*.*"))
    kept_images = 0

    for img in imgs:
        stem = img.stem
        lab = src_lab_dir / f"{stem}.txt"
        if not lab.exists():
            continue

        out_lab = dst_lab_dir / lab.name
        ok = filter_label_file(lab, out_lab, id_map)
        if not ok:
            if out_lab.exists():
                out_lab.unlink()
            continue

        copy_image(img, dst_img_dir)
        kept_images += 1

    print(f"[DONE] {split}: kept {kept_images} images (person/dog/car)")

def write_new_data_yaml():
    out = Path(__file__).resolve().parent / "data_3cls.yaml"
    y = {
        "train": str((DST / "train" / "images").as_posix()),
        "val": str((DST / "valid" / "images").as_posix()),
        "test": str((DST / "test" / "images").as_posix()),
        "nc": len(TARGET_NAMES),
        "names": TARGET_NAMES,
    }
    with out.open("w", encoding="utf-8") as f:
        yaml.safe_dump(y, f, allow_unicode=True, sort_keys=False)
    print("[OK] wrote", out)

def main():
    src_yaml = Path(__file__).resolve().parent / "data.yaml"
    d = load_yaml(src_yaml)
    src_names = d["names"]

    id_map = build_id_map(src_names)
    print("[INFO] mapped source ids -> new ids:", id_map)

    ensure_dirs()
    for split in ["train", "valid", "test"]:
        process_split(split, id_map)

    write_new_data_yaml()
    print("\n✅ 새 데이터셋 폴더:", DST)
    print("✅ 새 yaml:", Path(__file__).resolve().parent / "data_3cls.yaml")

if __name__ == "__main__":
    main()