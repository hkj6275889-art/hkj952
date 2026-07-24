#!/usr/bin/env python3
"""유튜브 정보성 내레이션 대본을 정해진 서사 구조에 맞춰 초안으로 조립하는 반자동화 도구.

사용자가 리서치한 사실/수치/이야기를 YAML로 입력하면,
훅 -> 문제제기 -> 전환 -> 비전 -> 근거 -> 미래상상 -> 구조변화 -> 실천 -> 마무리
순서의 내레이션 대본 초안을 생성한다. 최종 검수/수정은 사람이 한다.
"""

import argparse
import sys

import yaml

CHARS_PER_SEC = 4.5  # 한국어 내레이션 평균 발화 속도 추정치


def fmt_time(seconds: float) -> str:
    m, s = divmod(int(seconds), 60)
    return f"{m:02d}:{s:02d}"


def section(heading: str, body: str, cursor: float):
    body = body.strip()
    duration = len(body.replace("\n", "")) / CHARS_PER_SEC
    text = f"## [{fmt_time(cursor)}] {heading}\n\n{body}\n"
    return text, cursor + duration


def build_script(data: dict) -> str:
    meta = data.get("meta", {})
    hook = data["hook"]
    stat = data["key_stat"]
    walls = data["problem_walls"]
    turn = data["turn"]
    analogy = data["analogy"]
    systems = data["vision_systems"]
    history = data.get("history_story")
    future = data.get("future_scenario")
    power = data.get("power_shift")
    role = data.get("human_role")
    actions = data.get("action_items", [])
    closing = data["closing"]

    cursor = 0.0
    parts = []

    body = f"{hook['question']}\n\n{hook['relatable_feeling']}"
    t, cursor = section("훅 - 공감 질문", body, cursor)
    parts.append(t)

    body = f"{stat['number']}\n\n{stat['context']}"
    if stat.get("source_note"):
        body += f"\n\n({stat['source_note']})"
    t, cursor = section("핵심 수치 제시", body, cursor)
    parts.append(t)

    wall_body = "\n\n".join(
        f"{i + 1}번째, {w['title']}. {w['description']}" for i, w in enumerate(walls)
    )
    t, cursor = section("문제의 구조 (벽 쌓기)", wall_body, cursor)
    parts.append(t)

    t, cursor = section("전환 - 다른 길이 있다", turn["transition_line"], cursor)
    parts.append(t)

    analogy_body = f"{analogy['subject']}\n\n" + "\n".join(
        f"- {p}" for p in analogy["points"]
    )
    t, cursor = section("자연/생체 비유", analogy_body, cursor)
    parts.append(t)

    sys_body = "\n\n".join(
        f"{i + 1}. {s['name']} - {s['description']}" for i, s in enumerate(systems)
    )
    t, cursor = section("비전 제시 (핵심 요소)", sys_body, cursor)
    parts.append(t)

    if history:
        body = f"{history['year']}, {history['people']}\n\n{history['narrative']}"
        t, cursor = section("역사적 일화 / 근거", body, cursor)
        parts.append(t)

    if future:
        body = f"{future['setting']}\n\n{future['dialogue']}"
        t, cursor = section("미래 상상 시나리오", body, cursor)
        parts.append(t)

    if power:
        body = f"기존: {power['old_structure']}\n\n변화: {power['new_structure']}"
        t, cursor = section("구조 변화 논의", body, cursor)
        parts.append(t)

    if role:
        body = f"{role['liberation_from']}에서 해방되어,\n\n{role['liberation_to']}"
        t, cursor = section("인간의 역할 재정의", body, cursor)
        parts.append(t)

    if actions:
        body = "\n".join(f"{i + 1}. {a}" for i, a in enumerate(actions))
        t, cursor = section("오늘부터 할 수 있는 것", body, cursor)
        parts.append(t)

    body = f"{closing['share_ask']}\n\n{closing['channel_cta']}"
    t, cursor = section("마무리 및 구독 유도", body, cursor)
    parts.append(t)

    header = f"# {meta.get('topic', '제목 없음')}\n\n"
    header += f"채널: {meta.get('channel_name', '')}  \n"
    header += f"예상 길이: 약 {fmt_time(cursor)} (발화 속도 추정치 기준, 실제와 다를 수 있음)\n\n---\n\n"

    return header + "\n".join(parts)


def main():
    ap = argparse.ArgumentParser(description="유튜브 내레이션 대본 초안 생성기")
    ap.add_argument("--input", "-i", required=True, help="입력 YAML 파일 경로")
    ap.add_argument("--output", "-o", help="출력 마크다운 파일 경로 (생략 시 표준출력)")
    args = ap.parse_args()

    with open(args.input, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    script = build_script(data)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(script)
        print(f"대본 초안을 저장했습니다: {args.output}", file=sys.stderr)
    else:
        print(script)


if __name__ == "__main__":
    main()
