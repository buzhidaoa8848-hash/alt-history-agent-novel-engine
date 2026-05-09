"""
Plot Planner

Generates a structured novel plot outline from simulation timeline data.
Uses three-act structure with clear causal chains.
"""

from typing import Any, Dict, List


class PlotPlanner:
    """Generates novel outline from simulation results."""

    def __init__(self, timeline: Dict[str, Any], world_state: Dict[str, Any]):
        self.timeline = timeline
        self.world_state = world_state
        self.rounds = timeline.get("rounds", [])

    def generate_outline(self) -> str:
        """Generate full plot outline in markdown."""
        acts = self._build_three_acts()

        outline = f"""# 小说大纲：历史岔路口·李世民穿越为扶苏

> 基于多智能体推演结果生成
> 分歧点：扶苏接到赐死诏，李世民意识觉醒
> 推演轮次：{len(self.rounds)} 轮

---

## 三幕式结构

"""
        for act in acts:
            outline += f"## {act['title']}\n\n"
            outline += f"**核心冲突**：{act['core_conflict']}\n\n"
            outline += f"**覆盖章节**：{act['chapters']}\n\n"
            outline += f"**关键事件链**：\n\n"
            for i, event in enumerate(act['events'], 1):
                outline += f"{i}. {event}\n"
            outline += "\n"
            outline += f"**情感线**：{act['emotional_arc']}\n\n"
            if act.get('key_decisions'):
                outline += f"**关键决策**：\n\n"
                for d in act['key_decisions']:
                    outline += f"- {d}\n"
                outline += "\n"
            outline += "---\n\n"

        # Additional sections
        outline += self._generate_character_arcs()
        outline += self._generate_theme_analysis()
        outline += self._generate_chapter_by_chapter()

        return outline

    def _build_three_acts(self) -> List[Dict[str, Any]]:
        """Build three-act structure from timeline data."""
        total_rounds = len(self.rounds)
        return [
            {
                "title": "第一幕：沙丘之影（第1-3章）",
                "core_conflict": "生死抉择——扶苏/李世民是否接受赐死诏书。李世民带着对秦亡的恐惧醒来。",
                "chapters": "第1章 意识的裂缝 / 第2章 将军的抉择 / 第3章 封营",
                "events": self._extract_events_for_range(0, min(2, total_rounds - 1)),
                "emotional_arc": "从绝望到疑惑，从被动到主动。李世民知道自己必须阻止秦亡，但第一步是活下去。",
                "key_decisions": [
                    "扶苏（李世民）决定暂缓自杀——他知道自杀等于让秦朝走上灭亡之路",
                    "蒙恬决定支持扶苏核查诏书",
                    "决定封锁上郡大营",
                ],
            },
            {
                "title": "第二幕：帝国裂痕（第4-8章）",
                "core_conflict": "夺权与博弈——扶苏知道秦朝要亡但不知道如何阻止。他的唐代经验在秦朝完全不适用。",
                "chapters": "第4章 三条路 / 第5章 咸阳的暗流 / 第6章 李斯的天平 / "
                          "第7章 边军暗战 / 第8章 沙丘回声",
                "events": self._extract_events_for_range(2, min(4, total_rounds - 1)),
                "emotional_arc": "李世民的唐式思维与秦制激烈碰撞。他想用仁政但秦制不允许，他想改革但权力基础不稳。",
                "key_decisions": [
                    "决定双管齐下：同时向咸阳和西方派出密使",
                    "王离暴露，被软禁在军中",
                    "赵高提前公布始皇死讯",
                    "李斯开始暗中留退路",
                ],
            },
            {
                "title": "第三幕：历史岔路口（第9-12章）",
                "core_conflict": "决战与存亡——多方势力摊牌，角色走向各自的命运终点",
                "chapters": "第9章 匈奴南下 / 第10章 咸阳变局 / 第11章 最终对峙 / 第12章 宿命的终点",
                "events": self._extract_events_for_range(5, total_rounds - 1) if total_rounds > 5 else
                         self._generate_future_events(),
                "emotional_arc": "从被迫应对到主动出击。李世民开始理解——改变历史不是靠制度移植，而是靠人心。",
                "key_decisions": [
                    "决定率部分边军南下（或北上巩固边防——取决于前5轮推演结果）",
                    "与六国遗民的关系策略",
                    "最终与赵高集团的对决方式",
                    "各角色的最终命运——谁活到了最后",
                ],
            },
        ]

    def _extract_events_for_range(self, start: int, end: int) -> List[str]:
        """Extract key events from timeline rounds."""
        events = []
        for round_data in self.rounds[start:end + 1]:
            round_events = round_data.get("events", [])
            events.extend(round_events[:3])  # Take top 3 events per round
        return events[:8]  # Cap at 8

    def _generate_future_events(self) -> List[str]:
        """Generate projected events for unwritten acts."""
        return [
            "扶苏与蒙恬就是否南下产生激烈争论",
            "赵高在咸阳宣布胡亥登基，扶苏成为'叛逆'",
            "边军出现分裂，部分军官公开质疑扶苏的合法性",
            "六国故地开始出现反秦武装",
            "扶苏必须在民心、军心、法理之间做出选择",
            "最终决定：南下或另立朝廷",
        ]

    def _generate_character_arcs(self) -> str:
        """Generate character development arcs."""
        return """## 人物弧光

### 扶苏/李世民
- **起点**：两种人格的剧烈冲突——仁厚与铁血、孝道与权谋
- **发展**：李世民的决断力逐渐主导，但扶苏的仁厚也开始影响李世民
- **终点**：融合——既有李世民的军事才能,又有扶苏的仁德之心
- **核心问题**：权力的合法性来自制度,还是来自人心？

### 蒙恬
- **起点**：忠君爱国的秦军大将，家族荣誉高于一切
- **发展**：在忠君与保扶苏之间反复挣扎，开始质疑诏书的合法性
- **终点**：从制度忠诚转向对人的忠诚
- **核心问题**：当法律被篡改，忠君还是忠义？

### 赵高
- **起点**：阴险的政治投机者，精准但不失算
- **发展**：随着局势失控，开始暴露残暴本性
- **终点**：为权力不择手段，最终被权力反噬
- **核心问题**：纯粹的邪恶是否有持久的生命力？

### 李斯
- **起点**：秦制设计师，陷入自保与道义的困境
- **发展**：逐步意识到与赵高合作是饮鸩止渴
- **终点**：在关键时刻做出选择——但为时已晚或绝地反击？
- **核心问题**：聪明人为什么总是做出愚蠢的决定？

"""

    def _generate_theme_analysis(self) -> str:
        """Generate thematic analysis."""
        return """## 主题分析

### 核心主题
**权力的合法性来自何处？制度还是人心？**

### 次级主题
1. **历史惯性**：一个人的意志能否改变历史的方向？
2. **忠君与忠义**：当制度被篡改，忠诚的边界在哪里？
3. **穿越的意义**：经验与知识的价值——李世民的唐代经验在秦朝意味着什么？
4. **秦制与仁政**：帝国治理的两种路径

### 悬念设计
- 李世民何时知道秦朝灭亡的真相？（如果他知道的话）
- 胡亥是否会有独立意志？
- 六国遗民的真正实力？
- 蒙毅的生死？

"""

    def _generate_chapter_by_chapter(self) -> str:
        """Generate chapter-by-chapter breakdown."""
        return """## 分章纲要

### 第1章：意识的裂缝
- 扶苏接到赐死诏
- 李世民意识觉醒
- 两个灵魂的初次交锋
- 决定暂缓自杀

### 第2章：将军的抉择
- 蒙恬的内心挣扎
- 密谈至深夜
- 蒙恬决定支持扶苏
- 王离的警觉

### 第3章：封营
- 封锁上郡大营
- 控制朝廷使者
- 军中站队开始
- 王离被监视

### 第4章：三条路
- 战略讨论：北上/南下/等待
- 信息匮乏下的决策困境
- 决定双管齐下
- 密使出发

### 第5章：咸阳的暗流
- 赵高加速夺权
- 蒙毅被捕
- 李斯的内心交战
- 扶苏未死的消息传到沙丘

### 第6章：李斯的天平
- 从赵高视角看局势
- 李斯的重新计算
- 胡亥的登基准备
- 朝中暗流

### 第7章：边军暗战
- 王离的秘密行动
- 军中分化加剧
- 蒙恬的艰难抉择
- 扶苏展示军事才能

### 第8章：沙丘回声
- 赵高的反制措施
- 李斯的摇摆
- 扶苏收到的第一封咸阳密信
- 决定性的选择时刻

### 后续章节（第9-12章）
- 南下或北上——战略抉择
- 与赵高集团的公开对抗
- 六国遗民的变量
- 开放式结局

"""
