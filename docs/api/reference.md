# API 参考

本文档提供 TaskManager 系统所有公共 API 的详细参考。

## 数据模型 API

### TaskStatus (枚举)

任务状态枚举类。

```python
from task_manager.models import TaskStatus

class TaskStatus(Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    CANCELLED = "cancelled"
```

### Priority (枚举)

任务优先级枚举类。

```python
from task_manager.models import Priority

class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4
```

### SubTask (数据类)

子任务数据模型。

```python
from task_manager.models import SubTask

@dataclass
class SubTask:
    title: str
    done: bool = False
    subtask_id: str = field(default_factory=lambda: uuid4().hex[:6])
```

**方法：**

#### `complete() -> None`
标记子任务为已完成。

```python
subtask = SubTask("编写测试")
subtask.complete()
print(subtask.done)  # True
```

### Task (数据类)

主要的任务数据模型。

```python
from task_manager.models import Task, TaskStatus, Priority

@dataclass
class Task:
    title: str
    description: str = ""
    status: TaskStatus = TaskStatus.TODO
    priority: Priority = Priority.MEDIUM
    assignee: Optional[str] = None
    tags: list[str] = field(default_factory=list)
    subtasks: list[SubTask] = field(default_factory=list)
    due_date: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    task_id: str = field(default_factory=lambda: uuid4().hex[:8])
```

**构造函数：**

```python
task = Task(
    title="完成项目文档",
    description="撰写用户手册和API文档",
    priority=Priority.HIGH
)
```

**方法：**

#### `mark_done() -> None`
标记任务为已完成，更新状态和时间戳。

```python
task.mark_done()
print(task.status)  # TaskStatus.DONE
```

#### `cancel() -> None`
取消任务，设置状态为 CANCELLED。

```python
task.cancel()
print(task.status)  # TaskStatus.CANCELLED
```

#### `start() -> None`
开始任务，设置状态为 IN_PROGRESS。

```python
task.start()
print(task.status)  # TaskStatus.IN_PROGRESS
```

#### `assign_to(user: str) -> None`
将任务分配给指定用户。

**参数：**
- `user` (str): 负责人姓名

```python
task.assign_to("张三")
print(task.assignee)  # "张三"
```

#### `add_subtask(title: str) -> SubTask`
添加子任务并返回子任务对象。

**参数：**
- `title` (str): 子任务标题

**返回值：** 创建的 SubTask 对象

```python
subtask = task.add_subtask("设计数据库表结构")
print(len(task.subtasks))  # 1
```

#### `to_dict() -> dict`
将任务序列化为字典格式。

**返回值：** 包含任务所有数据的字典

```python
data = task.to_dict()
print(data["title"])  # 任务标题
```

#### `from_dict(data: dict) -> Task` (类方法)
从字典反序列化创建任务对象。

**参数：**
- `data` (dict): 任务数据字典

**返回值：** Task 实例

```python
task = Task.from_dict({
    "task_id": "abc123",
    "title": "测试任务",
    "status": "todo",
    "priority": 2,
    "created_at": "2026-03-06T14:32:54",
    "updated_at": "2026-03-06T14:32:54"
})
```

**属性：**

#### `progress -> float`
基于子任务的完成进度（0.0 到 1.0）。

```python
print(task.progress)  # 0.5 (50% 完成)
```

#### `is_overdue -> bool`
检查任务是否已过期。

```python
if task.is_overdue:
    print("任务已逾期！")
```

## 存储 API

### BaseTaskStore (抽象基类)

存储后端的抽象接口。

```python
from task_manager.base_store import BaseTaskStore
```

**抽象方法：**

#### `add(task: Task) -> str`
添加任务到存储。

**参数：** Task 对象
**返回值：** 任务ID字符串

#### `get(task_id: str) -> Optional[Task]`
根据ID获取任务。

**参数：** 任务ID
**返回值：** Task对象或None

#### `update(task: Task) -> None`
更新已存在的任务。

**参数：** 更新后的Task对象

#### `remove(task_id: str) -> bool`
删除任务。

**参数：** 任务ID
**返回值：** 删除成功返回True，不存在返回False

#### `list_all() -> list[Task]`
获取所有任务，按优先级降序排列。

**返回值：** Task对象列表

#### `filter_by_status(status: TaskStatus) -> list[Task]`
根据状态筛选任务。

**参数：** TaskStatus 枚举值
**返回值：** 匹配的Task对象列表

#### `filter_by_assignee(assignee: str) -> list[Task]`
根据负责人筛选任务。

**参数：** 负责人姓名
**返回值：** 分配给该用户的Task对象列表

#### `search(keyword: str) -> list[Task]`
根据关键词搜索任务。

**参数：** 搜索关键词
**返回值：** 匹配的Task对象列表

#### `count -> int` (属性)
任务总数。

### MemoryStore

基于内存的存储实现。

```python
from task_manager.storage import MemoryStore

store = MemoryStore()
```

**特点：**
- 数据存储在内存中
- 进程结束后数据丢失
- 查询性能优秀
- 适用于测试

**使用示例：**

```python
store = MemoryStore()
task = Task("测试任务")
task_id = store.add(task)
retrieved = store.get(task_id)
print(retrieved.title)  # "测试任务"
```

### JsonStore

基于JSON文件的持久化存储。

```python
from task_manager.json_store import JsonStore

# 使用默认文件路径
store = JsonStore()

# 使用自定义文件路径
store = JsonStore("/path/to/my/tasks.json")
```

**构造函数：**

#### `JsonStore(file_path: str = "tasks.json")`

**参数：**
- `file_path` (str): JSON文件路径，默认为 "tasks.json"

**特点：**
- 数据持久化到JSON文件
- 自动处理文件加载和保存
- UTF-8编码支持中文
- 每次修改都会保存

## 统计 API

### summary(store: BaseTaskStore) -> dict

生成任务统计摘要。

```python
from task_manager.stats import summary

stats = summary(store)
```

**参数：**
- `store`: BaseTaskStore 实例

**返回值：** 包含统计信息的字典

```python
{
    "total": 10,
    "by_status": {
        "todo": 3,
        "in_progress": 2,
        "done": 4,
        "cancelled": 1
    },
    "by_priority": {
        "LOW": 2,
        "MEDIUM": 5,
        "HIGH": 2,
        "CRITICAL": 1
    },
    "overdue_count": 1,
    "completion_rate": 0.4
}
```

### format_summary(stats: dict) -> str

将统计数据格式化为可读字符串。

```python
from task_manager.stats import format_summary

formatted = format_summary(stats)
print(formatted)
```

**参数：**
- `stats`: summary() 返回的统计字典

**返回值：** 格式化的统计报表字符串

## CLI API

### main()

命令行程序的主入口点。

```python
from task_manager.cli import main

if __name__ == "__main__":
    main()
```

### 支持的命令

#### add - 添加任务

```bash
python -m task_manager.cli add "任务标题" [选项]
```

**选项：**
- `-d, --description`: 任务描述
- `-p, --priority`: 优先级 (low/medium/high/critical)
- `-a, --assignee`: 负责人

**示例：**
```bash
python -m task_manager.cli add "完成报告" -d "季度总结报告" -p high -a "张三"
```

#### list - 列出任务

```bash
python -m task_manager.cli list [选项]
```

**选项：**
- `-s, --status`: 按状态筛选 (todo/in_progress/done/cancelled)
- `-a, --assignee`: 按负责人筛选

**示例：**
```bash
python -m task_manager.cli list -s todo
python -m task_manager.cli list -a "张三"
```

#### done - 标记完成

```bash
python -m task_manager.cli done <task_id>
```

**示例：**
```bash
python -m task_manager.cli done a1b2c3d4
```

#### search - 搜索任务

```bash
python -m task_manager.cli search <关键词>
```

**示例：**
```bash
python -m task_manager.cli search "文档"
```

#### stats - 显示统计

```bash
python -m task_manager.cli stats
```

#### remove - 删除任务

```bash
python -m task_manager.cli remove <task_id>
```

**示例：**
```bash
python -m task_manager.cli remove a1b2c3d4
```

## 使用示例

### 基础任务操作

```python
from task_manager.models import Task, Priority, TaskStatus
from task_manager.json_store import JsonStore

# 创建存储实例
store = JsonStore()

# 创建任务
task = Task(
    title="实现用户认证",
    description="添加用户登录和注册功能",
    priority=Priority.HIGH
)

# 添加子任务
task.add_subtask("设计数据库表")
task.add_subtask("实现登录API")
task.add_subtask("编写前端页面")

# 保存任务
task_id = store.add(task)

# 查询任务
retrieved = store.get(task_id)
print(f"进度: {retrieved.progress:.0%}")

# 完成子任务
retrieved.subtasks[0].complete()
store.update(retrieved)

# 完成整个任务
retrieved.mark_done()
store.update(retrieved)
```

### 统计和报表

```python
from task_manager.stats import summary, format_summary

# 生成统计
stats = summary(store)

# 显示报表
report = format_summary(stats)
print(report)
```

## 相关文档

- [快速开始](../guide/getting-started.md)
- [架构总览](../architecture/overview.md)
- [模块详解](../architecture/modules.md)