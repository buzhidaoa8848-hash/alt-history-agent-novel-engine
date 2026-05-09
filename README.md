# Alt-History Agent Novel Engine

> 基于多智能体推演的历史架空小说生成器

## 核心理念

**不是"AI直接写小说"，而是：**

```
用户定义(场景+人物+规则)
    ↓
多Agent推演（角色博弈直到有人死亡）
    ↓
结构化输出（场景/Agent卡/世界状态/时间线）
    ↓
小说生成（大纲+章节）
    ↓
一致性检查
```

## 当前状态

**v1.0 — Demo** ✅ 已跑通

- 场景：李世民穿越为扶苏（沙丘之变）
- 推演引擎：Mock（内置模板）或 DeepSeek API
- 输出：8个结构化文件
- 死亡结局：赵高死 / 蒙恬死 / 李世民病逝

## 🚀 产品化方向（v2.0）

### 输入系统
| 输入类型 | 说明 | 示例 |
|---------|------|------|
| **背景** | 历史/现实/架空/小说 | 秦朝 / 2024年 / 中土世界 |
| **人物** | 用户自定义，不替用户做主 | 角色名、性格、目标、资源 |
| **硬约束** | 不可违背的规则 | 常识、物理定律、历史关键节点 |

### 硬约束引擎
- ⚡ **常识约束**：30万精锐边军不会输给农民军
- ⚡ **历史约束**：关键节点的既成事实不可改
- ⚡ **逻辑约束**：人物行为符合其资源+性格
- ⚡ **AI不脑补**：不替用户"创造"人物关系和设定

### 可扩展场景库
- 历史架空（当前）：秦、三国、唐、宋、明…
- 现实推演：如果某公司没破产？如果某战争没发生？
- 小说二创：给已有IP做"if线"

---

## 快速开始

```bash
# Mock模式（无需API，直接看结构）
python main.py --scenario scenarios/qin_fusu_lishimin_data.py

# DeepSeek模式（真实AI推演）
# 需要先设置 DEEPSEEK_API_KEY
python run_deepseek.py
```

## 项目结构

```
alt-history-agent-novel-engine/
├── main.py                    # 主入口（Mock模式）
├── run_deepseek.py            # DeepSeek运行脚本
├── test_deepseek.py           # API测试
├── scenarios/                 # 场景定义
│   ├── qin_fusu_lishimin_data.py   # Demo场景
│   └── qin_fusu_lishimin.yaml      # 原始YAML
├── src/                       # 核心模块
│   ├── scenario_loader.py     # 场景加载
│   ├── agent_builder.py       # Agent卡生成
│   ├── world_state.py         # 世界状态
│   ├── simulation_runner.py   # 推演引擎
│   ├── plot_planner.py        # 大纲生成
│   ├── chapter_writer.py      # 章节生成
│   ├── consistency_checker.py # 一致性检查
│   └── llm_client.py          # LLM接口（支持DeepSeek）
├── data/historical_notes/     # 历史背景资料
└── outputs/                   # 输出产物
```

## Demo场景

**李世民穿越为扶苏——沙丘之变**

秦始皇三十七年，赵高李斯伪造赐死诏。在扶苏即将自杀的时刻，李世民（唐太宗）的意识完整穿越而来。他知道秦朝将亡，有30万边军，有军事天才——但真正的问题是：打赢了以后怎么办？

- 12章完整故事大纲 ✅
- 第一章正文 ✅
- 3个确定死亡结局 ✅
- 主题："历史可以改变，但代价永远比你想象的大"

## 技术栈

- Python 3.11+
- DeepSeek API（可选，Mock模式可独立运行）
- 无需数据库、无需前端、纯CLI
