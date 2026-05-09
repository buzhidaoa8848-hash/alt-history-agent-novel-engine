"""
Simulation Runner

Runs multi-agent simulation rounds.
Each round: observe → decide → act → update world state.

Inspired by mirofish-cli's RunSimulationTool + OASIS pattern,
but simplified for narrative simulation rather than social media.
"""

import json
import random
from typing import Any, Dict, List, Optional

from src.llm_client import get_client
from src.world_state import WorldState


class SimulationRound:
    """A single round of historical event simulation."""

    def __init__(self, round_id: int, definition: Dict[str, Any]):
        self.round_id = round_id
        self.title = definition.get("title", f"Round {round_id}")
        self.trigger = definition.get("trigger", "")
        self.key_conflicts = definition.get("key_conflicts", [])
        self.result: Dict[str, Any] = {}

    def run(self, agents: List[Dict], world_state: WorldState) -> Dict[str, Any]:
        """Execute this simulation round."""
        llm = get_client()

        # Prepare round context
        round_context = self._build_context(agents, world_state)

        # If using mock, generate structured outputs directly
        if llm.mode == "mock":
            result = self._mock_run(agents, world_state)
        else:
            result = self._llm_run(round_context, agents, world_state)

        # Record in world state
        world_state.record_round(self.round_id, result)

        # Update agent states based on round outcomes
        self._update_agents(agents, result, world_state)

        self.result = result
        return result

    def _build_context(self, agents: List[Dict], world_state: WorldState) -> str:
        """Build context string for this round."""
        context = f"""
## Round {self.round_id}: {self.title}

### Trigger
{self.trigger}

### Key Conflicts
{chr(10).join(f'- {c}' for c in self.key_conflicts)}

### Current World State
{json.dumps(world_state.snapshot(), ensure_ascii=False, indent=2)}

### Active Agents
"""
        for a in agents:
            context += f"\n- {a.get('name', 'Unknown')} ({a.get('identity', '')})"
            context += f"\n  Status: {a.get('current_status', '待机')}"
            context += f"\n  Goals: {a.get('core_goals', [])[:2]}"

        return context

    def _llm_run(self, context: str, agents: List[Dict], world_state: WorldState) -> Dict[str, Any]:
        """Run simulation round using real LLM."""
        llm = get_client()

        prompt = f"""你是一个历史推演引擎。请基于以下场景信息，模拟本轮历史推演。

{context}

请按以下JSON格式输出（只输出JSON，不要其他文字）：

{{
  "events": ["事件1", "事件2", "事件3", "事件4", "事件5"],
  "agent_observations": [
    {{"agent": "角色名", "observes": "观察到什么", "information_gap": "信息缺口"}}
  ],
  "agent_actions": [
    {{"agent": "角色名", "action": "采取什么行动", "success_probability": 60}}
  ],
  "conflicts": ["冲突1", "冲突2"],
  "world_state_updates": {{
    "变量名": 新数值
  }},
  "narrative_material": "一段可用于小说写作的叙事素材",
  "risk_flags": ["风险1", "风险2"]
}}

注意：
- 李世民是完整穿越，没有扶苏人格残留
- 李世民知道秦朝将亡（陈胜吴广、刘邦项羽），但不知道细节
- 李世民有唐代经验但秦朝无法直接使用
- 赵高、李斯、胡亥都是理性人，不会降智
- 蒙恬有忠君与保扶苏之间的内心冲突
- 每次推演要推动故事向前发展
- 世界状态变量的数值范围0-100"""

        system = "你是专业历史推演AI，擅长多Agent博弈模拟。输出严格JSON格式。"

        response = llm.generate(prompt, system, temperature=0.8)
        result = self._parse_llm_response(response)

        if not result:
            # Fallback to mock if LLM fails
            print(f"  ⚠️ 第{self.round_id}轮LLM输出解析失败，使用mock回退")
            result = self._mock_run(agents, world_state)

        # Update world state
        updates = result.get("world_state_updates", {})
        if updates:
            world_state.update(updates)
            result["world_state_update"] = updates

        return result

    def _parse_llm_response(self, response: str) -> Dict:
        """Parse LLM JSON response with fallback."""
        import re, json

        # Try to find JSON in response
        try:
            # Find JSON block
            match = re.search(r'\{[\s\S]*\}', response)
            if match:
                data = json.loads(match.group())
                # Validate required fields
                if "events" in data or "agent_observations" in data:
                    return data
        except (json.JSONDecodeError, ValueError, KeyError):
            pass

        # If response is small, it might be an error message
        if len(response) < 50:
            print(f"  ⚠️ LLM返回太短: {response[:100]}")
            return {}

        # Second attempt: try to find JSON in the full text
        try:
            start = response.find('{')
            end = response.rfind('}') + 1
            if start >= 0 and end > start:
                data = json.loads(response[start:end])
                return data
        except (json.JSONDecodeError, ValueError):
            pass

        return {}

    def _mock_run(self, agents: List[Dict], world_state: WorldState) -> Dict[str, Any]:
        """Run simulation with mock logic (for MVP without LLM)."""
        # Deterministic mock based on round number
        seed = self.round_id * 42

        # Build agent observations (what each agent perceives)
        agent_observations = []
        for a in agents:
            agent_observations.append({
                "agent": a.get("name", "Unknown"),
                "observes": self._mock_observation(a, self.round_id),
                "information_gap": random.Random(seed + hash(a.get("id", ""))).choice(
                    ["知道部分真相", "信息被封锁", "掌握关键信息", "被误导"]
                ),
            })

        # Build agent actions
        agent_actions = []
        for a in agents:
            agent_actions.append({
                "agent": a.get("name", "Unknown"),
                "action": self._mock_action(a, self.round_id),
                "success_probability": random.Random(seed * 3 + hash(a.get("id", ""))).randint(30, 80),
            })

        # Generate events for this round
        events = self._generate_round_events(self.round_id, agents)

        # Generate narrative material
        narrative_material = self._mock_narrative(self.round_id)

        # Calculate world state updates
        state_updates = self._calculate_state_updates(self.round_id, events)

        # Update world state
        world_state.update(state_updates)

        # Identify conflicts
        conflicts = self._identify_conflicts(agents, self.round_id)

        return {
            "round": self.round_id,
            "title": self.title,
            "agent_observations": agent_observations,
            "agent_actions": agent_actions,
            "events": events,
            "conflicts": conflicts,
            "world_state_update": state_updates,
            "narrative_material": narrative_material,
            "risk_flags": self._generate_risk_flags(self.round_id),
        }

    def _mock_observation(self, agent: Dict, round_id: int) -> str:
        """Generate mock observation for an agent."""
        observations = {
            "fusulishimin": [
                "感知到身体异常——意识中有另一个人的记忆和思维模式",
                "确认诏书细节，发现多处可疑之处",
                "观察到蒙恬的神色异常——他也在怀疑",
                "发现脑海中浮现出不属于自己的军事判断力",
            ],
            "meng_tian": [
                "注意到扶苏神色异常——与平日不同",
                "再次审视诏书，发现笔迹有细微可疑",
                "意识到军中已有人知道诏书内容",
                "评估王离的态度——他过于平静",
            ],
            "zhao_gao": [
                "收到密报：上郡方向尚无异常",
                "加速清理咸阳中的异己分子",
                "安排蒙毅被捕的密令已发出",
                "开始准备始皇发丧和新君继位的仪式",
            ],
            "li_si": [
                "内心不安——赵高的控制越来越强",
                "收到上郡方向的消息但被赵高拦截",
                "开始暗中保留一些文书证据",
                "担忧家族未来——扶苏若不死自己的路就绝了",
            ],
            "hu_hai": [
                "兴奋地准备登基事宜",
                "对赵高言听计从",
                "开始幻想当皇帝后的生活",
                "对扶苏的生死不关心——赵高说没事就没事",
            ],
            "imperial_decree": [
                "制度惯性仍在运行——秦法不因人废",
                "真诏书被扣留，但法理上扶苏是合法继承人",
                "假诏书正在被执行，但漏洞开始显现",
            ],
            "frontier_generals": [
                "低级军官在私下议论诏书之事",
                "王离收到来自咸阳的密信",
                "士兵们注意到军营气氛异常",
                "蒙恬的心腹将领表达了对扶苏的支持",
            ],
            "six_states_observer": [
                "六国故地出现关于始皇已死的传言",
                "秘密集会增多",
                "部分遗民贵族开始暗中积蓄力量",
                "张良等人在观察秦廷动向",
            ],
        }
        agent_id = agent.get("id", "")
        possible = observations.get(agent_id, ["观察到异常情况"])
        idx = (round_id - 1) % len(possible)
        return possible[idx]

    def _mock_action(self, agent: Dict, round_id: int) -> str:
        """Generate mock action for an agent."""
        actions = {
            "fusulishimin": [
                '暂缓自杀，以需要时间「思考」为由拖延',
                "秘密召见蒙恬，以新获得的犀利视角分析诏书疑点",
                "下令封锁上郡大营，控制所有出入通道",
                "派出最信任的使者，以私人身份前往咸阳探听虚实",
            ],
            "meng_tian": [
                "向扶苏表示愿意一同核实诏书真伪",
                "下令边军进入戒备状态，对外称'防匈奴'",
                "秘密接触军中可靠将领，评估支持度",
                "以军务为由扣留朝廷使者",
            ],
            "zhao_gao": [
                "下令加速返回咸阳的行程",
                "以皇帝名义发出密令，命王离密切监视蒙恬",
                "开始散布扶苏'抗旨'的消息，为公开定罪做准备",
                "诱捕蒙毅，作为要挟蒙恬的筹码",
            ],
            "li_si": [
                "表面配合赵高，暗中记录赵高的每一步行动",
                "以丞相身份发出公文，维持帝国行政运转",
                "秘密接触右丞相冯去疾，试探其态度",
                "开始评估如果扶苏南下，自己该如何站队",
            ],
            "hu_hai": [
                "沉浸在即将登基的兴奋中",
                "听从赵高安排练习秦始皇的言行举止",
                "对朝政毫无兴趣",
                "开始对服侍自己的人颐指气使",
            ],
            "imperial_decree": [
                "制度上，始皇的权威仍在约束所有人",
                "真诏书被隐藏，但法理效力未消失",
                "假诏书每多执行一天，就多一分既成事实的效力",
            ],
            "frontier_generals": [
                "王离收到密令后开始暗中拉拢中层军官",
                "蒙恬嫡系将领表态支持蒙恬",
                "基层士兵对情况一无所知，只听说'朝中有变'",
                "部分将领持观望态度——不敢得罪任何一方",
            ],
            "six_states_observer": [
                "楚国贵族秘密会面，讨论起兵可能性",
                "韩国遗民张良加紧联络各方势力",
                "齐国田氏家族在观望咸阳局势",
                "赵地民间出现'始皇已死'的传言",
            ],
        }
        agent_id = agent.get("id", "")
        possible = actions.get(agent_id, ["无行动"])
        idx = (round_id - 1) % len(possible)
        return possible[idx]

    def _generate_round_events(self, round_id: int, agents: List[Dict]) -> List[str]:
        """Generate events for this round."""
        round_events = {
            1: [
                "扶苏接到赐死诏书，痛哭欲自杀",
                "蒙恬紧急劝阻，指出诏书疑点",
                "李世民意识在扶苏体内觉醒",
                "两名灵魂在同一个身体中产生剧烈冲突",
                "使者在外营催促回复",
            ],
            2: [
                "扶苏以'父皇之恩当深思'为由暂缓自杀",
                "蒙恬与扶苏密谈至深夜",
                "蒙恬开始怀疑诏书真实性",
                "王离注意到军营中的异常",
                "扶苏开始用新的眼光审视周围每一个人",
            ],
            3: [
                "蒙恬下令封锁上郡军营",
                "扶苏秘密召见几名可靠将领",
                "王离试图派出信使被蒙恬截获",
                "军中开始流传'诏书有假'的传言",
                "扶苏决定派人去咸阳打探消息",
            ],
            4: [
                "扶苏与蒙恬讨论三种选择：北上、南下、谈判",
                "蒙恬主张先确认始皇是否在世",
                "扶苏（李世民经验）主张双管齐下——同时派人向南和向西",
                "王离被发现与咸阳有密信往来",
                "边军开始出现站队分化",
            ],
            5: [
                "赵高在行营收到扶苏未死的密报",
                "赵高紧急召见李斯商议对策",
                "胡亥得知消息后惊慌失措",
                "李斯内心开始产生动摇",
                "赵高决定提前公布始皇死讯，加速胡亥登基",
            ],
        }
        return round_events.get(round_id, ["暂无事件"])

    def _mock_narrative(self, round_id: int) -> str:
        """Generate narrative material for this round."""
        narratives = {
            1: (
                "这是意识与意识的碰撞。李世民刚刚经历玄武门的刀光剑影，"
                "转眼间却发现自己身处另一个时代、另一具身体、另一场生死抉择。"
                "扶苏的仁厚在哭泣，李世民的铁血在咆哮。"
                "赐死诏书就摆在案上，墨迹已干，但字字如刀。"
            ),
            2: (
                "蒙恬的目光在烛火中闪烁不定。这个在战场上从不退缩的将军，"
                "此刻面对一道诏书，手在微微颤抖。他见过太多朝堂上的阴谋，"
                "但从未想过有一天会落在自己身上。扶苏的不对劲他注意到了——"
                "这个平时仁厚到近乎软弱的公子，此刻的眼神竟像一头苏醒的猛兽。"
            ),
            3: (
                "上郡大营从未如此安静，也从未如此危险。"
                "每个人都在观察，每个人都在计算。"
                "王离在自己的营帐中来回踱步，手中握着咸阳的密信，"
                "信上的每一个字都足以让这个帝国震动。"
            ),
            4: (
                "扶苏面前摊开着一幅简略的天下舆图。上郡在北，咸阳在西，"
                "东方是曾经的六国故地。每一条路都通向不同的结局。"
                "李世民的军事直觉告诉他：时间不在自己这边。"
                "蒙恬的忠君观念在告诉他：每一步都必须有法理依据。"
            ),
            5: (
                "沙丘的暑气未散，但赵高感到一阵寒意。"
                "扶苏没死。这四个字像一把匕首抵在他的后颈。"
                "如果扶苏活着南下，如果蒙恬的三十万边军跟着南下……"
                "他看了看身边的胡亥——这个年轻人还在做梦，"
                "完全不知道他们共同编织的网已经开始出现裂口。"
            ),
        }
        return narratives.get(round_id, "叙事素材生成中……")

    def _calculate_state_updates(self, round_id: int, events: List[str]) -> Dict[str, Any]:
        """Calculate world state changes for this round."""
        updates = {
            1: {
                "protagonist_survival_risk": 60,
                "protagonist_identity_integration": 30,
                "meng_tian_loyalty": 85,
                "meng_tian_willingness_to_rebel": 15,
                "truth_about_decree": 10,
                "time_pressure": 85,
                "narrative_tension": 90,
            },
            2: {
                "protagonist_survival_risk": 50,
                "protagonist_identity_integration": 40,
                "meng_tian_willingness_to_rebel": 25,
                "border_army_stability": 70,
                "truth_about_decree": 20,
                "wang_li_reliability": 45,
            },
            3: {
                "protagonist_survival_risk": 45,
                "zhao_gao_information_control": 65,
                "border_army_stability": 65,
                "truth_about_decree": 30,
                "wang_li_reliability": 35,
                "meng_tian_willingness_to_rebel": 35,
                "narrative_tension": 85,
            },
            4: {
                "fusu_military_power": 55,
                "meng_tian_willingness_to_rebel": 40,
                "border_army_stability": 60,
                "time_pressure": 90,
                "public_unrest": 45,
                "six_states_restoration_risk": 55,
            },
            5: {
                "zhao_gao_information_control": 75,
                "li_si_commitment_to_conspiracy": 75,
                "xianyang_control": 70,
                "succession_legitimacy": 25,
                "time_pressure": 95,
                "public_unrest": 50,
                "six_states_restoration_risk": 55,
                "meng_yi_safety": 30,
                "narrative_tension": 95,
            },
        }
        return updates.get(round_id, {})

    def _identify_conflicts(self, agents: List[Dict], round_id: int) -> List[str]:
        """Identify conflicts arising from this round."""
        all_conflicts = {
            1: [
                "扶苏（孝）vs 李世民（生存）：同一身体中的意志冲突",
                "扶苏/李世民 vs 诏书：是否接受的生死抉择",
                "蒙恬 vs 职责：忠君与保扶苏的两难",
            ],
            2: [
                "蒙恬 vs 秦法：抗旨与忠君的内心撕裂",
                "扶苏（李世民）vs 蒙恬：李世民的激进 vs 蒙恬的谨慎",
                "王离 vs 蒙恬：军中权力暗流",
            ],
            3: [
                "扶苏 vs 未知：信息封锁下的决策困境",
                "王离 vs 蒙恬嫡系：边军内部站队",
                "赵高 vs 时间：必须在真相扩散前完成布局",
            ],
            4: [
                "南下 vs 北上 vs 等待：三种战略选择的冲突",
                "蒙恬的忠君 vs 李世民的实用主义",
                "公开讨赵高 vs 暗中积蓄力量",
            ],
            5: [
                "赵高 vs 李斯：同盟开始出现裂痕",
                "胡亥的无知 vs 现实的残酷",
                "赵高集团 vs 扶苏集团：公开对抗开始",
                "六国遗民 vs 秦廷：暗流涌动",
            ],
        }
        return all_conflicts.get(round_id, ["潜在冲突"])

    def _generate_risk_flags(self, round_id: int) -> List[str]:
        """Generate risk flags for this round."""
        risks = {
            1: ["扶苏随时可能被扶苏人格反噬", "使者可能等不及而回报咸阳"],
            2: ["王离可能已经向咸阳密报", "蒙恬的忠诚经不起反复拉扯"],
            3: ["消息封锁不可能持久", "王离的立场越来越危险"],
            4: ["任何战略选择都有致命风险", "时间窗口正在快速关闭"],
            5: ["赵高可能提前公布始皇死讯", "蒙毅的安危越发危急"],
        }
        return risks.get(round_id, ["潜在风险"])

    def _update_agents(self, agents: List[Dict], result: Dict, world_state: WorldState):
        """Update agent states based on round outcomes."""
        # Update loyalty/morale based on events
        for agent in agents:
            agent_id = agent.get("id", "")
            if agent_id == "fusulishimin":
                agent["current_status"] = "行动中"
                agent["morale"] = max(30, min(100, agent.get("morale", 70) + 5))
                agent["loyalty_to_protagonist"] = 100
            elif agent_id == "meng_tian":
                agent["current_status"] = "行动中"
                agent["morale"] = max(30, min(100, agent.get("morale", 70) - 3))
            elif agent_id == "zhao_gao":
                agent["current_status"] = "行动中"
                agent["morale"] = max(30, min(100, agent.get("morale", 70) + 2))
            elif agent_id == "li_si":
                agent["current_status"] = "行动中"
                agent["morale"] = max(30, min(100, agent.get("morale", 70) - 5))
            elif agent_id == "wang_li":
                agent["current_status"] = "受监视"
                agent["loyalty_to_protagonist"] = max(0, agent.get("loyalty_to_protagonist", 40) - 10)


class SimulationRunner:
    """Orchestrates the full multi-round simulation until a terminal condition."""

    # Terminal conditions: a character dies (Zhao Gao, Li Shimin, or Xiongnu resolved)
    TERMINAL_EVENTS = [
        "赵高死亡", "赵高被杀", "赵高被处决",
        "扶苏死亡", "扶苏被杀", "李世民死亡",
        "匈奴全面入侵", "匈奴攻破上郡",
    ]

    def __init__(self, agents: List[Dict], world_state: WorldState,
                 round_definitions: List[Dict]):
        self.agents = agents
        self.world_state = world_state
        self.round_definitions = round_definitions
        self.results: List[Dict] = []
        self.terminal_reason = None
        self.era_conflict_log = []  # Track era conflict events

    def run_all(self) -> List[Dict]:
        """Run simulation rounds until terminal condition or max rounds."""
        max_rounds = 12  # Allow up to 12 rounds for full story
        i = 0

        while i < max_rounds:
            round_num = i + 1

            # If we have a round definition, use it; otherwise generate
            if i < len(self.round_definitions):
                round_def = self.round_definitions[i]
            else:
                round_def = self._generate_extended_round(round_num)

            sim_round = SimulationRound(round_num, round_def)
            result = sim_round.run(self.agents, self.world_state)

            # Add era conflict tracking
            self._track_era_conflicts(round_num, result)
            result["era_conflicts"] = self._get_current_era_conflicts()

            self.results.append(result)

            # Check for terminal conditions
            terminal = self._check_terminal(result)
            if terminal:
                self.terminal_reason = terminal
                result["terminal_event"] = terminal
                print(f"  ⚔️ 第{round_num}轮: {terminal} — 推演终结")
                break

            i += 1

        # Final outcome summary
        if not self.terminal_reason:
            self.terminal_reason = "推演达上限（12轮），未出现死亡结局"

        return self.results

    def _generate_extended_round(self, round_num: int) -> Dict:
        """Generate round definition for rounds beyond the initial 5."""
        extended_rounds = {
            6: {
                "title": "决裂边缘",
                "trigger": "胡亥在咸阳登基，扶苏成为'反贼'。扶苏必须在二十天内做出最终战略决策。",
                "key_conflicts": ["公开反叛 vs 继续合法斗争", "边军粮草只能支撑一个月", "蒙恬家族的安危"]
            },
            7: {
                "title": "第一滴血",
                "trigger": "赵高以皇帝名义发兵讨伐上郡。扶苏必须决定是否迎战。首战结果将决定所有人对局势的判断。",
                "key_conflicts": ["边军内战——秦军打秦军", "王离可能临阵倒戈", "蒙毅被公开处决的威胁"]
            },
            8: {
                "title": "王离之叛",
                "trigger": "王离在军营中策动兵变，试图绑架扶苏献给咸阳。蒙恬与王离的边军面临分裂。",
                "key_conflicts": ["兵变——王离 vs 蒙恬嫡系", "扶苏必须在混乱中展示军事指挥能力", "蒙恬必须在忠诚与家族之间做选择"]
            },
            9: {
                "title": "匈奴南下",
                "trigger": "匈奴单于头曼得知秦廷内乱，率十万骑兵南下掠夺。上郡边军面临腹背受敌。",
                "key_conflicts": ["外敌 vs 内乱——如何同时应对", "扶苏的军事才能 vs 赵高的政治阴谋", "匈奴可能加速或改变权力格局"]
            },
            10: {
                "title": "咸阳变局",
                "trigger": "李斯意识到赵高要除掉自己（赵高已开始清洗朝中异己），开始秘密联络扶苏。六国故地出现武装起义（比史实提前）。",
                "key_conflicts": ["李斯是否值得信任", "六国起义是机会还是威胁", "扶苏必须决定是否与李斯合作"]
            },
            11: {
                "title": "最终对峙",
                "trigger": "赵高派出的讨伐军与扶苏边军在对峙中。扶苏派出的密使联络到了山东六国贵族。多方势力开始摊牌。",
                "key_conflicts": ["三线作战——匈奴/赵高/六国", "扶苏的仁政宣言 vs 秦法传统", "赵高孤注一掷的阴谋"]
            },
            12: {
                "title": "宿命的终点",
                "trigger": "最终决战/决裂时刻。所有矛盾集中爆发。",
                "key_conflicts": ["生死决战", "历史岔路口的最后抉择", "角色的最终命运"]
            },
        }
        return extended_rounds.get(round_num, {
            "title": f"第{round_num}轮推演",
            "trigger": "局势继续发展",
            "key_conflicts": ["多方博弈继续"]
        })

    def _track_era_conflicts(self, round_num: int, result: Dict):
        """Track era-specific conflicts (Tang values vs Qin reality)."""
        era_conflicts = {
            1: "李世民本能地想用唐制解决危机——但秦朝没有科举、没有均田、没有三省六部，他只能硬着头皮用秦法",
            2: "李世民意识到自己最擅长的'用人术'在秦朝行不通——秦朝官员不是经科举选拔的读书人，而是文法吏",
            3: "李世民想减轻赋税争取民心——但边军粮草全靠咸阳调拨，减税等于断军粮",
            4: "唐制以均田制为基础，秦朝的土地制度完全不同——李世民发现自己实际上不知道如何在秦朝搞经济",
            5: "李世民开始理解秦制的逻辑——严刑峻法虽然残酷，但在统一初期确实有效维持了帝国稳定",
            6: "李世民的最大恐惧成真：他知道秦法不改革帝国必亡，但改革本身就会动摇他的权力基础",
            7: "李世民意识到自己和扶苏的不同——扶苏是真相信仁政，李世民是实用主义地选择仁政",
            8: "时代错位达到顶峰：李世民想用的府兵制、科举制、谏官制度，在秦朝全部不存在",
        }
        if round_num in era_conflicts:
            self.era_conflict_log.append({
                "round": round_num,
                "conflict": era_conflicts[round_num]
            })

    def _get_current_era_conflicts(self) -> list:
        """Get the current era conflict description."""
        return list(self.era_conflict_log)

    def _check_terminal(self, result: Dict) -> str:
        """Check if a terminal condition has been met."""
        events = result.get("events", [])
        actions = result.get("agent_actions", [])

        all_text = " ".join(events)
        for action in actions:
            all_text += " " + action.get("action", "")

        for terminal in self.TERMINAL_EVENTS:
            if terminal in all_text:
                return terminal

        # Check world state for critical conditions
        ws = self.world_state
        survival_risk = ws.get("protagonist_survival_risk", 100)
        border_stability = ws.get("border_army_stability", 75)
        xianyang_control = ws.get("xianyang_control", 50)
        six_states_risk = ws.get("six_states_restoration_risk", 50)

        if survival_risk >= 100:
            return "主角生存风险达到100%"
        if border_stability <= 10:
            return "边军完全崩溃，大规模哗变"
        if xianyang_control >= 100:
            return "赵高完全控制咸阳，扶苏失去合法性"
        if six_states_risk >= 95:
            return "六国全面起义，帝国分裂"

        return None

    def get_timeline(self) -> Dict[str, Any]:
        """Generate structured timeline from simulation results."""
        timeline = {
            "scenario": "李世民穿越为扶苏——沙丘之变",
            "divergence_point": "扶苏接到赐死诏时李世民意识觉醒（李世民知道秦朝将亡）",
            "historical_start": "秦始皇三十七年七月（公元前210年）",
            "terminal_reason": self.terminal_reason or "未终结",
            "total_rounds": len(self.results),
            "era_conflicts": list(self.era_conflict_log),
            "rounds": [],
        }

        for r in self.results:
            round_entry = {
                "round": r["round"],
                "title": r.get("title", f"第{r['round']}轮"),
                "events": r.get("events", []),
                "world_state_changes": r.get("world_state_update", {}),
                "risk_flags": r.get("risk_flags", []),
                "era_conflicts": r.get("era_conflicts", []),
            }
            if r.get("terminal_event"):
                round_entry["terminal_event"] = r["terminal_event"]
            timeline["rounds"].append(round_entry)

        timeline["final_world_state"] = self.world_state.snapshot()
        return timeline
