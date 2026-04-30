import streamlit as st
import os
import sys
import json
import re
import io         # 👈 新增：用于在内存中处理文件打包
import zipfile    # 👈 新增：用于生成压缩包下载

sys.path.append(os.path.abspath("src"))
from my_avg_studio.manager import ProjectManager
from my_avg_studio.engine import AvgEngine

st.set_page_config(page_title="AVG Pro Studio", page_icon="🎮", layout="wide")
pm = ProjectManager()

# --- 核心辅助函数：提取章节清单 ---
def parse_chapter_list(text):
    if not text: return ["默认章节"]
    clean_text = text.replace('*', '')
    match = re.search(r'【章节清单】[：:]?\s*([\s\S]+?)(?=\n\n|$)', clean_text)
    if match:
        raw_str = match.group(1).strip()
        chapters = [c.strip() for c in re.split(r'[,，、|\n]', raw_str) if c.strip()]
        chapters = [re.sub(r'^[-*]\s*', '', c) for c in chapters if c.strip()]
        if chapters:
            return chapters
    return ["默认章节"]

# 🔒 UI 锁定回调函数
def lock_ui():
    st.session_state.is_processing = True

# 🌟 特权跳转回调函数 (丝滑进入下一章，带安全解锁)
def next_chapter_callback():
    st.session_state.is_processing = True
    try:
        current_idx = st.session_state.chapter_list.index(st.session_state.active_chapter)
        next_idx = (current_idx + 1) % len(st.session_state.chapter_list)
        next_chap = st.session_state.chapter_list[next_idx]
        
        # 1. 强制同步底层状态和下拉菜单UI状态，防止打架！
        st.session_state.active_chapter = next_chap
        st.session_state.edit_chap = next_chap 
        
        # 2. 在回调的特权时间里，把下一章的数据直接读好
        proj = st.session_state.project_name
        st.session_state.script_content = pm.read_file(proj, f"chapter_{next_chap}_script.md")
        st.session_state.logic_content = pm.read_file(proj, f"chapter_{next_chap}_logic.json")
        st.session_state.qa_report = pm.read_file(proj, f"chapter_{next_chap}_qa_report.md")
        st.session_state.asset_content = pm.read_file(proj, f"chapter_{next_chap}_assets.md")
        
        # 3. 状态推断
        if st.session_state.qa_report or st.session_state.logic_content: 
            st.session_state.current_step = 3 
        elif st.session_state.script_content: 
            st.session_state.current_step = 2
        else: 
            st.session_state.current_step = 1 
            
    except ValueError:
        pass
    finally:
        # 4. 无论发生什么，回调结束时强制解锁！绝不留死锁。
        st.session_state.is_processing = False

# --- 初始化会话状态 (State Machine) ---
if 'current_step' not in st.session_state: st.session_state.current_step = 0  
if 'error_msg' not in st.session_state: st.session_state.error_msg = None
if 'project_name' not in st.session_state: st.session_state.project_name = "Project_Zero"
if 'active_chapter' not in st.session_state: st.session_state.active_chapter = "默认章节"
if 'is_processing' not in st.session_state: st.session_state.is_processing = False

if 'outline_content' not in st.session_state: st.session_state.outline_content = ""
if 'script_content' not in st.session_state: st.session_state.script_content = ""
if 'logic_content' not in st.session_state: st.session_state.logic_content = ""
if 'qa_report' not in st.session_state: st.session_state.qa_report = ""
if 'asset_content' not in st.session_state: st.session_state.asset_content = ""
if 'chapter_list' not in st.session_state: st.session_state.chapter_list = ["默认章节"]
if 'current_project_path' not in st.session_state: st.session_state.current_project_path = ""

if 'session_config' not in st.session_state: st.session_state.session_config = pm.load_config() 
if 'using_custom_api' not in st.session_state: st.session_state.using_custom_api = False

# --- 侧边栏：核心设置与存档管理 ---
with st.sidebar:
    st.header("⚙️ 引擎配置")
    if st.session_state.using_custom_api:
        st.success("🟢 访客自定义 API (已隔离)")
    else:
        st.info("🟢 系统默认 API")

    with st.expander("🔌 自定义 API (访客专用)", expanded=False):
        with st.form("custom_api_form"):
            custom_api_key = st.text_input("自定义 API Key", type="password")
            custom_base_url = st.text_input("自定义 Base URL")
            custom_model = st.text_input("自定义模型名")
            if st.form_submit_button("应用 / 恢复", use_container_width=True):
                if custom_api_key:
                    st.session_state.session_config = {
                        "api_key": custom_api_key,
                        "base_url": custom_base_url if custom_base_url else st.session_state.session_config.get("base_url", ""),
                        "model": custom_model if custom_model else st.session_state.session_config.get("model", "openai/gpt-4o")
                    }
                    st.session_state.using_custom_api = True
                    st.success("✅ 已生效")
                else:
                    st.session_state.session_config = pm.load_config()
                    st.session_state.using_custom_api = False
                    st.success("🔄 已恢复")
                st.rerun()
                
    st.divider()
    st.header("📁 企划与章节管理")
    
    project_list = pm.list_projects()
    if project_list:
        selected_project = st.selectbox("📂 打开历史项目", ["--请选择--"] + project_list)
        if selected_project != "--请选择--":
            if st.button("✅ 加载该项目", type="primary", use_container_width=True, disabled=st.session_state.is_processing):
                st.session_state.project_name = selected_project
                st.session_state.current_project_path = pm.get_project_path(selected_project)
                
                outline = pm.read_file(selected_project, "outline.md")
                st.session_state.outline_content = outline
                chapters = parse_chapter_list(outline)
                st.session_state.chapter_list = chapters
                
                first_chap = chapters[0] if chapters else "默认章节"
                st.session_state.active_chapter = first_chap
                
                proj = selected_project
                st.session_state.script_content = pm.read_file(proj, f"chapter_{first_chap}_script.md")
                st.session_state.logic_content = pm.read_file(proj, f"chapter_{first_chap}_logic.json")
                st.session_state.qa_report = pm.read_file(proj, f"chapter_{first_chap}_qa_report.md") 
                st.session_state.asset_content = pm.read_file(proj, f"chapter_{first_chap}_assets.md")
                
                if st.session_state.qa_report or st.session_state.logic_content: st.session_state.current_step = 3
                elif st.session_state.script_content: st.session_state.current_step = 2
                elif st.session_state.outline_content: st.session_state.current_step = 1
                else: st.session_state.current_step = 0
                st.rerun()
            
            with st.expander("🗑️ 删除该项目 (危险)"):
                if st.button("确认彻底删除", use_container_width=True, disabled=st.session_state.is_processing):
                    pm.delete_project(selected_project)
                    if st.session_state.project_name == selected_project:
                        st.session_state.current_step = 0
                        st.session_state.project_name = "Project_Zero"
                        st.session_state.outline_content = ""
                        st.session_state.script_content = ""
                        st.session_state.logic_content = ""
                        st.session_state.qa_report = ""
                        st.session_state.asset_content = ""
                        st.session_state.chapter_list = ["默认章节"]
                        st.session_state.active_chapter = "默认章节"
                    st.rerun()
                    
    st.divider()
    
    if st.session_state.current_step > 0:
        st.caption("📍 切换章节 (自动同步进度)：")
        selected_chap = st.selectbox("当前编辑章节", st.session_state.chapter_list, key="edit_chap", disabled=st.session_state.is_processing)
        
        # 监听下拉菜单，自动加载对应章节数据
        if selected_chap != st.session_state.active_chapter:
            st.session_state.active_chapter = selected_chap
            proj = st.session_state.project_name
            st.session_state.script_content = pm.read_file(proj, f"chapter_{selected_chap}_script.md")
            st.session_state.logic_content = pm.read_file(proj, f"chapter_{selected_chap}_logic.json")
            st.session_state.qa_report = pm.read_file(proj, f"chapter_{selected_chap}_qa_report.md")
            st.session_state.asset_content = pm.read_file(proj, f"chapter_{selected_chap}_assets.md")
            
            if st.session_state.qa_report or st.session_state.logic_content: st.session_state.current_step = 3 
            elif st.session_state.script_content: st.session_state.current_step = 2
            else: st.session_state.current_step = 1 
            st.rerun()

    if st.session_state.current_step > 0:
        with st.expander(f"🗑️ 废弃【{st.session_state.active_chapter}】"):
            if st.button("确认清空本章数据", use_container_width=True, disabled=st.session_state.is_processing):
                pm.delete_chapter(st.session_state.project_name, st.session_state.active_chapter)
                st.session_state.script_content = ""
                st.session_state.logic_content = ""
                st.session_state.qa_report = ""
                st.session_state.asset_content = ""
                st.session_state.current_step = 1
                st.rerun()

    st.divider()
    if st.button("➕ 新建空白企划", use_container_width=True, disabled=st.session_state.is_processing):
        st.session_state.current_step = 0
        st.session_state.project_name = "New_Project"
        st.session_state.outline_content = ""
        st.session_state.script_content = ""
        st.session_state.logic_content = ""
        st.session_state.qa_report = ""
        st.session_state.asset_content = ""
        st.session_state.chapter_list = ["默认章节"]
        st.session_state.active_chapter = "默认章节"
        st.rerun()

    # === 🌟 核心新增：侧边栏最下方的本地打包下载模块 ===
    st.divider()
    st.header("💾 本地防丢失备份")
    st.info("⚠️ 云端数据会在关闭网页后清空，请务必在收工前下载存档！")
    
    if st.session_state.project_name not in ["Project_Zero", "New_Project"]:
        proj_dir = pm.get_project_path(st.session_state.project_name)
        if os.path.exists(proj_dir) and os.listdir(proj_dir):
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                for root, _, files in os.walk(proj_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, start=proj_dir)
                        zip_file.write(file_path, arcname)
            zip_buffer.seek(0)
            st.download_button(
                label=f"📦 下载【{st.session_state.project_name}】全套资产",
                data=zip_buffer,
                file_name=f"{st.session_state.project_name}_backup.zip",
                mime="application/zip",
                use_container_width=True,
                type="primary"
            )
        else:
            st.caption("当前项目暂无生成的数据文件。")

# ==========================================
# 主界面头部：全局进度可视化
# ==========================================
st.title("🎮 AVG 叙事工程工作站")
st.caption(f"当前项目：**{st.session_state.project_name}** | 当前章节：**【{st.session_state.active_chapter}】**")

step_names = ["0. 企划脑洞", "1. 剧情大纲", "2. 剧本创作", "3. 资产看板"]
cols = st.columns(len(step_names))
for i, name in enumerate(step_names):
    with cols[i]:
        if st.session_state.current_step == i: st.markdown(f"**🔵 {name}** (当前)")
        elif st.session_state.current_step > i: st.markdown(f"<span style='color:#32CD32'>✅ {name}</span>", unsafe_allow_html=True)
        else: st.markdown(f"<span style='color:gray'>⚪ {name}</span>", unsafe_allow_html=True)
st.progress(st.session_state.current_step / (len(step_names) - 1))
st.divider()

# --- 🌟 核心新增：全局错误提示展示区 ---
if st.session_state.error_msg:
    st.error(st.session_state.error_msg)
    # 阅后即焚：显示完立刻清空。
    st.session_state.error_msg = None

cfg = st.session_state.session_config
engine = AvgEngine(cfg) if cfg.get("api_key") else None

# ==========================================
# 步骤 0：项目初始化
# ==========================================
if st.session_state.current_step == 0:
    st.subheader("💡 阶段 0：构思企划大纲")
    project_name_input = st.text_input("设置项目名称", st.session_state.project_name)
    topic = text = st.text_area("游戏核心脑洞", height=150, placeholder="描述你的故事背景、核心玩法和角色...")
    
    if st.button("🚀 召唤策划总管生成大纲", type="primary", on_click=lock_ui, disabled=st.session_state.is_processing):
        try:
            if not engine: 
                st.session_state.error_msg = "请先在左侧配置 API Key！"
            elif not topic: 
                st.session_state.error_msg = "请输入企划概念。"
            else:
                st.session_state.project_name = project_name_input
                p_path = pm.get_project_path(project_name_input)
                st.session_state.current_project_path = p_path
                with st.spinner("策划总管正在构思世界观与章节 (约 30 秒)..."):
                    result, _ = engine.step_1_generate_outline(topic, p_path)
                    st.session_state.outline_content = result
                    st.session_state.chapter_list = parse_chapter_list(result)
                    st.session_state.active_chapter = st.session_state.chapter_list[0] if st.session_state.chapter_list else "默认章节"
                    st.session_state.current_step = 1
        except Exception as e:
            # ✅ 把错误存进信使
            st.session_state.error_msg = f"引擎运行报错: {e}"
        finally:
            # ✅ 安全闭环：永远解锁，永远刷新
            st.session_state.is_processing = False
            st.rerun()

# ==========================================
# 步骤 1：大纲确认与编辑
# ==========================================
elif st.session_state.current_step == 1:
    st.subheader(f"📝 阶段 1：全局大纲确认（当前目标：{st.session_state.active_chapter}）")
    edited_outline = st.text_area("世界观与核心机制大纲 (支持修改)", value=st.session_state.outline_content, height=400)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button(f"✅ 确认大纲，撰写【{st.session_state.active_chapter}】剧本", type="primary", on_click=lock_ui, disabled=st.session_state.is_processing):
            try:
                st.session_state.outline_content = edited_outline
                st.session_state.chapter_list = parse_chapter_list(edited_outline)
                with st.spinner(f"剧情导演正在爆肝写【{st.session_state.active_chapter}】剧本 (约 1-2 分钟)..."):
                    result, _ = engine.step_2_generate_script(
                        st.session_state.active_chapter, st.session_state.outline_content, st.session_state.current_project_path
                    )
                    st.session_state.script_content = result
                    st.session_state.current_step = 2
            except Exception as e:
                # ✅ 把错误存进信使
                st.session_state.error_msg = f"引擎运行报错: {e}"
            finally:
                # ✅ 安全闭环
                st.session_state.is_processing = False
                st.rerun()
    with col2:
         if st.button("🔙 彻底重写大纲", disabled=st.session_state.is_processing):
             st.session_state.current_step = 0
             st.rerun()

# ==========================================
# 步骤 2：剧本确认与后台逻辑提取
# ==========================================
elif st.session_state.current_step == 2:
    st.subheader(f"🎬 阶段 2：【{st.session_state.active_chapter}】剧本深度编辑")
    st.info("💡 请核对分支和台词。确认后，系统将静默生成逻辑节点并执行防死锁扫描。")
    edited_script = st.text_area("剧本草稿 (支持修改)", value=st.session_state.script_content, height=500)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ 确认剧本并提取底层逻辑", type="primary", on_click=lock_ui, disabled=st.session_state.is_processing):
            try:
                st.session_state.script_content = edited_script
                with st.spinner("后台正在极速生成底层逻辑节点 (约 20-30 秒)..."):
                    result, _ = engine.step_3_generate_logic(
                        st.session_state.active_chapter, st.session_state.script_content, st.session_state.current_project_path
                    )
                    st.session_state.logic_content = result
                    st.session_state.current_step = 3
            except Exception as e:
                # ✅ 把错误存进信使
                st.session_state.error_msg = f"引擎运行报错: {e}"
            finally:
                # ✅ 安全闭环
                st.session_state.is_processing = False
                st.rerun()
    with col2:
         if st.button("🔙 返回修改大纲", disabled=st.session_state.is_processing):
             st.session_state.current_step = 1
             st.rerun()

# ==========================================
# 步骤 3：全流程成果看板
# ==========================================
elif st.session_state.current_step == 3:
    st.subheader(f"🎉 【{st.session_state.active_chapter}】完工看板")
    st.success(f"✅ 资产已归档至 `projects/{st.session_state.project_name}`。")
    
    tab_outline, tab_script, tab_qa, tab_assets, tab_logic = st.tabs([
        "🌍 世界观大纲", "📜 本章剧本", "🕵️ QA 质量报告", "🎨 音画素材单", "⚙️ JSON 节点树"
    ])
    
    with tab_outline:
        with st.container(border=True, height=500): st.markdown(st.session_state.outline_content)
    with tab_script:
        with st.container(border=True, height=500): st.markdown(st.session_state.script_content)
    with tab_qa:
        with st.container(border=True, height=500):
            if st.session_state.qa_report: 
                st.markdown(st.session_state.qa_report)
            else:
                st.info("💡 尚未进行本章的逻辑查杀。如果剧本带有复杂分支，建议运行查杀。")
                if st.button("🕵️ 召唤 QA 审核员查杀逻辑死锁", type="primary", on_click=lock_ui, disabled=st.session_state.is_processing):
                    try:
                        with st.spinner("QA 正在交叉比对剧本与代码 (约 30 秒)..."):
                            result, _ = engine.step_5_run_qa(
                                st.session_state.active_chapter, 
                                st.session_state.script_content, 
                                st.session_state.logic_content, 
                                st.session_state.current_project_path
                            )
                            st.session_state.qa_report = result
                    except Exception as e:
                        st.session_state.error_msg = f"引擎运行报错: {e}"
                    finally:
                        st.session_state.is_processing = False
                        st.rerun()
    with tab_assets:
        with st.container(border=True, height=500):
            if st.session_state.asset_content: st.markdown(st.session_state.asset_content)
            else:
                st.info("💡 本章尚未拆解多媒体资源。")
                if st.button("🎵 一键生成音画素材需求表", type="primary", on_click=lock_ui, disabled=st.session_state.is_processing):
                    try:
                        with st.spinner("音画统筹 Agent 正在发力 (约 1-2 分钟)..."):
                            result, _ = engine.step_4_generate_assets(
                                st.session_state.active_chapter, st.session_state.script_content, st.session_state.current_project_path
                            )
                            st.session_state.asset_content = result
                    except Exception as e:
                        st.session_state.error_msg = f"引擎运行报错: {e}"
                    finally:
                        st.session_state.is_processing = False
                        st.rerun()
    with tab_logic:
        with st.container(border=True, height=500):
            if st.session_state.logic_content:
                raw_json = st.session_state.logic_content
                if raw_json.startswith("```json"): raw_json = raw_json[7:-3].strip()
                elif raw_json.startswith("```"): raw_json = raw_json[3:-3].strip()
                try: st.json(json.loads(raw_json)) 
                except: st.code(st.session_state.logic_content, language="json")
            else: st.info("未找到底层逻辑代码。")

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.button("⏭️ 归档本章，并自动开始创作下一章", type="primary", use_container_width=True, on_click=next_chapter_callback, disabled=st.session_state.is_processing)
    with col2:
        if st.button("🔙 发现不足？退回重修本章剧本", use_container_width=True, disabled=st.session_state.is_processing):
            st.session_state.current_step = 2
            st.rerun()