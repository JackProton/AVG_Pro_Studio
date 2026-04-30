# 🎮 AVG Pro Studio (AI 叙事工程工作站)

![Python Version](https://img.shields.io/badge/Python-3.11%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30%2B-FF4B4B)
![CrewAI](https://img.shields.io/badge/CrewAI-Powered-orange)

AVG Pro Studio 是一款工业级的**文字冒险游戏 (AVG / Galgame) 智能创作管线**。它将传统的“脑洞 -> 大纲 -> 剧本 -> 逻辑代码 -> 美术资产”开发流程，通过多 Agent (智能体) 协同工作流实现了全自动化。

无论是个人独立开发者还是小微游戏工作室，都可以利用这个工作站，将几句话的灵感，极速转化为结构严谨、可直接用于游戏引擎（如 Unity, Ren'Py, 唤境等）的底层资产。

## ✨ 核心特性 (Core Features)

*   🤖 **六引擎 Agent 工业流水线**：
    *   **策划总管**：根据脑洞生成全局世界观与动态章节目录。
    *   **剧情导演**：撰写带有分支选项和 `[系统：xxx]` 标签的严谨剧本。
    *   **逻辑转换员**：极速解析剧本，静默输出标准化的 JSON 逻辑节点树。
    *   **主美统筹 & 咒术师**：串行分析剧本，提取音画需求并输出工业级 AI 生图 Prompt。
    *   **QA 审核员**：交叉比对文本与底层代码，排查逻辑死锁。
*   ⚙️ **动态状态机与防死锁 UI**：专为 Streamlit 打造的安全原子锁回调，支持丝滑的跨章节自动跳转，彻底告别页面卡死。
*   🔒 **“访客安全隔离”架构**：完美支持云端公开部署。API Key 仅存在于前端内存中，刷新即毁，绝不触碰服务器硬盘，保护开发者与访客的资产安全。
*   💾 **无痕云端与本地全量备份**：一键将整个项目目录打成 `.zip` 压缩包下载到本地硬盘，对抗云服务器的“阅后即焚”。

## 🚀 快速开始 (Quick Start)

### 方案 A：在云端一键部署 (Streamlit Community Cloud)

1. Fork 或下载本仓库代码。
2. 登录 [Streamlit Cloud](https://share.streamlit.io/)，点击 `New app`。
3. 选择你的仓库、分支，并将 `Main file path` 设置为 `app.py`。
4. ⚠️ **关键步骤**：点击部署按钮下方的 `Advanced settings`，确保将 **Python version** 切换至 **3.11**。
5. 点击 `Deploy`。部署完成后，在网页左侧边栏输入你的 API Key 即可安全使用！

### 方案 B：本地私有化部署 (推荐)

如果你希望拥有最高的数据隐私，可以直接在本地运行：
```bash
# 1. 克隆项目
git clone [https://github.com/yourusername/AVG-Pro-Studio.git](https://github.com/yourusername/AVG-Pro-Studio.git)
cd AVG-Pro-Studio

# 2. 创建并激活虚拟环境 (可选但强烈推荐)
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 3. 安装依赖包
pip install -r requirements.txt

# 4. 运行工作站
streamlit run app.py
