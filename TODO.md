# TODO: 下一步开发计划

## 🎯 近期目标（MVP 后）

### 1. 接入真实 LLM
- [ ] 实现 `src/llm_client.py` 的 `_real_generate` 方法
- [ ] 支持 OpenAI / DeepSeek / Anthropic 等多种API
- [ ] Agent卡增强：用LLM深化每个角色的心理动机和潜在冲突
- [ ] 推演文本生成：用LLM替代 mock 模板，生成更丰富的推演事件和叙事素材
- [ ] 章节正文生成：用LLM生成更高质量的历史小说章节

### 2. 接入 MiroFish 思想/架构
- [ ] 参考 mirofish-cli 的 `tools/` 管道架构，重构当前单模块
  - `GenerateOntologyTool` → 从场景文件生成历史事件本体
  - `BuildGraphTool` → 构建人物关系图谱
  - `PrepareSimulationTool` → 生成更精细的Agent Profile
  - `RunSimulationTool` → 接入OASIS或其他多Agent框架
  - `GenerateReportTool` → 生成推演报告和小说正文
- [ ] 研究 mirofish-cli 的 `app/core/workbench_session.py` 工作流调度模式
- [ ] 研究 mirofish-cli 的 `scripts/run_parallel_simulation.py` 并行推演

### 3. 增加更多场景
- [ ] 场景2：岳飞穿越为袁崇焕
- [ ] 场景3：王莽穿越回汉武帝时期
- [ ] 场景4：如果赤壁之战曹操赢了
- [ ] 场景5：王安石变法没有失败

### 4. 推演引擎增强
- [ ] 增加更多推演轮次（当前5轮→12轮，对应12章）
- [ ] 增加随机因子——每次运行可产生不同结果
- [ ] 增加Agent关系的动态变化（盟友变敌人、敌人变盟友）
- [ ] 增加意外事件卡片系统（天灾、密报、刺杀等随机事件）
- [ ] 增加历史惯性约束——某些历史趋势不可轻易改变

### 5. Web Demo
- [ ] 用 Streamlit 或 Gradio 做简单前端
- [ ] 可视化推演过程（人物关系图、状态变化曲线）
- [ ] 交互式Agent卡查看
- [ ] 时间线可视化

---

## 🚀 远期目标

### 6. MiroFish 深度集成
- [ ] 将当前项目作为 MiroFish 的一个 Skill 包（参考 `hermes-geopolitical-market-sim`）
- [ ] 接入 OASIS 多Agent社交模拟框架
- [ ] 引入 GraphRAG 增强历史知识检索
- [ ] 引入 Zep 长期记忆管理Agent状态

### 7. 小说质量提升
- [ ] 生成多章完整小说（12章）
- [ ] 多分支结局生成
- [ ] 角色对话增强
- [ ] 历史细节校验（自动查证）

### 8. 社区功能
- [ ] 场景分享/下载
- [ ] 推演结果对比
- [ ] 自定义Agent创建

---

## 技术债务

- [ ] 单元测试（当前仅手动验证）
- [ ] `simulation_runner.py` 中大量 mock 数据需要提取到单独的模板文件
- [ ] 异常处理——当前很多模块缺少完善的错误处理
- [ ] 日志系统——增加结构化日志记录
- [ ] 配置系统——支持 `.env` 配置LLM参数

---

## 提交历史

- v0.1.0 — MVP: 单场景、8个Agent、5轮推演、mock模式、7个输出文件
