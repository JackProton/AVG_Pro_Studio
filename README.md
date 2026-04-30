# 🎮 AVG Pro Studio (AI 叙事工程工作站)

![Python Version](https://img.shields.io/badge/Python-3.11%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30%2B-FF4B4B)
![CrewAI](https://img.shields.io/badge/CrewAI-Powered-orange)

AVG Pro Studio 是一款工业级的**文字冒险游戏 (AVG / Galgame) 智能创作管线**。它将传统的“脑洞 -> 大纲 -> 剧本 -> 逻辑代码 -> 美术资产”开发流程，通过多 Agent (智能体) 协同工作流实现了全自动化。

无论是个人独立开发者还是小微游戏工作室，都可以利用这个工作站，将几句话的灵感，极速转化为结构严谨、可直接用于游戏引擎（如 Unity, Ren'Py, 唤境等）的底层资产。

---

## ✨ 核心特性 (Core Features)

*   🤖 **六引擎 Agent 工业流水线**：
    *   **策划总管**：根据脑洞生成全局世界观与动态章节目录。
    *   **剧情导演**：撰写带有分支选项和 `[系统：xxx]` 标签的严谨剧本。
    *   **逻辑转换员**：极速解析剧本，静默输出标准化的 JSON 逻辑节点树。
    *   **主美统筹 & 咒术师**：串行分析剧本，提取音画需求并输出工业级 AI 生图 Prompt。
    *   **QA 审核员**：交叉比对文本与底层代码，排查逻辑死锁。
*   ⚙️ **动态状态机与防死锁 UI**：专为 Streamlit 打造的安全原子锁回调，支持丝滑的跨章节自动跳转，彻底告别页面卡死。
*   🔒 **“访客安全隔离”架构**：完美支持云端公开部署。访客 API Key 仅存在于前端内存中，刷新即毁，绝不触碰服务器硬盘，保护资产安全。
*   💾 **无痕云端与本地全量备份**：一键将整个项目目录打成 `.zip` 压缩包下载到本地硬盘，对抗云服务器的“阅后即焚”。

---

## 🚀 快速开始 (Quick Start)

### 方案 A：本地私有化部署 (最安全，强烈推荐)

如果你希望拥有最高的数据隐私，且不想每次都在网页里手动输入 API Key，请选择在本地运行。

**1. 克隆项目与安装环境**
```bash
git clone [https://github.com/yourusername/AVG-Pro-Studio.git](https://github.com/yourusername/AVG-Pro-Studio.git)
cd AVG-Pro-Studio

# 创建并激活虚拟环境 (强烈推荐)
python -m venv venv

# Windows 激活: 
venv\Scripts\activate
# Mac/Linux 激活: 
source venv/bin/activate

# 安装依赖包
pip install -r requirements.txt
```

**2. 核心配置：创建 `config.json`**
在项目根目录（与 `app.py` 同级）新建一个名为 `config.json` 的文件。本系统已深度优化适配 **`deepseek-4`**，请按以下格式填入你的 API 配置：
```json
{
  "api_key": "sk-你的真实API密钥",
  "base_url": "[https://api.deepseek.com](https://api.deepseek.com)",
  "model": "deepseek-4"
}
```
*(注：项目已自带 `.gitignore`，该配置文件绝不会被意外推送到 GitHub，请放心填写。)*

**3. 运行工作站**
```bash
streamlit run app.py
```

### 方案 B：在云端一键部署 (适合作为 Demo 分享给他人)

1. Fork 或下载本仓库代码（**⚠️ 警告：传上 GitHub 前，请务必确保你的仓库里没有提交包含真实密钥的 `config.json` 文件！**）。
2. 登录 [Streamlit Community Cloud](https://share.streamlit.io/)，点击 `New app`。
3. 选择你的仓库、分支，并将 `Main file path` 设置为 `app.py`。
4. ⚠️ **关键步骤**：点击部署按钮下方的 `Advanced settings`，确保将 **Python version** 切换至 **3.11** 以上（否则会报依赖错误）。
5. 点击 `Deploy`。部署完成后，访客只需在网页左侧边栏展开“🔌 自定义 API”，输入其个人的 API Key 即可安全使用。

---

## 📁 目录结构 (Directory Structure)
```text
AVG-Pro-Studio/
│
├── app.py                  # Streamlit 前端主入口与状态机逻辑
├── requirements.txt        # 核心依赖清单
├── .gitignore              # Git 忽略配置（拦截私有项目与密钥）
│
└── src/
    └── my_avg_studio/
        ├── manager.py      # 项目文件 I/O 与配置读取
        ├── engine.py       # LLM 双擎调度与 Agent 任务编排
        └── config/
            ├── agents.yaml # 六大 Agent 的人设与核心提示词
            └── tasks.yaml  # 流水线任务指令与输出格式约束
```

---

## 🧠 技术栈 (Tech Stack)

*   **前端交互**：[Streamlit](https://streamlit.io/)
*   **多智能体框架**：[CrewAI](https://www.crewai.com/)
*   **大语言模型底层**：基于标准 OpenAI API 格式构建。**默认深度优化适配 `deepseek-4`**。

---

## 📝 最佳实践与避坑指南

1.  **关于算力分配**：在 `engine.py` 中，建议将需要极高逻辑推理和创造力的任务（如写大纲、写剧本）交接给满血版 `deepseek-4`；将纯机械式的格式化提取任务（如转化为 JSON 代码）交接给速度更快、成本更低的模型版本，可大幅提升整条管线的生成效率。
2.  **善用本地备份**：云端部署环境下，生成的所有文件均暂存于 Docker 容器的内存中。一旦关闭网页或应用休眠，数据将清空。请务必在收工前，点击侧边栏最下方的 **“📦 下载全套资产”** 将项目打成 Zip 包带走。
3.  **遵循系统标签**：如果你在右侧看板中手动修改了剧本，请确保关键的物品和数值变化带有 `[系统：获得道具 XX]` 这样的固定格式标签。这是逻辑 Agent 能够 100% 准确提取 JSON 节点树的核心锚点。

---

## 🤝 贡献与交流
欢迎提交 Pull Request 或 Issue！如果你对 AI 辅助游戏开发、叙事工程或 Agent 自动化管线感兴趣，欢迎一起探索更高效的独立游戏开发流。

---
*Built with ❤️ and AI.*
