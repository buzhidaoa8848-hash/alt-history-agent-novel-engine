#!/usr/bin/env python3
"""
Alt-History Agent Novel Engine v2.0
历史岔路口小说生成器

Usage:
    python main.py --scenario scenarios/qin_fusu_lishimin_data.py
    python main.py --preset qin_fusu
    python main.py --preset three_kingdoms
    python main.py --interactive
"""

import argparse
import json
import os
import sys
from pathlib import Path
from datetime import datetime


def main():
    parser = argparse.ArgumentParser(
        description="Alt-History Agent Novel Engine v2.0 - 历史岔路口小说生成器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python main.py --preset qin_fusu                     # 经典秦王李世民
    python main.py --preset three_kingdoms               # 三国郭嘉if线
    python main.py --scenario scenarios/xxx.py           # 指定场景文件
    python main.py --interactive                         # 交互式创建
    python main.py --preset qin_fusu --mode llm          # DeepSeek模式
        """
    )
    parser.add_argument("--scenario", "-s",
                        help="Path to scenario file (.py)")
    parser.add_argument("--preset", "-p",
                        choices=["qin_fusu", "three_kingdoms", "modern_startup"],
                        help="Use preset scenario")
    parser.add_argument("--interactive", "-i", action="store_true",
                        help="Interactive scenario builder")
    parser.add_argument("--mode", "-m", default="mock",
                        choices=["mock", "llm"],
                        help="Generation mode: mock or llm")
    parser.add_argument("--list-presets", action="store_true",
                        help="List available presets")
    parser.add_argument("--check", action="store_true",
                        help="Run constraint check on existing output")

    args = parser.parse_args()

    # Handle --list-presets
    if args.list_presets:
        _list_presets()
        return

    # Handle --interactive
    if args.interactive:
        print("\n⚠️  交互模式需要终端支持。当前为消息模式，请使用 --preset 或 --scenario")
        print("   支持的预设: --preset qin_fusu / three_kingdoms / modern_startup\n")
        _list_presets()
        return

    # Determine scenario source
    scenario_data = None

    if args.preset:
        print(f"[0/7] 加载预设场景: {args.preset}")
        from src.scenario_builder import ScenarioBuilder
        builder = ScenarioBuilder()
        scenario_data = builder.load_preset(args.preset)
        print(f"  ✓ 预设: {scenario_data['scenario']['title']}")

    elif args.scenario:
        print(f"[0/7] 加载场景文件: {args.scenario}")
        from src.scenario_loader import load_scenario
        loader = load_scenario(args.scenario)
        scenario_data = {"scenario": loader.data}

    else:
        parser.print_help()
        print("\n请指定场景：--preset, --scenario, 或 --interactive")
        return

    # Ensure we have data
    data = scenario_data["scenario"]

    # --- Phase 1: Load scenario ---
    print("\n[1/7] 解析场景配置...")
    print(f"  ✓ 标题: {data.get('title', 'Unknown')}")
    print(f"  ✓ 类型: {data.get('type', 'history')}")
    print(f"  ✓ 时代: {data.get('era', data.get('setting', {}).get('era', 'N/A'))}")
    agents_def = data.get('agents', [])
    print(f"  ✓ Agent预设: {len(agents_def)} 个")

    # --- Phase 1.5: Load constraints ---
    print("\n[1.5/7] 加载硬约束...")
    from src.constraint_engine import ConstraintEngine
    engine = ConstraintEngine()
    engine.load_presets(["common_sense", "historical"])
    engine.add_from_scenario(data)
    print(f"  ✓ {len(engine.constraints)} 条约束生效")
    for c in engine.constraints:
        print(f"    [{c.constraint_type}] {c.rule[:50]}...")

    # --- Phase 2: Build agent cards ---
    print("\n[2/7] 生成人物Agent卡...")
    from src.agent_builder import AgentBuilder

    builder = AgentBuilder(data)
    agents = builder.build_all()
    agents_dict = [a.to_dict() for a in agents]
    print(f"  ✓ {len(agents)} 个人物 Agent:")
    for a in agents_dict:
        print(f"    - {a['name']}")

    # --- Phase 3: Initialize world state ---
    print("\n[3/7] 初始化世界状态...")
    from src.world_state import create_initial_world_state

    world_state = create_initial_world_state(data)
    print(f"  ✓ {len(world_state.state)} 个变量")

    # --- Phase 4: Run simulation ---
    print("\n[4/7] 运行历史推演...")
    from src.simulation_runner import SimulationRunner

    round_defs = data.get("simulation_rounds", [])
    runner = SimulationRunner(agents_dict, world_state, round_defs)
    results = runner.run_all()
    timeline = runner.get_timeline()

    print(f"  ✓ 完成 {len(results)} 轮推演")
    for r in results:
        print(f"    第{r['round']}轮: {r.get('title', '')} "
              f"({len(r.get('events', []))} 事件)")

    # Check constraints
    violations = engine.validate_timeline(timeline)
    if violations:
        print(f"  ⚠️ 约束违规: {len(violations)} 条")
        for v in violations[:3]:
            print(f"    [{v['severity']}] 第{v['round']}轮: {v['detail'][:60]}")

    terminal = runner.terminal_reason
    print(f"  ⚔️ 终结原因: {terminal}")

    # --- Phase 5: Generate plot outline ---
    print("\n[5/7] 生成小说大纲...")
    from src.plot_planner import PlotPlanner

    planner = PlotPlanner(timeline, world_state.to_dict())
    outline = planner.generate_outline()
    print(f"  ✓ {len(outline)} 字符")

    # --- Phase 6: Write Chapter 1 ---
    print("\n[6/7] 生成第一章正文...")
    from src.chapter_writer import generate_first_chapter

    chapter = generate_first_chapter(timeline, outline,
                                      world_state.to_dict(), agents_dict)
    print(f"  ✓ {len(chapter)} 字符")

    # --- Phase 7: Consistency check ---
    print("\n[7/7] 执行一致性检查...")
    from src.consistency_checker import ConsistencyChecker

    checker = ConsistencyChecker(timeline, outline, world_state.to_dict(),
                                  agents_dict, data)
    report = checker.to_markdown()

    # Add constraint report
    constraint_report = engine.summary_report()
    full_report = report + "\n\n" + constraint_report

    print(f"  ✓ 完成")

    # --- Save outputs ---
    print("\n" + "=" * 60)
    print("  保存输出文件")
    print("=" * 60)

    output_config = data.get("output", {})
    base_dir = output_config.get("base_dir", "outputs/run_001")
    output_path = Path(base_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    from src.scenario_loader import ScenarioLoader
    loader = ScenarioLoader.__new__(ScenarioLoader)

    files_to_save = {
        "scenario.json": json.dumps({
            "scenario_id": data.get("id", "unknown"),
            "title": data.get("title", ""),
            "type": data.get("type", "history"),
            "description": data.get("description", ""),
            "divergence_point": data.get("divergence_point", {}),
            "setting": data.get("setting", {}),
        }, ensure_ascii=False, indent=2),
        "agents.json": json.dumps(agents_dict, ensure_ascii=False, indent=2),
        "world_state.json": json.dumps(world_state.to_dict(), ensure_ascii=False, indent=2),
        "timeline.json": json.dumps(timeline, ensure_ascii=False, indent=2),
        "plot_outline.md": outline,
        "chapter_001.md": chapter,
        "constraint_report.md": constraint_report,
        "consistency_report.md": report,
    }

    for filename, content in files_to_save.items():
        filepath = output_path / filename
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  ✓ {filename} ({len(content)} bytes)")

    meta = {
        "generated_at": datetime.now().isoformat(),
        "scenario": args.preset or args.scenario or "interactive",
        "mode": args.mode,
        "terminal_reason": terminal,
        "constraint_violations": len(violations),
        "files": list(files_to_save.keys()),
    }
    with open(output_path / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    print(f"  ✓ metadata.json")

    print(f"\n  📁 输出目录: {output_path.absolute()}")
    print(f"  ⚔️ 故事结局: {terminal}")
    if violations:
        print(f"  ⚠️ 约束违规: {len(violations)} 条（详见 constraint_report.md）")
    print()
    print("=" * 60)
    print("  v2.0 生成完成！")
    print("=" * 60)


def _list_presets():
    """列出所有预设场景"""
    from src.scenario_builder import PRESET_SCENARIOS
    print("\n" + "=" * 60)
    print("  📚 预设场景库")
    print("=" * 60)
    for key, preset in PRESET_SCENARIOS.items():
        print(f"\n  [{key}]")
        print(f"  标题: {preset['title']}")
        print(f"  类型: {preset['type']}")
        print(f"  时代: {preset['era']}")
        print(f"  描述: {preset['description']}")
        print(f"  用法: python main.py --preset {key}")


if __name__ == "__main__":
    project_root = Path(__file__).parent.absolute()
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    main()
