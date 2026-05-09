"""
Scenario Builder (v2.0)
场景构建器 — 用户通过交互式CLI创建自定义场景

支持场景类型：
- history: 历史架空（给历史加if线）
- reality: 现实推演（如果某件事没发生）
- fiction: 小说二创（给已有作品做同人if线）
- free: 自由创作（完全架空世界）
"""

import json
import os
from typing import Any, Dict, List, Optional
from datetime import datetime


# ====== 场景预设库 ======

PRESET_SCENARIOS = {
    "qin_fusu": {
        "id": "qin_fusu_lishimin_v2",
        "title": "李世民穿越为扶苏（经典版）",
        "type": "history",
        "era": "秦朝",
        "year": "秦始皇三十七年（公元前210年）",
        "description": "沙丘之变后，赵高李斯伪造赐死诏。李世民在扶苏身上醒来。",
        "default_protagonist": "李世民（唐太宗）",
        "divergence_point": "扶苏接到赐死诏时李世民意识觉醒",
        "constraints": [
            {"rule": "30万边军是精锐，不会轻易被击败", "reason": "军事常识", "severity": "error"},
            {"rule": "李世民拥有军事天才，正面战场不应失败", "reason": "主角设定", "severity": "error"},
            {"rule": "制度改革需要时间，不可能一蹴而就", "reason": "历史常识", "severity": "error"},
        ],
    },
    "three_kingdoms": {
        "id": "three_kingdoms_if",
        "title": "如果郭嘉没死——官渡之战后",
        "type": "history",
        "era": "三国",
        "year": "建安十二年（公元207年）",
        "description": "郭嘉在北征乌桓途中未病逝，曹操统一北方的进程改变。",
        "default_protagonist": "郭嘉",
        "divergence_point": "郭嘉没有病逝，继续为曹操谋划",
        "constraints": [
            {"rule": "郭嘉是顶级谋士，不应被轻易击败", "reason": "人物设定", "severity": "error"},
            {"rule": "曹操在赤壁之战时期的决策会因郭嘉存在而不同", "reason": "历史逻辑", "severity": "warning"},
        ],
    },
    "modern_startup": {
        "id": "modern_startup_war",
        "title": "如果字节跳动没有张一鸣",
        "type": "reality",
        "era": "现代（2012年）",
        "year": "2012年",
        "description": "张一鸣在创办字节跳动前夕意外退出，另一批人接手。",
        "default_protagonist": "字节跳动新CEO",
        "divergence_point": "张一鸣退出，字节跳动由职业经理人管理",
        "constraints": [
            {"rule": "商业竞争遵循市场规律", "reason": "经济常识", "severity": "error"},
            {"rule": "产品成功需要匹配市场需求，不依赖个人英雄主义", "reason": "商业逻辑", "severity": "warning"},
        ],
    },
}


class ScenarioBuilder:
    """交互式场景构建器"""

    def __init__(self):
        self.scenario = {}
        self.agents = []
        self.constraints = []

    def interactive_create(self) -> Dict[str, Any]:
        """交互式创建场景（CLI提示）"""
        print("\n" + "=" * 60)
        print("  🏗️  场景构建器 v2.0")
        print("=" * 60)

        # Step 1: Choose type or preset
        self._step_choose_type()

        # Step 2: Basic info
        self._step_basic_info()

        # Step 3: Protagonist
        self._step_protagonist()

        # Step 4: Divergence
        self._step_divergence()

        # Step 5: Characters
        self._step_characters()

        # Step 6: Constraints
        self._step_constraints()

        # Step 7: Summary
        self._show_summary()

        return self._build_scenario_data()

    def _step_choose_type(self):
        """Step 1: 选择场景类型或预设"""
        print("\n📌 选择场景来源：")
        print("  1) 历史架空（给历史加if线）")
        print("  2) 现实推演（如果某件事没发生）")
        print("  3) 小说二创（给已有作品做同人）")
        print("  4) 自由创作（完全架空世界）")
        print("  5) 使用预设场景")
        print()

        # For non-interactive mode, use presets or history as default
        self.scenario["type"] = "history"

    def _step_basic_info(self):
        """Step 2: 基本信息"""
        self.scenario["title"] = "用户自定义场景"
        self.scenario["era"] = ""
        self.scenario["year"] = ""
        self.scenario["description"] = ""

    def _step_protagonist(self):
        """Step 3: 主角设置"""
        # Key rule: user defines protagonist, AI doesn't make things up
        self.scenario["protagonist_name"] = ""
        self.scenario["protagonist_identity"] = ""
        self.scenario["protagonist_info"] = ""

    def _step_divergence(self):
        """Step 4: 分歧点"""
        self.scenario["divergence_point"] = ""
        self.scenario["historical_outcome"] = ""

    def _step_characters(self):
        """Step 5: 自定义角色"""
        # User adds characters manually
        self.agents = []

    def _step_constraints(self):
        """Step 6: 硬约束"""
        self.constraints = []

    def _show_summary(self):
        """Step 7: 显示摘要"""
        print("\n" + "=" * 60)
        print("  📋 场景构建完成")
        print("=" * 60)

    def _build_scenario_data(self) -> Dict[str, Any]:
        """构建完整的场景数据"""
        return {
            "scenario": {
                "id": f"custom_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "title": self.scenario.get("title", "自定义场景"),
                "type": self.scenario.get("type", "history"),
                "era": self.scenario.get("era", ""),
                "year": self.scenario.get("year", ""),
                "description": self.scenario.get("description", ""),
                "divergence_point": {
                    "event": self.scenario.get("divergence_point", ""),
                    "alternate_trigger": self.scenario.get("alternate_trigger", ""),
                    "protagonist_info": self.scenario.get("protagonist_info", ""),
                },
                "setting": {
                    "era": self.scenario.get("era", ""),
                    "year": self.scenario.get("year", ""),
                    "location": self.scenario.get("location", ""),
                    "political_situation": self.scenario.get("political_situation", ""),
                },
                "agents": self.agents,
                "simulation_rounds": self._default_rounds(),
                "constraints": self.constraints,
                "output": {
                    "base_dir": f"outputs/custom_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                },
            }
        }

    def _default_rounds(self) -> List[Dict]:
        """生成默认推演轮次"""
        return [
            {"round": 1, "title": "分歧点触发", "trigger": "分歧事件发生，主角做出不同选择", "key_conflicts": ["主角vs旧有秩序"]},
            {"round": 2, "title": "连锁反应", "trigger": "主角的选择引发各方反应", "key_conflicts": ["各方势力开始博弈"]},
            {"round": 3, "title": "局势明朗", "trigger": "各方力量对比逐渐清晰", "key_conflicts": ["盟友vs敌人的界限确定"]},
            {"round": 4, "title": "第一次危机", "trigger": "首次重大冲突爆发", "key_conflicts": ["主角面临第一次重大考验"]},
            {"round": 5, "title": "反制与博弈", "trigger": "对手开始反制", "key_conflicts": ["信息战/舆论战/正面冲突"]},
        ]

    def load_preset(self, preset_id: str) -> Dict[str, Any]:
        """加载预设场景"""
        preset = PRESET_SCENARIOS.get(preset_id)
        if not preset:
            raise ValueError(f"未知预设场景: {preset_id}")

        # Convert preset to full scenario format
        return {
            "scenario": {
                "id": preset["id"],
                "title": preset["title"],
                "type": preset["type"],
                "era": preset["era"],
                "year": preset["year"],
                "description": preset["description"],
                "divergence_point": {
                    "event": preset.get("divergence_point", ""),
                    "alternate_trigger": f"{preset.get('default_protagonist', '')}做出不同选择",
                    "protagonist_info": f"主角是{preset.get('default_protagonist', '未知')}",
                },
                "setting": {
                    "era": preset["era"],
                    "year": preset["year"],
                    "location": "",
                    "political_situation": preset.get("description", ""),
                },
                "agents": self._preset_agents(preset_id),
                "simulation_rounds": self._default_rounds(),
                "constraints": preset.get("constraints", []),
                "output": {
                    "base_dir": f"outputs/{preset_id}_run_001",
                },
            }
        }

    def _preset_agents(self, preset_id: str) -> List[Dict]:
        """为预设场景生成默认Agent"""
        # For now return minimal agents - user can expand
        if preset_id == "qin_fusu":
            return [
                {"id": "protagonist", "name": "李世民/扶苏", "identity": "主角", "core_goals": ["活下去", "改变命运"], "resources": ["军队", "智慧"], "fears": ["失败", "历史重演"], "personality": "果断", "information_available": ["知道历史走向"], "constraints": ["不能暴露穿越"], "likely_actions": ["整合力量", "改革"], "relationship_to_protagonist": "自身"},
                {"id": "ally", "name": "蒙恬", "identity": "秦大将", "core_goals": ["保扶苏", "忠君"], "resources": ["三十万边军"], "fears": ["家族被灭"], "personality": "忠勇", "information_available": ["怀疑诏书有假"], "constraints": ["不能公开反叛"], "likely_actions": ["支持扶苏", "观望"], "relationship_to_protagonist": "盟友"},
                {"id": "enemy", "name": "赵高", "identity": "中车府令", "core_goals": ["扶胡亥", "杀扶苏"], "resources": ["玺印", "宫廷"], "fears": ["扶苏不死"], "personality": "阴险", "information_available": ["知道诏书是假的"], "constraints": ["必须依靠李斯"], "likely_actions": ["加速夺权", "派兵镇压"], "relationship_to_protagonist": "死敌"},
            ]
        return []

    def create_from_params(self, params: Dict) -> Dict[str, Any]:
        """从参数字典直接创建（非交互模式）"""
        scenario_type = params.get("type", "history")

        # Build scenario data
        scenario_data = {
            "scenario": {
                "id": f"custom_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "title": params.get("title", "自定义场景"),
                "type": scenario_type,
                "era": params.get("era", ""),
                "year": params.get("year", ""),
                "description": params.get("description", ""),
                "divergence_point": {
                    "event": params.get("divergence", ""),
                    "alternate_trigger": params.get("trigger", ""),
                    "protagonist_info": params.get("protagonist_info", ""),
                },
                "setting": {
                    "era": params.get("era", ""),
                    "year": params.get("year", ""),
                    "location": params.get("location", ""),
                    "political_situation": params.get("background", ""),
                },
                "agents": params.get("agents", []),
                "simulation_rounds": self._default_rounds(),
                "constraints": params.get("constraints", []),
                "output": {
                    "base_dir": f"outputs/custom_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                },
            }
        }
        return scenario_data
