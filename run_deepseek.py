#!/usr/bin/env python3
"""Run full alt-history simulation with DeepSeek API"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set API key
os.environ["DEEPSEEK_API_KEY"] = "sk-915c1aabb54d4a67941bcbb2bc9af8d0"
os.environ["DEEPSEEK_API_BASE"] = "https://api.deepseek.com/v1"
os.environ["DEEPSEEK_MODEL"] = "deepseek-chat"

from src.llm_client import reset_client, get_client

# Configure LLM
reset_client()
llm = get_client(mode="llm", config={
    "api_key": "sk-915c1aabb54d4a67941bcbb2bc9af8d0",
    "api_base": "https://api.deepseek.com/v1",
    "model": "deepseek-chat"
})

print("=" * 60)
print("  Alt-History Novel Engine — DeepSeek Mode")
print("=" * 60)

# 1. Load scenario
print("\n[1/7] 加载场景...")
from src.scenario_loader import load_scenario
loader = load_scenario("scenarios/qin_fusu_lishimin_data.py")
data = loader.data
print(f"  ✓ {data['title']}")

# 2. Build agents
print("\n[2/7] 生成Agent卡...")
from src.agent_builder import AgentBuilder
builder = AgentBuilder(data)
agents = builder.build_all()
agents_dict = [a.to_dict() for a in agents]
print(f"  ✓ {len(agents)} 个Agent")

# 3. Init world
print("\n[3/7] 初始化世界状态...")
from src.world_state import create_initial_world_state
ws = create_initial_world_state(data)
print(f"  ✓ {len(ws.state)} 个变量")

# 4. Run simulation with DeepSeek  
print("\n[4/7] 用DeepSeek运行推演...")
from src.simulation_runner import SimulationRunner, SimulationRound
from src.world_state import WorldState

round_defs = data.get("simulation_rounds", [])
runner = SimulationRunner(agents_dict, ws, round_defs)
results = runner.run_all()

print(f"  ✓ 完成 {len(results)} 轮")
for r in results:
    print(f"    第{r['round']}轮: {r.get('title','')}")
    for e in r.get('events',[]):
        print(f"      ▸ {str(e)[:60]}")

timeline = runner.get_timeline()
terminal = runner.terminal_reason
print(f"\n  ⚔️ 终结: {terminal}")

# 5. Plot outline
print("\n[5/7] 生成小说大纲...")
from src.plot_planner import PlotPlanner
planner = PlotPlanner(timeline, ws.to_dict())
outline = planner.generate_outline()
print(f"  ✓ {len(outline)} 字符")

# 6. Chapter 1 with DeepSeek
print("\n[6/7] 用DeepSeek生成第一章...")
# Use DeepSeek for the chapter instead of mock template
chapter_prompt = f"""请根据以下历史推演结果，写一篇历史小说的第一章。

背景：秦始皇三十七年（前210年），沙丘之变后。赵高、李斯、胡亥伪造赐死诏，命扶苏自杀。
穿越设定：李世民（唐太宗）的意识完整穿越到扶苏身上。他知道秦朝将亡，但不知道具体细节。

推演事件：
{chr(10).join(f'- {e}' for r in results[:2] for e in r.get('events',[]))}

要求：
- 文风：历史正剧，有张力、克制、细节丰富
- 人物：李世民（扶苏身体）的内心活动、蒙恬的怀疑
- 长度：2000-3000字
- 语言：中文文学语言，有古风韵味但不晦涩
- 标题：第一章 意识的裂缝"""

chapter = llm.generate(chapter_prompt, 
    system_prompt="你是中国历史小说作家，擅长秦汉题材，文风沉稳有力。",
    temperature=0.8)
print(f"  ✓ {len(chapter)} 字符")

# 7. Consistency check
print("\n[7/7] 一致性检查...")
from src.consistency_checker import ConsistencyChecker
checker = ConsistencyChecker(timeline, outline, ws.to_dict(), agents_dict, data)
report = checker.to_markdown()
print(f"  ✓ 完成")

# Save
output_dir = "outputs/qin_fusu_lishimin_deepseek_run_001"
os.makedirs(output_dir, exist_ok=True)

files = {
    "scenario.json": json.dumps(loader.to_dict(), ensure_ascii=False, indent=2),
    "agents.json": json.dumps(agents_dict, ensure_ascii=False, indent=2),
    "world_state.json": json.dumps(ws.to_dict(), ensure_ascii=False, indent=2),
    "timeline.json": json.dumps(timeline, ensure_ascii=False, indent=2),
    "plot_outline.md": outline,
    "chapter_001.md": chapter,
    "consistency_report.md": report,
}

print(f"\n{'=' * 60}")
print(f"  保存到 {output_dir}/")
for name, content in files.items():
    path = os.path.join(output_dir, name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  ✓ {name} ({len(content)} bytes)")

print(f"\n{'=' * 60}")
print(f"  ✅ 全部完成！DeepSeek 生成")
print(f"  终结原因: {terminal}")
print(f"  📁 {output_dir}/")
