# 贡献指南

感谢你考虑为时煜源创科技项目贡献代码！🎉

## 快速开始

1. Fork 本仓库
2. 创建特性分支: `git checkout -b feat/your-feature`
3. 提交变更: `git commit -m 'feat: add your feature'`
4. 推送分支: `git push origin feat/your-feature`
5. 创建 Pull Request

## 提交规范

使用 [Conventional Commits](https://www.conventionalcommits.org/) 格式：

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### 类型
- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `style`: 代码格式（不影响功能）
- `refactor`: 重构
- `perf`: 性能优化
- `test`: 测试相关
- `chore`: 构建/工具/依赖更新
- `ci`: CI/CD 配置

### 示例
```
feat(auth): add OAuth2 login support

fix(api): handle null pointer in user lookup

docs(readme): update installation guide
```

## 分支策略

- `main`: 生产就绪，受保护分支
- `feat/*`: 新功能分支
- `fix/*`: Bug 修复分支
- `hotfix/*`: 紧急热修复

## 代码审查

所有变更必须通过 PR 并至少获得 **1 次审查通过** 才能合并到 main。

审查重点：
- 代码正确性与可读性
- 测试覆盖
- 文档同步
- 安全性考量

## 发布流程

1. 版本号遵循 [SemVer](https://semver.org/)
2. 通过 GitHub Release 发布
3. 变更日志自动生成（基于 Conventional Commits）

## 行为准则

- 友善、包容、尊重
- 建设性反馈
- 专注技术问题

---

> 时煜源创科技 · 飞书技术员团队
