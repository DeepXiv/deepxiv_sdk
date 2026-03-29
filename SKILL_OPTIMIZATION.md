# SKILL.md 优化分析与建议

## 📊 当前评估

### ✅ 优点
1. 清晰的模块化结构
2. 包含实际示例
3. 有多框架兼容性说明
4. 响应指导明确

### 🔴 需要改进的地方

#### 1. **目标用户不清晰**
- 当前写给"代理开发者"和"代理"混合
- 应该更明确地区分：
  - "这个 skill 如何使用"（给代理/框架）
  - "代理应该怎样行动"（给 AI 模型）

#### 2. **缺少决策树/选择指南**
- 用户想搜索论文，应该用哪个命令？
- 用户想读完整论文，应该怎么做？
- 没有"何时使用什么"的明确指导

#### 3. **命令用途说明不足**
- 列出了命令但没解释为什么要选择某个而非另一个
- 例如：`--brief` vs `--head` vs `--preview` 的区别不清楚

#### 4. **缺少边界情况处理**
- 论文未找到怎么办？
- 超过日限额怎么办？
- 没有错误处理的指导

#### 5. **输出格式选择不够明确**
- 何时用 `--format json`？
- 何时用纯文本？
- 没有清晰的决策标准

#### 6. **OA 文献路线图未体现**
- 目前只提 arXiv 和 PMC
- 应该提及 bioRxiv, medRxiv 等即将支持
- 缺少未来方向的提示

#### 7. **Token 管理策略不完整**
- 只说了自动注册
- 没有说明什么时候需要手动配置
- 没有提及检查 token 状态的方法

#### 8. **内容过度详细 vs 不够简洁**
- 对于某些高频操作（搜索、读论文）太简洁
- 对于低频操作（agent 配置）太详细

---

## 💡 优化建议

### A. 重构为"决策树"风格

**现在的问题**:
```
看看有什么命令...
好吧我就用第一个...
```

**优化后应该是**:
```
用户想做什么？
  - 搜索论文？→ deepxiv search
  - 读论文？→ deepxiv paper (选择格式)
  - 访问医学文献？→ deepxiv pmc
  - 智能分析？→ deepxiv agent
```

### B. 为每个命令添加"何时使用"和"预期输出"

**当前**:
```bash
deepxiv paper 2409.05591 --head
```

**优化**:
```bash
deepxiv paper 2409.05591 --head
# 何时使用: 当需要论文的完整结构和元数据时
# 包含: 标题、作者、摘要、所有章节列表及其摘要
# Token 成本: 低 (~1-2k tokens)
```

### C. 添加"常见任务工作流"

**新增章节**:
```markdown
## Common Workflows (常见工作流)

### 快速审视新论文
deepxiv paper <arxiv_id> --brief
# 快速了解论文内容，包括 TLDR、关键词、引用数

### 深入理解论文
deepxiv paper <arxiv_id> --head     # 了解结构
deepxiv paper <arxiv_id> --section "Introduction"  # 读导言
deepxiv paper <arxiv_id> --section "Methods"       # 读方法
```

### D. 添加错误处理和常见问题

**新增章节**:
```markdown
## Troubleshooting (故障排查)

### 论文未找到
deepxiv paper invalid_id
# → NotFoundError: Paper not found
# 解决: 检查 arXiv ID 格式 (应为 YYMM.NNNNN)

### 超过日限额
# → RateLimitError: Daily limit reached
# 解决: 等到明天，或联系 tommy@chien.io 申请更高限额
```

### E. 明确 Token 成本预期

**新增每个命令的 Token 成本**:
```markdown
### Search papers
deepxiv search "query" --limit 5
# Token cost: ~500-1000 tokens
# 返回: 标题、摘要、引用数、评分
```

### F. 添加"何时不用这个工具"

```markdown
## When NOT to use deepxiv

- 需要非开放获取论文 (需要订阅)
- 需要商业数据库内容
- 需要实时论文更新 (arXiv 有延迟)
```

### G. 重构 frontmatter

**现在**:
```yaml
---
name: deepxiv-cli
description: Use the deepxiv CLI to search...
---
```

**优化**:
```yaml
---
name: deepxiv-cli
description: Access academic papers (arXiv, PMC, bioRxiv, medRxiv) via CLI with smart search and content extraction
version: "0.2.0"
frameworks: ["codex", "langchain", "custom"]
use_cases: ["literature-review", "paper-analysis", "knowledge-synthesis"]
---
```

### H. 添加"推荐用法模式"部分

```markdown
## Recommended Patterns (推荐模式)

### 模式 1: 快速查找 (3 秒)
deepxiv search "topic" --limit 3 | 扫读摘要

### 模式 2: 深入阅读 (3 分钟)
deepxiv paper <id> --head           # 了解结构
deepxiv paper <id> --section Intro  # 读导言

### 模式 3: 智能分析 (5 分钟)
deepxiv agent query "分析这篇论文的关键贡献"
```

### I. 优化"Response Guidance"为"Output Format Guide"

**现在过于模糊**:
```markdown
- For search requests, report the most relevant papers...
```

**应该更具体**:
```markdown
## Output Format Guide

### For search results
- Format: "Title (arxiv_id, N citations) - Brief takeaway"
- Example: "MemGPT (2409.05591, 150 citations) - Extends LLM context with hierarchical memory"

### For paper reading
- Always mention which command was used: "摘要来自 `deepxiv paper <id> --brief`"
- Include token estimate: "(约 ~2k tokens)"
```

### J. 添加"能力和限制"清晰陈述

```markdown
## Capabilities (能力)
✅ 搜索超过 200 万篇 arXiv 论文
✅ 混合搜索 (BM25 + 向量)
✅ 分章节访问 (节省 tokens)
✅ 支持生物医学文献 (PMC, 即将: bioRxiv/medRxiv)
✅ AI 生成摘要和关键词

## Limitations (限制)
❌ 不支持付费期刊论文
❌ arXiv 更新延迟 ~1-2 天
❌ 日限额 10,000 请求 (免费用户)
❌ PMC 仅支持某些论文格式
```

---

## 📋 优化后的结构建议

```markdown
# DeepXiv CLI Skill

## 1. Quick Summary (30秒)
   - 是什么
   - 能做什么
   - 何时使用

## 2. Decision Tree (选择什么命令)
   用户想要 X → 使用命令 Y

## 3. Core Commands (有详细说明)
   - 命令
   - 何时使用
   - 示例
   - Token 成本
   - 预期输出格式

## 4. Common Workflows (常见工作流)
   - 快速浏览
   - 深入阅读
   - 批量分析
   - 智能查询

## 5. Capabilities & Limitations (能力和限制)
   - 能做什么
   - 不能做什么

## 6. Troubleshooting (故障排查)
   - 常见错误
   - 解决方案

## 7. Response Guidance (响应指南)
   - 输出格式
   - 何时用 JSON
   - 何时用纯文本

## 8. Advanced Usage (高级用法)
   - Token 管理
   - Agent 配置
   - 批量处理
```

---

## 🎯 优化优先级

| 优化 | 优先级 | 工作量 | 影响 |
|------|--------|--------|------|
| 添加决策树 | 🔴 高 | 中 | ⭐⭐⭐⭐⭐ |
| 每命令添加"何时使用" | 🔴 高 | 小 | ⭐⭐⭐⭐⭐ |
| 添加常见工作流 | 🟡 中 | 小 | ⭐⭐⭐⭐ |
| 添加故障排查 | 🟡 中 | 中 | ⭐⭐⭐⭐ |
| 优化 frontmatter | 🟡 中 | 小 | ⭐⭐⭐ |
| 添加能力/限制 | 🟡 中 | 小 | ⭐⭐⭐⭐ |
| 输出格式指南 | 🟢 低 | 小 | ⭐⭐⭐ |

---

## 📝 快速优化清单

- [ ] 在开头添加 30 秒快速总结
- [ ] 添加"选择命令决策树"
- [ ] 每个命令后添加"何时使用"和"Token 成本"
- [ ] 新增"常见工作流"部分
- [ ] 新增"能力和限制"部分
- [ ] 新增"故障排查"部分
- [ ] 优化"响应指南"为"输出格式指南"
- [ ] 更新 frontmatter 增加元数据

---

## ✨ 优化后的价值

1. **更易学习** - 决策树帮助理解
2. **更易使用** - 工作流提供现成方案
3. **更易扩展** - 清晰的能力/限制边界
4. **更易集成** - 更好的元数据和格式指南
5. **更专业** - 成为"一流的 skill 文档"

---

你想我现在就优化 SKILL.md 吗？还是先看看具体的改进版本？
