# 配置说明

本文档介绍 TaskManager 的配置选项和自定义设置。

## 存储配置

### JSON 存储后端

默认使用 JSON 文件作为持久化存储，文件路径为当前目录下的 `tasks.json`。

```python
from task_manager.json_store import JsonStore

# 使用默认路径
store = JsonStore()  # tasks.json

# 使用自定义路径
store = JsonStore("/path/to/my/tasks.json")
```

### 内存存储后端

用于测试或临时使用，数据不会持久化：

```python
from task_manager.storage import MemoryStore

store = MemoryStore()
```

## CLI 配置

### 命令别名

可以为常用命令设置别名：

```bash
# 在 .bashrc 或 .zshrc 中添加
alias taskm="python -m task_manager.cli"
alias tls="taskm list"
alias tadd="taskm add"
alias tdone="taskm done"
```

### 默认优先级

默认优先级为 `medium`，可以在代码中修改：

```python
# task_manager/cli.py
p_add.add_argument(
    "-p", "--priority", 
    default="high",  # 修改默认值
    choices=["low", "medium", "high", "critical"]
)
```

## 数据格式

### JSON 存储格式

任务数据以 JSON 数组形式存储：

```json
[
  {
    "task_id": "a1b2c3d4",
    "title": "完成项目文档",
    "description": "撰写用户手册和API文档",
    "status": "todo",
    "priority": 2,
    "assignee": "张三",
    "tags": ["文档", "重要"],
    "subtasks": [
      {
        "subtask_id": "st01",
        "title": "用户手册",
        "done": false
      }
    ],
    "due_date": "2026-03-15T18:00:00",
    "created_at": "2026-03-06T14:32:54",
    "updated_at": "2026-03-06T14:32:54"
  }
]
```

### 优先级映射

- `LOW = 1`
- `MEDIUM = 2` 
- `HIGH = 3`
- `CRITICAL = 4`

### 状态值

- `"todo"` - 待办
- `"in_progress"` - 进行中
- `"done"` - 已完成
- `"cancelled"` - 已取消

## 环境变量

当前版本暂不支持环境变量配置，后续版本可能添加：

```bash
# 计划支持的环境变量
export TASKM_STORE_PATH="/path/to/tasks.json"
export TASKM_DEFAULT_PRIORITY="high"
export TASKM_DATE_FORMAT="%Y-%m-%d"
```

## 扩展存储后端

要实现自定义存储后端，继承 `BaseTaskStore` 抽象类：

```python
from task_manager.base_store import BaseTaskStore

class DatabaseStore(BaseTaskStore):
    def __init__(self, connection_string: str):
        self.conn = create_connection(connection_string)
    
    def add(self, task: Task) -> str:
        # 实现数据库存储逻辑
        pass
    
    # 实现其他抽象方法...
```

## 性能优化

### JSON 文件大小

当任务数量增长到数万个时，建议：

1. 定期归档已完成任务
2. 使用数据库存储后端
3. 实现分页查询

### 搜索优化

当前搜索是线性查找，对于大量任务可考虑：

1. 添加索引支持
2. 使用全文搜索引擎
3. 实现缓存机制

## 相关文档

- [快速开始](getting-started.md)
- [架构总览](../architecture/overview.md)
- [技术决策](../development/tech-decisions.md)