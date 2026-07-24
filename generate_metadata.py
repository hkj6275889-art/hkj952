#!/usr/bin/env python3
"""대본 입력 YAML을 바탕으로 유튜브 업로드용 제목/설명/태그 후보를 생성하는 반자동화 도구."""

import argparse

import yaml

TITLE_PATTERNS = [
    "{topic}, 아무도 말해주지 않은 진실",
    "숫자 하나로 보는 {topic}의 미래",
    "{topic}, 우리가 놓치고 있는 것",
    "{topic}에 대해 아무도 설명해주지 않은 이야기",
    "10분 안에 이해하는 {topic}",
]


def build_titles(topic: str):
    return [p.format(topic=topic) for p in TITLE_PATTERNS]


def build_description(meta: dict, hook: dict, actions: list) -> str:
    lines = [hook.get("question", ""), ""]
    lines.append(f"이 영상은 '{meta.get('topic', '')}'에 대해 이야기합니다.")
    lines.append("")
    if actions:
        lines.append("영상에서 소개한 실천 방법:")
        for i, a in enumerate(actions, 1):
            lines.append(f"{i}. {a}")
        lines.append("")
    lines.append("채널을 구독하고 알림을 설정해 주세요.")
    keywords = meta.get("keywords", [])
    if keywords:
        lines.append("")
        lines.append(" ".join(f"#{k.replace(' ', '')}" for k in keywords))
    return "\n".join(lines)


def build_tags(meta: dict):
    base = meta.get("keywords", [])
    extra = [meta.get("channel_name", "")]
    tags, seen = [], set()
    for t in base + extra:
        if t and t not in seen:
            seen.add(t)
            tags.append(t)
    return tags


def main():
    ap = argparse.ArgumentParser(description="유튜브 메타데이터(제목/설명/태그) 후보 생성기")
    ap.add_argument("--input", "-i", required=True)
    ap.add_argument("--output", "-o")
    args = ap.parse_args()

    with open(args.input, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    meta = data.get("meta", {})
    hook = data.get("hook", {})
    actions = data.get("action_items", [])

    titles = build_titles(meta.get("topic", ""))
    description = build_description(meta, hook, actions)
    tags = build_tags(meta)

    out = ["# 제목 후보", ""]
    out += [f"- {t}" for t in titles]
    out += ["", "# 설명란", "", description]
    out += ["", "# 태그", "", ", ".join(tags)]

    text = "\n".join(out)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(text)
    else:
        print(text)


if __name__ == "__main__":
    main()
