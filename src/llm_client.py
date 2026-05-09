"""
LLM Client Interface

Provides a unified interface for LLM calls.
In mock mode, generates structured outputs using templates.
In real mode, calls configured LLM API.

Reference: mirofish-cli app/utils/llm_client.py pattern
"""

import json
import random
from typing import Optional


class LLMClient:
    """LLM interaction client. Defaults to mock mode for MVP."""

    def __init__(self, mode: str = "mock", config: Optional[dict] = None):
        self.mode = mode
        self.config = config or {}
        self._mock_seed = 42

    def generate(self, prompt: str, system_prompt: str = "", temperature: float = 0.7) -> str:
        """Generate text from prompt. In mock mode, returns templated response."""
        if self.mode == "mock":
            return self._mock_generate(prompt, system_prompt)
        return self._real_generate(prompt, system_prompt, temperature)

    def generate_json(self, prompt: str, system_prompt: str = "",
                      temperature: float = 0.3) -> dict:
        """Generate structured JSON output."""
        text = self.generate(prompt, system_prompt, temperature)
        # Try to extract JSON from response
        try:
            # Find JSON boundaries
            start = text.find('{')
            end = text.rfind('}') + 1
            if start >= 0 and end > start:
                return json.loads(text[start:end])
            return json.loads(text)
        except (json.JSONDecodeError, ValueError):
            return {"error": "Failed to parse JSON", "raw": text[:200]}

    def _mock_generate(self, prompt: str, system_prompt: str = "") -> str:
        """Generate mock responses based on prompt keywords."""
        prompt_lower = prompt.lower()

        if "agent" in prompt_lower or "人物卡" in prompt_lower or "角色" in prompt_lower:
            return self._mock_agent_response(prompt)
        elif "事件" in prompt_lower or "推演" in prompt_lower or "simulation" in prompt_lower or "round" in prompt_lower:
            return self._mock_event_response(prompt)
        elif "章节" in prompt_lower or "chapter" in prompt_lower or "正文" in prompt_lower:
            return self._mock_chapter_response(prompt)
        elif "大纲" in prompt_lower or "outline" in prompt_lower or "plot" in prompt_lower:
            return self._mock_outline_response(prompt)
        elif "一致" in prompt_lower or "consistency" in prompt_lower or "检查" in prompt_lower:
            return self._mock_consistency_response(prompt)
        else:
            return f"[Mock LLM Response for: {prompt[:100]}...]"

    def _mock_agent_response(self, prompt: str) -> str:
        """Generate mock agent card in JSON."""
        return json.dumps({
            "analysis": f"Agent analysis based on: {prompt[:80]}",
            "personality_traits": ["果断", "谨慎", "重情义"],
            "likely_response": "会先观察局势再做决定",
            "decision_factors": ["自身安全", "家族利益", "道义"],
            "uncertainty": "中等",
            "temp_result": "Mock agent card generated"
        }, ensure_ascii=False, indent=2)

    def _mock_event_response(self, prompt: str) -> str:
        """Generate mock event simulation output."""
        events = [
            "扶苏暂缓自杀决定，命人暗中监视使者动向。",
            "蒙恬封锁上郡军营，禁止任何人出入。",
            "赵高在咸阳得知扶苏未死，加速夺权步伐。",
            "王离暗中派出信使向咸阳报告。",
            "六国遗民得知秦廷内乱，开始秘密串联。"
        ]
        return json.dumps({
            "event": f"Round simulation: {prompt[:60]}",
            "key_developments": random.sample(events, 3),
            "world_state_changes": {
                "fusu_survival_risk": "降低",
                "meng_tian_loyalty": "巩固",
                "zhao_gao_control": "加强咸阳控制",
                "information_leak_risk": "增加"
            },
            "narrative_material": "李世民用军事经验判断诏书伪造手法不专业",
            "risk_flags": ["王离不可靠", "时间紧迫"]
        }, ensure_ascii=False, indent=2)

    def _mock_chapter_response(self, prompt: str) -> str:
        """Generate mock chapter text."""
        return """# 第一章 意识的裂缝

秦始皇三十七年，七月。

上郡的夏天干燥而炎热，风从塞外吹来，裹着沙土和马粪的气味。军营中异常的安静——不是因为戒备，而是因为恐惧。

扶苏睁开眼睛时，最先感受到的不是疼痛，而是一种巨大的错位感。

他前一秒还在长安城的玄武门——不，那不对。他是扶苏，始皇的长子，此刻应该在上郡的大营中。可是为什么他的脑海中还残留着刀剑相击的声音、马匹的嘶鸣、以及一种更为尖锐的——兄弟相残的痛苦？

"公子？公子！"

有人在叫他。声音很急，带着压抑的焦虑。

扶苏——或者说，占据着扶苏身体的那个意识——缓慢地将视线聚焦。一个身披铁甲、面容刚毅的中年将领正俯身看着他，眼中满是担忧和急切。

蒙恬。

这个名字从记忆深处浮现，伴随着一股复杂的情绪——一部分是扶苏对这位大将的信任，另一部分……来自何处？是一种本能的判断力，一种从对方的眼神中读取忠诚和能力的经验。

"公子，诏书……"蒙恬压低声音，"臣以为此事蹊跷。"

诏书。赐死。

这两个词像冷水一样浇下来，让那混乱的意识瞬间清晰了几分。记忆如潮水般涌来——他是扶苏，因为劝谏父皇而被派来上郡监军；他刚刚接到了父皇的诏书，指责他"诽谤""怨望"，赐他自尽；父皇的使者就在营外等候回复；按照礼法，他应该哭泣、谢恩、然后……

然后死。

可是为什么，他内心深处有一股强烈的冲动在呐喊——不。

这不像扶苏。

扶苏是孝子，从不会质疑父皇的决定。可是此刻，在这个身体里，有另一个人在冷笑，在审视那道诏书，在用一种近乎冷酷的政治眼光分析着每一个字的含义。

"蒙将军，"他开口，声音沙哑得不像自己的，"那道诏书……"

他停住了。

因为他本来想说"那道诏书有问题"，可这是扶苏应该说出来的话吗？扶苏应该问的是"父皇为何如此绝情"，而不是直接质疑诏书的真实性。

但那个声音——来自另一个时代的意识——在告诉他：权力的游戏里，诏书从来都是最不可信的东西。他曾亲眼见过……

他猛地摇头，让那个念头散去。

他是扶苏。他是始皇的长子。他要……

他要活着。

这个决定来得如此坚定、如此清晰、如此不像扶苏，以至于他自己都愣了一下。"""

    def _mock_outline_response(self, prompt: str) -> str:
        """Generate mock plot outline."""
        return """# 小说大纲：《历史岔路口·扶苏未死》

## 三幕式结构

### 第一幕：沙丘之影（第1-3章）
- 核心冲突：生死抉择
- 第1章：李世民意识觉醒，决定不自杀
- 第2章：说服蒙恬，控制上郡军心
- 第3章：确认诏书伪造，开始布局反制
- 情感线：两个灵魂的磨合，李世民的果断与扶苏的仁厚开始融合

### 第二幕：帝国裂痕（第4-8章）
- 核心冲突：夺权与博弈
- 第4章：赵高加速夺权，蒙毅被捕
- 第5章：李世民派使者联络咸阳各方
- 第6章：李斯的摇摆与抉择
- 第7章：边军分裂危机，王离密谋
- 第8章：胡亥登基，李世民的"合法"窗口关闭

### 第三幕：历史岔路口（第9-12章）
- 核心冲突：决战与抉择
- 第9章：李世民率部分边军南下
- 第10章：六国遗民观望与行动
- 第11章：咸阳决战
- 第12章：新帝国的可能未来（开放式结局）

## 主要情节线
1. **权力线**：真假诏书 → 夺权战争 → 新的权力格局
2. **性格线**：李世民决策方式 vs 秦朝制度约束
3. **历史线**：秦制 vs 仁政的路径选择
4. **军事线**：边军内部站队 → 南下 → 咸阳攻防

## 主题
权力的合法性来自何处？制度还是人心？
一个人能否在历史的惯性中做出真正的改变？
"""

    def _mock_consistency_response(self, prompt: str) -> str:
        """Generate mock consistency report."""
        return """# 一致性检查报告

## 检查结果：⚠️ 部分通过（2项问题）

### ✅ 通过项
1. **时间线一致性**：所有事件按日期排列，无前后矛盾
2. **人物信息边界**：李世民未获取穿越前不该知道的信息
3. **资源约束**：蒙恬边军动用受粮草限制，合理
4. **架空分歧点清晰**：扶苏未自杀是唯一分歧点

### ⚠️ 警告项
5. **蒙毅角色一致性**：第3章中蒙毅的反应与史实有细微出入——史实中蒙毅在始皇病重时已被派往山川祭祀，此时是否在咸阳需确认 → 建议：在第2章加一句说明蒙毅行踪
6. **赵高信息速度**：赵高从沙丘到咸阳的路线与上郡到咸阳的路线有时间差，第4轮推演中赵高反应速度需要调整

### ❌ 未发现严重问题

## 改进建议
1. 在 historical_notes 中补充蒙毅行踪的史料
2. 调整第4轮推演的时间计算——赵高收到消息的时间应比目前设定晚3天
"""
        return ""

    def _real_generate(self, prompt: str, system_prompt: str = "", temperature: float = 0.7) -> str:
        """Real LLM call - requires API configuration."""
        raise NotImplementedError(
            "Real LLM mode not yet configured. "
            "Set mode='mock' or configure API key in config."
        )


# Singleton
_client: Optional[LLMClient] = None


def get_client(mode: str = "mock", config: Optional[dict] = None) -> LLMClient:
    """Get or create the LLM client singleton."""
    global _client
    if _client is None:
        _client = LLMClient(mode=mode, config=config)
    return _client


def reset_client():
    """Reset the LLM client singleton."""
    global _client
    _client = None
