# Demo-Code

本项目使用 `uv` 进行现代化的 Python 包管理和环境管理。

## 🚀 快速上手 (Quick Start)

只需两步即可配置好开发环境并运行代码。

### 1. 同步环境
自动安装 Python 3.12 及所有项目依赖：
```bash
uv sync
```

### 2. 运行代码
直接运行脚本，无需手动激活虚拟环境：
```bash
uv run <你的脚本文件.py>
```

---

## 📖 详细文档 (Detailed Documentation)

以下是 `uv` 的常用命令详解，涵盖了从项目初始化到依赖管理的完整流程。

### 📦 依赖管理

#### 添加依赖
安装新的 Python 包，并自动更新 `pyproject.toml` 和 `uv.lock`：
```bash
uv add <package_name>
```
示例：
```bash
uv add requests      # 添加 requests
uv add openai        # 添加 openai
uv add "flask>=3.0"  # 添加指定版本的 flask
```

#### 开发依赖
添加仅在开发环境中需要的包（如测试工具）：
```bash
uv add --dev pytest
```

#### 移除依赖
移除不再需要的包：
```bash
uv remove <package_name>
```

#### 查看依赖树
查看当前项目的依赖关系树，排查版本冲突：
```bash
uv tree
```

### 🛠️ 环境管理

#### 锁定 Python 版本
指定项目使用的 Python 版本（例如锁定为 3.12）：
```bash
uv python pin 3.12
```

#### 导出依赖
如果需要生成标准的 `requirements.txt` 文件（例如用于部署）：
```bash
uv export --format requirements-txt > requirements.txt
```

#### 清理环境
清理缓存和未使用的环境：
```bash
uv cache clean
```

### ⚡ 高级用法

#### 运行任意命令
在虚拟环境上下文中运行任意命令（如 pip）：
```bash
uv run pip list
uv run pytest
```

#### 兼容性模式
如果你习惯使用 `pip`，也可以在激活虚拟环境后使用标准 pip 命令：
- **Windows**: `.venv\Scripts\activate`
- **Mac/Linux**: `source .venv/bin/activate`

激活后：
```bash
pip install -r requirements.txt
```

更多详细信息请参考 [uv 官方文档](https://docs.astral.sh/uv/)。
