# 历史岔路口小说生成器

> Alt-History Agent Novel Engine

一个基于多智能体推演的**历史架空小说生成器**。不是简单的"AI写小说"，而是先建模历史世界和人物，运行推演，再基于推演结果生成小说。

## 核心理念

```
历史事实 + 架空假设
    ↓
人物Agent建模（8个核心角色）
    ↓
5轮事件推演（每轮：观察→决策→行动→世界状态更新）
    ↓
结构化产物（场景、Agent卡、世界状态、时间线）
    ↓
小说生成（三幕式大纲 + 章节正文）
    ↓
一致性检查
```

## Demo 场景

**「李世民穿越为扶苏——沙丘之变」**

秦始皇三十七年，沙丘之变后。赵高、李斯、胡亥伪造赐死诏，命扶苏自杀。在扶苏准备自杀的关键时刻，李世民（唐朝第二位皇帝）的意识在他身上觉醒。

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 运行
python main.py --scenario scenarios/qin_fusu_lishimin.yaml

# 3. 查看输出
ls outputs/qin_fusu_lishimin_run_001/
```

## 输出产物

运行一次完整生成，产生以下结构化文件：

| 文件 | 说明 |
|------|------|
| `scenario.json` | 场景设定（分歧点、时代背景、Agent定义） |
| `agents.json` | 8个人物Agent卡（目标、资源、恐惧、性格） |
| `world_state.json` | 推演前后的世界状态 |
| `timeline.json` | 5轮推演的时间线 |
| `plot_outline.md` | 三幕式小说大纲 |
| `chapter_001.md` | 第一章正文 |
| `consistency_report.md` | 一致性检查报告 |

## 8个核心人物Agent

| Agent | 角色 | 核心冲突 |
|-------|------|---------|
| 扶苏/李世民 | 主角，融合灵魂 | 生存 vs 孝道，经验 vs 历史 |
| 蒙恬 | 秦大将 | 忠君 vs 保扶苏 |
| 赵高 | 宦官 | 扶胡亥登基，清除异己 |
| 李斯 | 丞相 | 自保 vs 道义 |
| 胡亥 | 傀儡皇子 | 权力欲 vs 无能力 |
| 始皇遗诏 | 制度性Agent | 法理权威 vs 被篡改 |
| 王离及边军 | 军方代表 | 服从 vs 站队 |
| 六国遗民 | 底层暗流 | 等待时机 vs 伺机而动 |

## 5轮推演

1. **意识觉醒**：扶苏接到赐死诏，李世民意识醒来
2. **说服蒙恬**：决定不自杀，说服蒙恬支持
3. **控局与判断**：封锁消息，判断敌我
4. **战略抉择**：南下/北上/派使者
5. **反制与博弈**：赵高集团的反击

## 模式说明

### Mock 模式（默认）
使用内置模板生成，无需API Key，适合测试和演示：
```bash
python main.py --scenario scenarios/qin_fusu_lishimin.yaml --mode mock
```

### LLM 模式（开发中）
接入真实LLM生成更丰富的推演和小说内容：
```bash
python main.py --scenario scenarios/qin_fusu_lishimin.yaml --mode llm --api-key sk-xxx
```

## 项目结构

```
alt-history-agent-novel-engine/
├── main.py              # 主入口
├── scenarios/           # 场景配置（YAML）
├── src/                 # Python模块
│   ├── scenario_loader.py    # 场景加载
│   ├── agent_builder.py      # Agent卡生成
│   ├── world_state.py        # 世界状态管理
│   ├── simulation_runner.py  # 推演引擎
│   ├── plot_planner.py       # 大纲生成
│   ├── chapter_writer.py     # 章节生成
│   ├── consistency_checker.py# 一致性检查
│   └── llm_client.py        # LLM接口
├── data/
│   └── historical_notes/     # 历史背景资料
└── outputs/             # 输出产物
```

## 设计原则

1. **事实与虚构分层**：历史事实、架空设定、推演结果、小说正文分别保存
2. **先推演后写作**：先建模世界运行，再基于推演结果创作
3. **多Agent博弈**：每个角色有独立目标、资源和约束
4. **不降智**：反派（赵高）不过度无能，正派（扶苏）不过度全能
5. **可追溯**：每一轮推演都有记录，小说内容可溯源到具体推演事件

## 下一步开发

详见 [TODO.md](./TODO.md)

## 借鉴

本项目受 [MiroFish](https://github.com/666ghj/MiroFish) / [mirofish-cli](https://github.com/amadad/mirofish-cli) 的多智能体模拟思路启发，将群体智能推演引擎的思路应用于历史架空小说生成。

许可：MIT
