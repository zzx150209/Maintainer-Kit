# Maintainer Kit

[English](README.md)

一个离线运行的开源项目维护检查工具。它检查常见文档和协作配置是否存在，列出文件依据，并支持在 CI 中只拦截新增缺项。

当前版本 **0.2.0，早期版本**。不需要 API Key，没有运行时第三方依赖，不上传仓库内容，也不执行被检查项目的代码。检查结果只反映文件是否存在且非空，不代表内容合格、安全或满足资助申请条件。

## 快速运行

需要 Python 3.10 及以上版本：

```sh
git clone https://github.com/zzx150209/Maintainer-Kit.git
cd Maintainer-Kit
python3 -m venv .venv
.venv/bin/python -m pip install .
.venv/bin/maintainer-kit examples/minimal --portable
```

Windows 使用 `.venv\Scripts\python` 和 `.venv\Scripts\maintainer-kit`。项目尚未发布到 PyPI；请从仓库安装，不要按同名软件包搜索安装。

## 常见用法

```sh
maintainer-kit /你的项目路径 --portable
maintainer-kit /你的项目路径 --portable --format json > baseline.json
maintainer-kit /你的项目路径 --baseline baseline.json
maintainer-kit /你的项目路径 --fail-on-missing
```

普通检查只输出结果；严格模式遇到缺项返回状态 1。基线模式只在出现新的缺项时返回状态 1，适合已有项目逐步接入。输入错误返回状态 2。严格模式和基线模式不能同时使用。

`--portable` 将报告里的本机绝对路径替换成 `.`，方便分享。报告仍含仓库相对文件名，发布前请检查。

## 检查范围

README、许可证、贡献指南、安全报告说明、行为准则、PR 模板、Issue 模板，以及 GitHub Actions / GitLab CI 文件。工具不会验证文件内容，不会判断许可证有效性，也不会扫描漏洞。

## 中文文档和自定义路径

在被检查项目根目录新建 `.maintainer-kit.json`：

```json
{
  "ignore": ["conduct"],
  "paths": {
    "readme": ["说明.md"],
    "ci": ["ci/pipeline.yml"]
  }
}
```

路径作为内置检查的补充。自定义文件必须位于项目内部，不接受绝对路径、`..` 或指向外部的链接。可重复传入 `--ignore 检查项`。完整检查项、退出状态、GitHub Action 接入方式和限制见英文文档。

## 开发与贡献

```sh
python3 -m pip install -e .
python3 -m unittest discover -s tests -v
```

欢迎提供最小复现案例、真实项目的使用反馈或提交修复。项目采用 MIT 许可证.
