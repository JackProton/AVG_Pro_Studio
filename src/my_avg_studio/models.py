from pydantic import BaseModel, Field
from typing import List, Optional

class FlagChange(BaseModel):
    flag_name: str = Field(..., description="变量名")
    value: str = Field(..., description="变动值")
    reason: str = Field(..., description="变动原因")

class LogicScriptNode(BaseModel):
    node_id: str = Field(..., description="节点ID")
    content: str = Field(..., description="剧情文本")
    character: Optional[str] = Field(None, description="角色名")
    changes: List[FlagChange] = Field(..., description="逻辑变动")
    next_node_logic: str = Field(..., description="跳转逻辑")