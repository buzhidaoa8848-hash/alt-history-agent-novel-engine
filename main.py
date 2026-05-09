#!/usr/bin/env python3
"""
Alt-History Agent Novel Engine
历史岔路口小说生成器

Usage:
    python main.py --scenario scenarios/qin_fusu_lishimin.yaml

Based on mirofish-cli multi-agent simulation pipeline pattern.
"""

import argparse
import json
import os
import sys
from pathlib import Path
from datetime import datetime


def main():
    parser = argparse.ArgumentParser(
        description="Alt-History Agent Novel Engine - 历史岔路口小说生成器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example:
    python main.py --scenario scenarios/qin_fusu_lishimin.yaml
    python main.py --scenario scenarios/qin_fusu_lishimin.yaml --mode mock
    python main.py --scenario scenarios/qin_fusu_lishimin.yaml --mode llm --api-key sk-xxx
        """
    )
    parser.add_argument("--scenario", "-s", required=True,
                        help="Path to scenario file (.yaml, .json, or .py)")
    parser.add_argument("--mode", "-m", default="mock",
                        choices=["mock", "llm"],
                        help="Generation mode: mock (built-in templates) or llm (real AI)")
    parser.add_argument("--api-key", help="LLM API key (required for --mode llm)")
    parser.add_argument("--api-base", default="https://api.openai.com/v1",
                        help="LLM API base URL")
    parser.add_argument("--model", default="gpt-4",
                        help="LLM model name")
    parser.add_argument("--output-dir", help="Override output directory")

    args = parser.parse_args()

    # --- Phase 0: Setup ---
    print("=" * 60)
    print("  历史岔路口小说生成器 · Alt-History Novel Engine")
    print("=" * 60)
    print()

    # --- Phase 1: Load scenario ---
    print("[1/7] 加载场景配置...")
    from src.scenario_loader import load_scenario

    try:
        loader = load_scenario(args.scenario)
        scenario_data = loader.data
        print(f"  ✓ 场景: {scenario_data.get('title', 'Unknown')}")
        print(f"  ✓ Agents: {len(scenario_data.get('agents', []))}")
        print(f"  ✓ 推演轮次: {len(scenario_data.get('simulation_rounds', []))}")
    except Exception as e:
        print(f"  ✗ 场景加载失败: {e}")
        sys.exit(1)

    # --- Phase 2: Build agent cards ---
    print("\n[2/7] 生成人物Agent卡...")
    from src.agent_builder import AgentBuilder

    try:
        builder = AgentBuilder(scenario_data)
        agents = builder.build_all()
        agents_dict = [a.to_dict() for a in agents]
        print(f"  ✓ 已生成 {len(agents)} 个人物 Agent:")
        for a in agents_dict:
            print(f"    - {a['name']} ({a.get('identity', '')[:40]})")
    except Exception as e:
        print(f"  ✗ Agent生成失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # --- Phase 3: Initialize world state ---
    print("\n[3/7] 初始化世界状态...")
    from src.world_state import create_initial_world_state

    try:
        world_state = create_initial_world_state(scenario_data)
        ws = world_state.state
        print(f"  ✓ 世界状态已初始化 ({len(ws)} 个变量)")
        print(f"    - 时间: {ws.get('current_year', 'N/A')}")
        print(f"    - 地点: {ws.get('current_location', 'N/A')}")
        print(f"    - 皇权状态: {ws.get('emperor_status', 'N/A')}")
        print(f"    - 主角生存风险: {ws.get('protagonist_survival_risk', 'N/A')}/100")
    except Exception as e:
        print(f"  ✗ 世界状态初始化失败: {e}")
        sys.exit(1)

    # --- Phase 4: Run simulation ---
    print("\n[4/7] 运行历史推演...")
    from src.simulation_runner import SimulationRunner

    try:
        round_defs = scenario_data.get("simulation_rounds", [])
        runner = SimulationRunner(agents_dict, world_state, round_defs)
        results = runner.run_all()
        timeline = runner.get_timeline()
        print(f"  ✓ 完成 {len(results)} 轮推演:")
        for r in results:
            print(f"    第{r['round']}轮: {r.get('title', '')} "
                  f"({len(r.get('events', []))} 事件)")
    except Exception as e:
        print(f"  ✗ 推演失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # --- Phase 5: Generate plot outline ---
    print("\n[5/7] 生成小说大纲...")
    from src.plot_planner import PlotPlanner

    try:
        planner = PlotPlanner(timeline, world_state.to_dict())
        outline = planner.generate_outline()
        print(f"  ✓ 大纲已生成 ({len(outline)} 字符)")
    except Exception as e:
        print(f"  ✗ 大纲生成失败: {e}")
        outline = "# Outline generation failed\n\n"
        sys.exit(1)

    # --- Phase 6: Write Chapter 1 ---
    print("\n[6/7] 生成第一章正文...")
    from src.chapter_writer import generate_first_chapter

    try:
        chapter = generate_first_chapter(timeline, outline,
                                          world_state.to_dict(), agents_dict)
        print(f"  ✓ 第一章已生成 ({len(chapter)} 字符)")
    except Exception as e:
        print(f"  ✗ 章节生成失败: {e}")
        chapter = "# 第一章 生成失败\n\n"
        import traceback
        traceback.print_exc()

    # --- Phase 7: Consistency check ---
    print("\n[7/7] 执行一致性检查...")
    from src.consistency_checker import ConsistencyChecker

    try:
        checker = ConsistencyChecker(
            timeline, outline, world_state.to_dict(),
            agents_dict, scenario_data
        )
        consistency_report = checker.to_markdown()
        print(f"  ✓ 一致性检查完成")
        print(f"    状态: {checker.check_all()['summary']['status']}")
    except Exception as e:
        print(f"  ✗ 一致性检查失败: {e}")
        consistency_report = "# Consistency check failed\n\n"

    # --- Save outputs ---
    print("\n" + "=" * 60)
    print("  保存输出文件")
    print("=" * 60)

    # Determine output directory
    output_config = scenario_data.get("output", {})
    base_dir = args.output_dir or output_config.get("base_dir", "outputs/run_001")
    output_path = Path(base_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Save all files
    files_to_save = {
        "scenario.json": json.dumps(loader.to_dict(), ensure_ascii=False, indent=2),
        "agents.json": json.dumps(agents_dict, ensure_ascii=False, indent=2),
        "world_state.json": json.dumps(world_state.to_dict(), ensure_ascii=False, indent=2),
        "timeline.json": json.dumps(timeline, ensure_ascii=False, indent=2),
        "plot_outline.md": outline,
        "chapter_001.md": chapter,
        "consistency_report.md": consistency_report,
    }

    for filename, content in files_to_save.items():
        filepath = output_path / filename
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  ✓ {filename} ({os.path.getsize(filepath)} bytes)")

    # Save metadata
    meta = {
        "generated_at": datetime.now().isoformat(),
        "scenario": args.scenario,
        "mode": args.mode,
        "files": list(files_to_save.keys()),
    }
    with open(output_path / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    print(f"  ✓ metadata.json")

    print()
    print(f"  📁 所有输出保存在: {output_path.absolute()}")
    print()
    print("=" * 60)
    print("  生成完成！")
    print(f"  共生成 {len(files_to_save) + 1} 个文件")
    print("=" * 60)


if __name__ == "__main__":
    # Ensure we can import src modules
    project_root = Path(__file__).parent.absolute()
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    main()
