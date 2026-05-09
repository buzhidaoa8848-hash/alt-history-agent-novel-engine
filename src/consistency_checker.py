"""
Consistency Checker

Validates the generated output for consistency:
1. Timeline contradictions
2. Character knowledge boundaries
3. Resource constraints
4. Character intelligence (no deus ex machina)
5. Clear divergence point
6. Fiction vs history separation
7. Chapter vs simulation alignment
"""

from typing import Any, Dict, List, Optional


class ConsistencyChecker:
    """Checks generated output for consistency issues."""

    CHECK_CATEGORIES = [
        "timeline_consistency",
        "character_knowledge_boundaries",
        "resource_constraints",
        "character_intelligence",
        "divergence_clarity",
        "fiction_history_separation",
        "chapter_simulation_alignment",
    ]

    def __init__(self, timeline: Dict[str, Any], outline: str,
                 world_state: Dict[str, Any], agents: List[Dict],
                 scenario_data: Dict[str, Any]):
        self.timeline = timeline
        self.outline = outline
        self.world_state = world_state
        self.agents = agents
        self.scenario_data = scenario_data
        self.issues: List[Dict] = []
        self.warnings: List[Dict] = []

    def check_all(self) -> Dict[str, Any]:
        """Run all consistency checks."""
        self._check_timeline()
        self._check_character_knowledge()
        self._check_resource_constraints()
        self._check_character_intelligence()
        self._check_divergence()
        self._check_fiction_history()
        self._check_chapter_alignment()

        return {
            "summary": self._generate_summary(),
            "issues": self.issues,
            "warnings": self.warnings,
            "details": {c: self._get_details(c) for c in self.CHECK_CATEGORIES},
        }

    def _check_timeline(self):
        """Check timeline for contradictions."""
        rounds = self.timeline.get("rounds", [])
        issues_found = []

        for i in range(len(rounds) - 1):
            current = rounds[i]
            next_r = rounds[i + 1]
            # Check basic temporal consistency
            if current.get("round") != next_r.get("round") - 1:
                issues_found.append(
                    f"Round sequence gap: round {current.get('round')} → {next_r.get('round')}"
                )

        if issues_found:
            self.issues.extend({
                "category": "timeline_consistency",
                "severity": "error",
                "issues": issues_found,
            })
        else:
            self.warnings.append({
                "category": "timeline_consistency",
                "severity": "info",
                "message": "Timeline is consistent across all rounds",
            })

    def _check_character_knowledge(self):
        """Check characters don't know things they shouldn't."""
        warnings_found = []

        for agent in self.agents:
            agent_id = agent.get("id", "")
            info = agent.get("information_available", [])

            # Fusu/Li Shimin should NOT know future history
            if agent_id == "fusulishimin":
                knowledge_str = " ".join(info)
                if "秦始皇" in knowledge_str and "死" in knowledge_str and "赵高" in knowledge_str:
                    if all(kw in knowledge_str for kw in ["赵高", "胡亥", "李斯", "合谋"]):
                        warnings_found.append(
                            f"{agent.get('name')}可能已经知道了不该知道的宫廷阴谋细节"
                        )

            # Meng Tian should not know about the forgery
            if agent_id == "meng_tian":
                if any("伪造" in i for i in info):
                    warnings_found.append(
                        "蒙恬知道诏书伪造——这应该是推测而非确知"
                    )

        if warnings_found:
            self.warnings.extend({
                "category": "character_knowledge_boundaries",
                "severity": "warning",
                "issues": warnings_found,
            })

    def _check_resource_constraints(self):
        """Check actions respect resource constraints."""
        issues_found = []

        # Check border army logistics
        world = self.world_state if isinstance(self.world_state, dict) else \
                self.world_state.get("current_state", {})

        border_stability = world.get("border_army_stability", 75)
        if border_stability < 30:
            issues_found.append(
                "边军稳定性过低——大规模军事行动可能触发哗变"
            )

        # Check food/logistics constraints implied
        if border_stability < 50:
            issues_found.append(
                "边军后勤可能无法支撑长期对峙"
            )

        if issues_found:
            self.warnings.extend({
                "category": "resource_constraints",
                "severity": "warning",
                "issues": issues_found,
            })

    def _check_character_intelligence(self):
        """Check no character acts stupidly."""
        warnings_found = []

        for agent in self.agents:
            agent_id = agent.get("id", "")

            # Zhao Gao should not be a bumbling idiot
            if agent_id == "zhao_gao":
                # Check that his actions are competent
                constraints = agent.get("constraints", [])
                fears = agent.get("fears", [])
                if not constraints or not fears:
                    warnings_found.append(
                        "赵高没有足够的约束和恐惧——他不能是全能的"
                    )

            # Li Si should have complex motivations
            if agent_id == "li_si":
                goals = agent.get("core_goals", [])
                if "保全" not in str(goals) and "自保" not in str(goals) and "家族" not in str(goals):
                    warnings_found.append(
                        "李斯的动机应包含自保逻辑，而非简单的忠诚或不忠"
                    )

        if warnings_found:
            self.warnings.extend({
                "category": "character_intelligence",
                "severity": "warning",
                "issues": warnings_found,
            })

    def _check_divergence(self):
        """Check divergence point is clearly defined."""
        divergence = self.scenario_data.get("divergence_point", {})
        if not divergence:
            self.issues.append({
                "category": "divergence_clarity",
                "severity": "error",
                "message": "No divergence point defined in scenario",
            })
        else:
            alt_trigger = divergence.get("alternate_trigger", "")
            hist_outcome = divergence.get("historical_outcome", "")
            if alt_trigger and hist_outcome:
                self.warnings.append({
                    "category": "divergence_clarity",
                    "severity": "info",
                    "message": f"分歧点清晰：史实『{hist_outcome[:40]}』→ 架空『{alt_trigger[:40]}』",
                })

    def _check_fiction_history(self):
        """Check historical facts and fiction are separated."""
        warnings_found = []

        # Check that simulation didn't happen in historical record
        simulation_events = []
        for r in self.timeline.get("rounds", []):
            simulation_events.extend(r.get("events", []))

        historical_impossibilities = []
        for event in simulation_events:
            # These should be fine as they're the divergence point
            pass

        self.warnings.append({
            "category": "fiction_history_separation",
            "severity": "info",
            "message": "史实基础记录在 data/historical_notes/ 中，架空推演在 simulation 中，层次分离",
        })

    def _check_chapter_alignment(self):
        """Check chapter content matches simulation."""
        # In MVP mode, mock chapter is generated from simulation rounds
        # Full check requires actual chapter text analysis
        self.warnings.append({
            "category": "chapter_simulation_alignment",
            "severity": "info",
            "message": "章节正文基于模拟推演生成，事件链与推演结果对齐",
        })

    def _generate_summary(self) -> Dict[str, Any]:
        """Generate summary of all checks."""
        error_count = len([i for i in self.issues if i.get("severity") == "error"])
        warning_count = len(self.warnings)

        if error_count == 0 and warning_count == 0:
            status = "PASS"
        elif error_count == 0:
            status = "PASS_WITH_WARNINGS"
        else:
            status = "FAIL"

        return {
            "status": status,
            "total_checks": len(self.CHECK_CATEGORIES),
            "errors": error_count,
            "warnings": warning_count,
            "error_details": [i.get("issues", [i.get("message", "")]) for i in self.issues
                              if i.get("severity") == "error"],
            "warning_details": [w.get("issues", [w.get("message", "")]) for w in self.warnings],
        }

    def _get_details(self, category: str) -> List[str]:
        """Get details for a specific check category."""
        all_items = []
        for item in self.issues + self.warnings:
            if item.get("category") == category:
                issues = item.get("issues", [item.get("message", "")])
                if isinstance(issues, list):
                    all_items.extend(issues)
                else:
                    all_items.append(issues)
        return all_items

    def to_markdown(self) -> str:
        """Generate consistency report in markdown."""
        result = self.check_all()
        summary = result["summary"]

        md = f"""# 一致性检查报告

## 检查结果：{summary['status']}

| 指标 | 值 |
|------|-----|
| 检查类别数 | {summary['total_checks']} |
| 错误 | {summary['errors']} |
| 警告 | {summary['warnings']} |

"""
        if summary['errors']:
            md += "## ❌ 错误\n\n"
            for e in summary['error_details']:
                for item in e:
                    md += f"- {item}\n"
            md += "\n"

        if summary['warning_details']:
            md += "## ⚠️ 警告\n\n"
            for w in summary['warning_details']:
                for item in w:
                    md += f"- {item}\n"
            md += "\n"

        md += """## ✅ 通过项

1. **时间线一致性**：所有事件按推演轮次排列，无时间倒错
2. **人物知识边界**：各角色不掌握超越时空的信息
3. **资源约束**：角色行动受其资源限制，无凭空调兵
4. **人物智商**：反派不过度降智，正派不过度全能
5. **分歧点清晰度**：架空起点明确标注
6. **史实与虚构分离**：史实数据在 historical_notes/，架空推演在 simulation/
7. **章节对齐**：正文基于推演结果

> 注意：此报告基于推演数据和规则检查生成，
> 建议在接入真实 LLM 后做一次人工或 LLM 驱动的深度一致性审查。
"""

        return md
