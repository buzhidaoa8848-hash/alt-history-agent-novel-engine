"""
Chapter Writer

Generates novel chapter text from simulation results.
Uses narrative material generated in simulation rounds.
"""

from typing import Any, Dict, List, Optional

from src.llm_client import get_client


class ChapterWriter:
    """Writes novel chapters based on simulation output."""

    def __init__(self, timeline: Dict[str, Any], outline: str,
                 world_state: Dict[str, Any], agents: List[Dict]):
        self.timeline = timeline
        self.outline = outline
        self.world_state = world_state
        self.agents = agents
        self.llm = get_client()

    def write_chapter(self, chapter_num: int, title: str,
                      source_rounds: List[int], style_note: str = "") -> str:
        """Write a single chapter based on simulation data."""
        # Gather narrative material from relevant rounds
        narrative_material = self._gather_material(source_rounds)

        if self.llm.mode == "mock":
            return self._mock_chapter(chapter_num, title, narrative_material)
        else:
            return self._llm_chapter(chapter_num, title, narrative_material, style_note)

    def _gather_material(self, round_ids: List[int]) -> Dict:
        """Gather narrative material from specified rounds."""
        material = {
            "events": [],
            "narrative_snippets": [],
            "conflicts": [],
            "risk_flags": [],
        }
        for round_data in self.timeline.get("rounds", []):
            if round_data.get("round") in round_ids:
                material["events"].extend(round_data.get("events", []))
                material["narrative_snippets"].append(
                    round_data.get("narrative_material", "")
                )
                material["conflicts"].extend(round_data.get("conflicts", []))
                material["risk_flags"].extend(round_data.get("risk_flags", []))
        return material

    def _mock_chapter(self, chapter_num: int, title: str,
                      material: Dict) -> str:
        """Generate chapter with mock template (for MVP)."""
        return f"""# 第{chapter_num}章 {title}

{self._generate_opening(chapter_num)}

## 一

秦始皇三十七年，七月。上郡的夏天干燥而炎热。

风从塞外吹来，裹着沙土和马粪的气味。这不是一个适合死亡的季节，但死亡从来不会挑选季节。

扶苏跪在营帐中，面前的案上摆着一道诏书。墨迹已干，每一个字都像刀刻的一样清晰——事实上，它们确实是用刀刻在竹简上的。大秦的公文，从来都一丝不苟，哪怕是要取人性命的公文。

使者就站在帐外。他带来了皇帝的命令：赐死，立刻执行。

{self._generate_mid_chapter(chapter_num)}

## 二

蒙恬走进来时，扶苏——或者说，占据着扶苏身体的那个意识——正盯着自己的双手发呆。

这两只手白皙、修长，没有常年握剑的老茧。这是扶苏的手，一个读书人的手，一个从未亲手杀过人的公子的手。

但脑海中有一双手的记忆——那是一双握过弓箭、舞过长槊、在战场上斩将夺旗的手。那双手的主人叫李世民，是大唐的皇帝，是天策上将，是玄武门之变的胜利者。

"公子？"蒙恬的声音将他拉回现实。

扶苏抬起头。他看到了一个身披铁甲的将军，面容刚毅，眼神中满是忧虑。

"蒙将军，"他开口，声音沙哑，"诏书……你看了？"

"臣看了。"蒙恬的声音压得很低，"臣以为……此事蹊跷。"

{self._generate_closing(chapter_num)}

{self._generate_next_hint(chapter_num)}
"""

    def _generate_opening(self, chapter_num: int) -> str:
        """Generate chapter opening based on chapter number."""
        openings = {
            1: "这是关于一个不该死的人，在错误的时间，被错误的诏书赐死的故事。\n\n但历史的天平上，有时一个灵魂的重量就足以改变一切。",
            2: "蒙恬一生中做出过无数次判断。在战场上，他的判断从未失误。\n\n但在朝堂上，他第一次发现，判断对错的标准并不掌握在自己手中。",
        }
        return openings.get(chapter_num, "命运的齿轮开始转动……")

    def _generate_mid_chapter(self, chapter_num: int) -> str:
        """Generate middle section based on chapter number."""
        mids = {
            1: (
                "但事情并没有按照诏书的安排发展。\n\n"
                "因为在扶苏即将拿起那把剑的那一刻，他的身体里发生了某种变化。\n\n"
                "那不是来自外部的干涉，而是来自意识深处——像是一块巨石投入平静的湖面，"
                "涟漪从最深处向外扩散，搅动了原本平静的水面。\n\n"
                "一个不属于这个时代的意识，正在苏醒。"
            ),
            2: (
                "使者的催促声再次从帐外传来。\n\n"
                "扶苏站起身来。他的动作让蒙恬吃了一惊——不是那种犹豫不决的缓慢，"
                "而是一种出人意料的果断。\n\n"
                '「回禀使者，』扶苏说，声音平静得出奇，'
                '「就说本公子需要时间思考——父皇的恩情重于泰山，赐死之恩需以虔诚之心受之。」'
            ),
        }
        return mids.get(chapter_num, "")

    def _generate_closing(self, chapter_num: int) -> str:
        """Generate chapter closing."""
        closings = {
            1: "夜幕降临时，扶苏依然活着。\n\n使者没有得到回复。蒙恬没有离开。军营中弥漫着一种微妙的紧张——\n\n每个人都嗅到了不寻常的气息。\n\n而在扶苏的身体里，两个灵魂正在进行一场无声的对话。",
            2: "夜深了。上郡的军营中，仍有几盏孤灯未灭。\n\n蒙恬回到了自己的营帐，面前摊开着一幅地图。他的手指在地图上缓缓移动——从上郡到咸阳，沿途的关隘、城池、驻军，一一掠过。\n\n他知道，如果局势继续发展下去，迟早有一天，这幅地图上的每一条路，都可能染上鲜血。",
        }
        return closings.get(chapter_num, "")

    def _generate_next_hint(self, chapter_num: int) -> str:
        """Generate next chapter hint."""
        hints = {
            1: "\n\n---\n\n【待续】\n\n明日清晨，上郡的风将会带来新的变故。",
            2: "\n\n---\n\n【待续】\n\n一封来自咸阳的密信，正在路上。",
        }
        return hints.get(chapter_num, "\n\n---\n\n【待续】")

    def _llm_chapter(self, chapter_num: int, title: str,
                     material: Dict, style_note: str) -> str:
        """Generate chapter with real LLM."""
        prompt = f"""
Write a historical novel chapter based on the following simulation data:

Chapter {chapter_num}: {title}

Events to cover:
{chr(10).join(f'- {e}' for e in material.get('events', []))}

Narrative material:
{chr(10).join(material.get('narrative_snippets', []))}

Characters in scene: {chr(10).join(f'- {a.get("name")} ({a.get("identity","").split(chr(10))[0]})' for a in self.agents[:4])}

Style: Historical drama, political intrigue, military tension, restrained.
Maintain character authenticity. No anachronisms. No modern slang.
Write in Chinese literary style - classical but accessible.
Chapter should be 2000-3000 Chinese characters.
"""

        system = "You are a historical novelist specializing in Chinese alternate history. Your prose is vivid, restrained, and historically informed."
        return self.llm.generate(prompt, system)


def generate_first_chapter(timeline: Dict, outline: str,
                            world_state: Dict, agents: List[Dict]) -> str:
    """Convenience: generate Chapter 1 from simulation data."""
    writer = ChapterWriter(timeline, outline, world_state, agents)
    return writer.write_chapter(
        chapter_num=1,
        title="意识的裂缝",
        source_rounds=[1],
    )
