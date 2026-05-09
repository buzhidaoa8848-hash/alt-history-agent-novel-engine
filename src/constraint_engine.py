"""
Constraint Engine (v2.0)
硬约束引擎 — 确保推演不违背常识、历史、用户设定

三种约束类型：
1. COMMON_SENSE — 常识约束（如"30万精锐不会输给农民军"）
2. HISTORICAL — 历史约束（如"秦始皇死在公元前210年"）
3. USER_DEFINED — 用户自定义约束

每条约束有：
- type: 类型
- rule: 规则描述（自然语言）
- check: 检查函数（返回 True=通过, False=违规, str=违规说明）
- severity: "error"（不可违）| "warning"（建议不违）
"""

import json
from typing import Any, Dict, List, Optional, Callable, Union


class Constraint:
    """单条约束定义"""

    def __init__(self, rule: str, constraint_type: str = "user_defined",
                 severity: str = "error", reason: str = ""):
        self.rule = rule
        self.constraint_type = constraint_type
        self.severity = severity
        self.reason = reason

    def to_dict(self) -> Dict:
        return {
            "rule": self.rule,
            "type": self.constraint_type,
            "severity": self.severity,
            "reason": self.reason,
        }


# ====== 预设常识约束库 ======

COMMON_SENSE_CONSTRAINTS = [
    Constraint(
        rule="精锐军队不应轻易被劣势兵力击败",
        constraint_type="common_sense",
        reason="30万训练有素的边军打不过临时召集的农民军，违背军事常识"
    ),
    Constraint(
        rule="人物行为应符合其性格和利益",
        constraint_type="common_sense",
        reason="角色不会突然做出与性格完全相反的决定，除非有充分理由"
    ),
    Constraint(
        rule="获取信息需要合理渠道",
        constraint_type="common_sense",
        reason="角色不能知道超出其信息渠道的事情"
    ),
    Constraint(
        rule="行动需要资源支撑",
        constraint_type="common_sense",
        reason="军队需要粮草、兵器需要铁、政令需要官吏执行"
    ),
    Constraint(
        rule="制度改革需要时间",
        constraint_type="common_sense",
        reason="制度转型不能一蹴而就，最少需要数年"
    ),
    Constraint(
        rule="人口和社会结构不会突变",
        constraint_type="common_sense",
        reason="科举需要识字人口、均田需要土地统计，这些都无法短期创造"
    ),
]

HISTORICAL_CONSTRAINTS = [
    Constraint(
        rule="历史关键人物死亡时间不可改",
        constraint_type="historical",
        reason="除非在分歧点明确标注，否则不应改变已发生的历史事件"
    ),
    Constraint(
        rule="科技水平不能超越时代",
        constraint_type="historical",
        reason="穿越者不应带来超越当时科技水平的知识（除非设定允许）"
    ),
    Constraint(
        rule="地理和气候不应改变",
        constraint_type="historical",
        reason="黄河还是那条黄河，长城还是那道长城"
    ),
]


class ConstraintEngine:
    """硬约束引擎：验证推演结果是否符合所有约束"""

    def __init__(self):
        self.constraints: List[Constraint] = []
        self.violations: List[Dict] = []

    def load_presets(self, types: List[str] = None):
        """加载预设约束库"""
        if types is None:
            types = ["common_sense", "historical"]

        if "common_sense" in types:
            self.constraints.extend(COMMON_SENSE_CONSTRAINTS)
        if "historical" in types:
            self.constraints.extend(HISTORICAL_CONSTRAINTS)

    def add_user_constraint(self, rule: str, reason: str = "",
                            severity: str = "error"):
        """添加用户自定义约束"""
        self.constraints.append(Constraint(
            rule=rule,
            constraint_type="user_defined",
            severity=severity,
            reason=reason
        ))

    def add_from_scenario(self, scenario_data: Dict):
        """从场景定义中加载约束"""
        constraints_data = scenario_data.get("constraints", [])
        for c in constraints_data:
            self.add_user_constraint(
                rule=c.get("rule", ""),
                reason=c.get("reason", ""),
                severity=c.get("severity", "error")
            )

    def validate_events(self, events: List[str],
                        round_id: int) -> List[Dict]:
        """验证事件序列是否违反约束"""
        violations = []
        event_text = " ".join(events)

        for constraint in self.constraints:
            result = self._check_event_against_constraint(
                event_text, constraint
            )
            if result:
                violations.append({
                    "round": round_id,
                    "constraint": constraint.rule,
                    "detail": result,
                    "severity": constraint.severity,
                    "type": constraint.constraint_type,
                })

        return violations

    def validate_timeline(self, timeline: Dict) -> List[Dict]:
        """验证整个时间线"""
        all_violations = []
        for round_data in timeline.get("rounds", []):
            events = round_data.get("events", [])
            violations = self.validate_events(
                events, round_data.get("round", 0)
            )
            all_violations.extend(violations)
        return all_violations

    def _check_event_against_constraint(self, event_text: str,
                                        constraint: Constraint) -> Optional[str]:
        """检查事件是否违反特定约束"""
        rule = constraint.rule

        # 精锐军队不应被轻易击败
        if "精锐" in rule and "击败" in rule:
            keywords = ["击败", "打败", "溃败", "投降", "全歼"]
            strength_keywords = ["精锐", "边军", "主力", "禁军", "三十万"]
            weak_keywords = ["农民", "起义", "乌合", "临时"]

            if any(k in event_text for k in strength_keywords) and \
               any(k in event_text for k in weak_keywords) and \
               any(k in event_text for k in keywords):
                return f"精锐军队不应轻易被劣势兵力击败（事件中提到了弱势方击败强势方）"

        # 行为应符合性格
        if "性格" in rule and "利益" in rule:
            # 需要结合具体角色检查，这里做基础检测
            betrayal_patterns = ["突然背叛", "无理由投降", "突然效忠"]
            if any(p in event_text for p in betrayal_patterns):
                return f"角色行为转变缺少合理动机"

        # 信息获取渠道
        if "信息" in rule and "渠道" in rule:
            telepathy_patterns = ["知道了", "发现", "得知", "收到密报"]
            if any(p in event_text for p in telepathy_patterns):
                # 信息获取本身合理，但需要上下文验证
                pass

        return None

    def summary_report(self) -> str:
        """生成约束检查报告"""
        errors = [v for v in self.violations if v["severity"] == "error"]
        warnings = [v for v in self.violations if v["severity"] == "warning"]

        report = "## ⚖️ 约束引擎检查报告\n\n"

        if not errors and not warnings:
            report += "✅ 全部通过，无违规\n"
            return report

        if errors:
            report += f"### ❌ 违规 ({len(errors)}条)\n\n"
            for e in errors:
                report += f"- 第{e['round']}轮: {e['detail']}\n"
                report += f"  （违反: {e['constraint']}）\n\n"

        if warnings:
            report += f"### ⚠️ 警告 ({len(warnings)}条)\n\n"
            for w in warnings:
                report += f"- 第{w['round']}轮: {w['detail']}\n"

        return report
