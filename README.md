# GMP Pharma Warehouse — Claude Code Skill

面向药企仓库一线员工的 AI 合规助手。

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 这是什么？

一个 [Claude Code](https://www.anthropic.com/claude-code) Skill，内嵌了药品 GMP（2010 版）仓库管理合规知识。安装后，Claude 就变成了你的专属 GMP 仓库顾问——温湿度标准、批次追溯规则、不合格品处置流程，随问随答。

## 适用人群

药企仓库管理员、QA/QC 人员、生产部物料管理员。不用翻几百页的 GMP 原文，遇到问题直接问 AI。

## 安装

Claude Code 终端内执行：

```bash
npx skills add xiao-shi-feng/gmp-pharma-warehouse@gmp-pharma-warehouse
```

或者手动：

```bash
mkdir -p ~/.claude/skills/gmp-pharma-warehouse
cp SKILL.md ~/.claude/skills/gmp-pharma-warehouse/
```

## 能干什么

- 仓库温湿度标准查询（常温库/阴凉库/冷库各多少度）
- 五距要求（垛距、墙距、柱距、地面距、顶距）
- 物料验收四查
- 批次号管理与近效期预警规则
- 色标管理（绿/黄/红）
- 不合格品与退货处理流程
- 记录与台账规范（修改规则、保存期限）
- 验证与校准周期
- 特殊管理药品双人双锁要求

## 提问示例

> 阴凉库的温度范围是多少？

> 不合格品应该怎么处理？

> 近效期物料提前多久预警？

> 帮我生成一张温湿度记录表模板

> 退货品的处理流程是什么？

## 知识覆盖

- **2010 版《药品生产质量管理规范》**（GMP）正文
- **GMP 附录：计算机化系统、确认与验证**
- **《药品经营质量管理规范》**（GSP）仓储相关条款
- 面向仓库岗位做了精简提炼，删掉无关内容

## 许可证

MIT
