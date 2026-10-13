# GitHub 中文软件雷达 / GitHub Software Radar

零新增费用的开源软件发现工具，用于发现 AI、开发工具、企业管理和平台基础设施项目。

## V1

- GitHub Search API 公开项目采集：近期代码更新的 AI Agent、开发工具、CRM、认证项目。
- 去重，记录官方链接、原始简介、Star、更新日期、许可证标识。
- 自动生成 `reports/latest.md` 与 `reports/latest.json`。
- GitHub Actions 每周二 06:00 UTC（赞比亚约 08:00）运行，或在 Actions 页面手动运行。

**边界：** V1 是候选项目清单，并非 AI 中文翻译或通过验证的软件评测；简介可能为英文。中文价值判断由 ChatGPT 定期简报进行。Star 不代表质量、安全或商业许可。项目未实际安装测试。

## 启用方法

1. 将开发分支的 PR 合并到 main。
2. 打开 Settings → Actions → General，确认允许 GitHub Actions。若推送报告失败，检查 Workflow permissions 是否允许 Read and write permissions。
3. 打开 Actions → Weekly Software Radar → Run workflow。
4. 成功后到 `reports/latest.md` 查看采集候选。

所有采集仅请求公开 GitHub 元数据，不执行第三方项目代码，也不需要额外 AI API、服务器、私人 Token 或数据库。GitHub 的限制和免费配额可能变化。

## 下一步

验证首次执行，再优化发现近期新项目的排序、中文解读流程与可搜索历史目录。