import os
import yaml
from crewai import Agent, Task, Crew, Process, LLM

class AvgEngine:
    def __init__(self, config_data):
        self.llm = LLM(
            model=config_data.get("model", "openai/gpt-4o"),
            base_url=config_data.get("base_url"),
            api_key=config_data.get("api_key")
        )
        self.agents_config = self._load_yaml('src/my_avg_studio/config/agents.yaml')
        self.tasks_config = self._load_yaml('src/my_avg_studio/config/tasks.yaml')

    def _load_yaml(self, path):
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def _create_agent(self, role_key):
        """工厂方法：创建指定角色的 Agent"""
        return Agent(config=self.agents_config[role_key], llm=self.llm)

    def _execute_single_task(self, task_config, agent, inputs, output_path=None):
        """执行单一任务，实现分步控制"""
        task = Task(
            config=task_config,
            agent=agent,
            output_file=output_path
        )
        crew = Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=True)
        return crew.kickoff(inputs=inputs)

    # ---------------------------------------------------------
    # 以下为分步调用的具体方法，支持按章节传入上下文
    # ---------------------------------------------------------

    def step_1_generate_outline(self, topic, output_dir):
        """第一步：生成大纲"""
        agent = self._create_agent('lead_designer')
        out_path = os.path.join(output_dir, "outline.md")
        result = self._execute_single_task(
            self.tasks_config['initial_planning_task'], 
            agent, 
            inputs={'game_topic': topic}, 
            output_path=out_path
        )
        return str(result), out_path

    def step_2_generate_script(self, chapter_num, outline_content, output_dir):
        """第二步：根据确认的大纲，按章节生成剧本"""
        agent = self._create_agent('story_director')
        out_path = os.path.join(output_dir, f"chapter_{chapter_num}_script.md")
        
        # 💡 这里是关键：将上一阶段的确认结果（或用户修改后的结果）作为这一阶段的输入
        inputs = {
            'chapter': chapter_num,
            'outline': outline_content,
            'game_topic': "基于设定大纲创作" # 简化提示词，避免重复
        }
        
        # 需要修改 tasks.yaml 里的 story_writing_task，让它接收 {chapter} 和 {outline}
        # 如果你不改 yaml，可以暂时把 inputs 拼接成一个长的 game_topic
        result = self._execute_single_task(
            self.tasks_config['story_writing_task'], 
            agent, 
            inputs=inputs, 
            output_path=out_path
        )
        return str(result), out_path

    def step_3_generate_logic(self, chapter_num, script_content, output_dir):
        """第三步：仅极速提取底层逻辑 JSON"""
        logic_agent = self._create_agent('logic_agent')
        logic_path = os.path.join(output_dir, f"chapter_{chapter_num}_logic.json")
        
        logic_inputs = {
            'chapter': chapter_num, 
            'script': script_content, 
            'game_topic': "逻辑提取"
        }
        
        logic_result = self._execute_single_task(
            self.tasks_config['logic_conversion_task'], 
            logic_agent, 
            inputs=logic_inputs, 
            output_path=logic_path
        )
        return str(logic_result), logic_path
    
    def step_4_generate_assets(self, chapter_num, script_content, output_dir):
        """第四步：资产统筹与生图咒术师的双擎联动"""
        asset_agent = self._create_agent('asset_manager')
        prompt_agent = self._create_agent('prompt_engineer') # 👈 召唤新 Agent
        
        out_path = os.path.join(output_dir, f"chapter_{chapter_num}_assets.md")
        
        # 任务 1：主美拆解需求
        task1 = Task(
            config=self.tasks_config['asset_planning_task'],
            agent=asset_agent
        )
        # 任务 2：咒术师写提示词（输出到最终文件）
        task2 = Task(
            config=self.tasks_config['prompt_generation_task'],
            agent=prompt_agent,
            output_file=out_path
        )
        
        # CrewAI 串行工作流：task2 会自动读取 task1 的结果作为上下文！
        crew = Crew(
            agents=[asset_agent, prompt_agent], 
            tasks=[task1, task2], 
            process=Process.sequential, 
            verbose=True
        )
        
        inputs = {
            'chapter': chapter_num,
            'script': script_content,
            'game_topic': "当前项目企划"
        }
        
        result = crew.kickoff(inputs=inputs)
        return str(result), out_path
        
    def step_5_run_qa(self, chapter_num, script_content, logic_json_content, output_dir):
        """第五步(选修)：专门的 QA 逻辑查杀"""
        checker_agent = self._create_agent('checker')
        report_path = os.path.join(output_dir, f"chapter_{chapter_num}_qa_report.md")
        
        qa_inputs = {
            'chapter': chapter_num,
            'script': script_content,
            'logic_json': logic_json_content  
        }
        
        qa_result = self._execute_single_task(
            self.tasks_config['final_check_task'], 
            checker_agent, 
            inputs=qa_inputs, 
            output_path=report_path
        )
        return str(qa_result), report_path