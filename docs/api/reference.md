# API 参考

本文档提供 TaskManager v0.3.0 系统所有公共 API 的详细参考。

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
    tags: list[str] = field(default_factory=list)  # 新增：标签支持
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
    priority=Priority.HIGH,
    tags=["documentation", "important"]
)
```

所有原有方法保持不变，Task 类新增标签支持但其他 API 接口未变更。

## 事件系统 API

### EventType (枚举)

系统事件类型枚举。

```python
from task_manager.events import EventType

class EventType(Enum):
    TASK_CREATED = "task_created"
    TASK_UPDATED = "task_updated"
    TASK_COMPLETED = "task_completed"
    TASK_CANCELLED = "task_cancelled"
    TASK_DELETED = "task_deleted"
    TASK_ASSIGNED = "task_assigned"
    TASK_OVERDUE = "task_overdue"
    SUBTASK_ADDED = "subtask_added"
    SUBTASK_COMPLETED = "subtask_completed"
    BATCH_IMPORT = "batch_import"
    BATCH_EXPORT = "batch_export"
```

### Event (数据类)

事件数据载体。

```python
from task_manager.events import Event, EventType

@dataclass
class Event:
    event_type: EventType
    timestamp: datetime = field(default_factory=datetime.now)
    task_id: Optional[str] = None
    payload: dict[str, Any] = field(default_factory=dict)
```

**属性：**

#### `key -> str`
返回事件的短字符串标识符。

```python
event = Event(EventType.TASK_COMPLETED, task_id="abc123")
print(event.key)  # "task_completed:abc123"
```

### EventBus (核心类)

事件总线，负责事件分发和管理。

```python
from task_manager.events import EventBus, get_event_bus

# 获取全局单例
bus = get_event_bus()

# 或创建新实例
bus = EventBus()
```

**方法：**

#### `subscribe(event_type: Optional[EventType], handler: EventHandler) -> None`
订阅事件处理器。

**参数：**
- `event_type`: 要监听的事件类型，传入 `None` 监听所有事件
- `handler`: 事件处理函数，签名为 `(Event) -> None`

```python
def on_task_done(event: Event):
    print(f"Task {event.task_id} completed!")

bus.subscribe(EventType.TASK_COMPLETED, on_task_done)

# 监听所有事件
def log_all(event: Event):
    print(f"Event: {event.key}")

bus.subscribe(None, log_all)
```

#### `unsubscribe(event_type: Optional[EventType], handler: EventHandler) -> None`
取消订阅事件处理器。

#### `emit(event: Event) -> None`
发出事件，触发所有匹配的处理器。

```python
bus.emit(Event(
    EventType.TASK_COMPLETED,
    task_id="abc123",
    payload={"title": "完成文档"}
))
```

#### `get_history(event_type: Optional[EventType] = None, limit: int = 50) -> list[Event]`
获取事件历史记录。

**参数：**
- `event_type`: 事件类型过滤器，`None` 返回所有类型
- `limit`: 最大返回数量

```python
# 获取最近20个完成事件
recent_completions = bus.get_history(EventType.TASK_COMPLETED, 20)

# 获取最近50个事件
recent_events = bus.get_history(limit=50)
```

#### `clear_history() -> None`
清空事件历史记录。

#### `handler_count -> int` (属性)
返回已注册的处理器总数。

### 工具函数

#### `get_event_bus() -> EventBus`
获取全局事件总线单例。

#### `reset_event_bus() -> None`
重置全局事件总线（主要用于测试）。

## 模板系统 API

### TaskTemplate (数据类)

任务模板数据模型。

```python
from task_manager.templates import TaskTemplate
from task_manager.models import Priority

@dataclass
class TaskTemplate:
    name: str
    title_pattern: str
    description_pattern: str = ""
    default_priority: Priority = Priority.MEDIUM
    default_tags: list[str] = field(default_factory=list)
    subtask_titles: list[str] = field(default_factory=list)
    variables: dict[str, str] = field(default_factory=dict)
```

**方法：**

#### `render(overrides: Optional[dict[str, str]] = None) -> Task`
从模板生成任务实例。

**参数：**
- `overrides`: 变量值覆盖字典

**返回值：** 生成的 Task 对象

```python
template = TaskTemplate(
    name="bug-fix",
    title_pattern="Fix: {summary}",
    description_pattern="Bug report: {details}",
    subtask_titles=["Reproduce issue", "Fix code", "Test"],
    variables={"summary": "", "details": ""}
)

task = template.render({
    "summary": "Login fails",
    "details": "Users cannot sign in"
})
print(task.title)  # "Fix: Login fails"
```

#### `to_dict() -> dict[str, Any]`
序列化模板为字典。

#### `from_dict(data: dict[str, Any]) -> TaskTemplate` (类方法)
从字典反序列化模板。

### TemplateRegistry (管理类)

模板注册表，管理模板的存储和加载。

```python
from task_manager.templates import TemplateRegistry

# 使用默认文件路径
registry = TemplateRegistry()

# 使用自定义文件路径
registry = TemplateRegistry("my_templates.json")
```

**构造函数：**

#### `TemplateRegistry(file_path: Optional[str] = None)`

**参数：**
- `file_path`: JSON文件路径，`None` 表示仅内存存储

**方法：**

#### `add(template: TaskTemplate) -> None`
添加或更新模板。

```python
registry.add(TaskTemplate(
    name="meeting",
    title_pattern="{type} meeting: {topic}",
    default_tags=["meeting"]
))
```

#### `get(name: str) -> Optional[TaskTemplate]`
根据名称获取模板。

#### `remove(name: str) -> bool`
删除模板，成功返回 `True`。

#### `list_all() -> list[TaskTemplate]`
获取所有已注册模板。

#### `builtin_templates() -> list[TaskTemplate]` (静态方法)
获取内置模板列表。

```python
builtins = TemplateRegistry.builtin_templates()
for template in builtins:
    print(f"{template.name}: {template.title_pattern}")
```

**内置模板：**
- `bug-fix` - Bug修复工作流
- `feature` - 功能开发模板
- `release` - 版本发布检查清单

## 批量操作 API

### BatchOperations (操作类)

批量任务操作的高级接口。

```python
from task_manager.batch import BatchOperations

batch = BatchOperations(store)
```

**构造函数：**

#### `BatchOperations(store: BaseTaskStore)`

**参数：**
- `store`: 任务存储实例

**方法：**

#### `import_from_json(file_path: str) -> list[Task]`
从JSON文件导入任务。

**参数：**
- `file_path`: JSON文件路径

**返回值：** 成功导入的任务列表

```python
imported = batch.import_from_json("backup.json")
print(f"Imported {len(imported)} tasks")
```

#### `export_to_json(file_path: str, status_filter: Optional[TaskStatus] = None) -> int`
导出任务到JSON文件。

**参数：**
- `file_path`: 输出文件路径
- `status_filter`: 状态过滤器，`None` 导出所有任务

**返回值：** 导出的任务数量

```python
# 导出所有任务
count = batch.export_to_json("all_tasks.json")

# 仅导出已完成任务
count = batch.export_to_json("done_tasks.json", TaskStatus.DONE)
```

#### `complete_all(task_ids: Optional[list[str]] = None) -> int`
批量完成任务。

**参数：**
- `task_ids`: 任务ID列表，`None` 表示完成所有未完成任务

**返回值：** 实际完成的任务数量

```python
# 完成指定任务
count = batch.complete_all(["abc123", "def456"])

# 完成所有待办任务
count = batch.complete_all()
```

#### `cancel_all(task_ids: Optional[list[str]] = None) -> int`
批量取消任务。

#### `reassign_all(task_ids: list[str], new_assignee: str) -> int`
批量重新分配任务。

**参数：**
- `task_ids`: 任务ID列表
- `new_assignee`: 新的负责人

**返回值：** 重新分配的任务数量

```python
count = batch.reassign_all(["abc123", "def456"], "张三")
print(f"Re-assigned {count} tasks to 张三")
```

#### `find_duplicates(threshold: float = 0.8) -> list[tuple[Task, Task]]`
查找重复任务。

**参数：**
- `threshold`: 相似度阈值（0.0-1.0）

**返回值：** 疑似重复任务对列表

```python
duplicates = batch.find_duplicates(threshold=0.9)
for task_a, task_b in duplicates:
    print(f"Similar: {task_a.title} vs {task_b.title}")
```

## 插件系统 API

### PluginMeta (数据类)

插件元数据。

```python
from task_manager.plugins import PluginMeta

@dataclass
class PluginMeta:
    name: str
    version: str
    description: str
    author: str = ""
```

### BasePlugin (抽象基类)

所有插件的基类。

```python
from task_manager.plugins import BasePlugin
from task_manager.events import EventBus

class MyPlugin(BasePlugin):
    def __init__(self, event_bus: EventBus, config: dict):
        super().__init__(event_bus, config)
    
    @property
    def meta(self) -> PluginMeta:
        return PluginMeta(
            name="my-plugin",
            version="1.0.0",
            description="My custom plugin"
        )
    
    def activate(self):
        self.bus.subscribe(EventType.TASK_COMPLETED, self._on_complete)
    
    def _on_complete(self, event):
        print(f"Task completed: {event.task_id}")
```

**构造函数：**

#### `BasePlugin(event_bus: Optional[EventBus] = None, config: Optional[dict[str, Any]] = None)`

**参数：**
- `event_bus`: 事件总线实例，默认使用全局单例
- `config`: 插件配置字典

**抽象方法：**

#### `meta -> PluginMeta` (属性)
返回插件元数据。

#### `activate() -> None`
激活插件，注册事件处理器。

**可选方法：**

#### `deactivate() -> None`
停用插件，清理资源。默认为空实现。

### PluginRegistry (管理类)

插件注册表，管理插件生命周期。

```python
from task_manager.plugins import PluginRegistry

registry = PluginRegistry()
```

**方法：**

#### `register(plugin_cls: type[BasePlugin], config: Optional[dict[str, Any]] = None) -> BasePlugin`
注册并激活插件。

**参数：**
- `plugin_cls`: 插件类
- `config`: 插件配置

**返回值：** 插件实例

```python
class NotifyPlugin(BasePlugin):
    # ... 插件实现

plugin = registry.register(NotifyPlugin, {
    "log_file": "/tmp/notifications.log"
})
```

#### `unregister(name: str) -> None`
注销插件。

#### `get(name: str) -> Optional[BasePlugin]`
根据名称获取插件实例。

#### `loaded -> list[str]` (属性)
返回所有已加载插件的名称列表。

#### `shutdown() -> None`
关闭所有插件。

## 内置插件 API

### NotificationPlugin

任务事件通知插件。

```python
from task_manager.plugins.notification import NotificationPlugin

plugin = NotificationPlugin(config={
    "log_file": "notifications.log",
    "notify_events": ["task_completed", "task_overdue"]
})
```

**配置选项：**
- `log_file` (str): 日志文件路径，可选
- `notify_events` (list[str]): 要通知的事件类型列表

### ExportPlugin

任务导出插件。

```python
from task_manager.plugins.export import ExportPlugin

plugin = ExportPlugin()
csv_content = plugin.export_tasks(tasks, fmt="csv")
```

**方法：**

#### `export_tasks(tasks: list[Task], fmt: str = "json", output_path: Optional[str] = None) -> str`
导出任务到指定格式。

**参数：**
- `tasks`: 要导出的任务列表
- `fmt`: 输出格式（json/csv/markdown）
- `output_path`: 输出文件路径，`None` 返回字符串

**返回值：** 格式化的内容字符串

## CLI API

命令行界面保持原有的所有命令，新增以下命令组：

### 模板命令

```bash
# 列出模板
python -m task_manager.cli template list

# 使用模板
python -m task_manager.cli template use <name> [-v key=value] [-a assignee]
```

### 批量命令

```bash
# 批量完成
python -m task_manager.cli batch complete [task_id...]

# 批量取消
python -m task_manager.cli batch cancel [task_id...]
```

### 导入导出命令

```bash
# 导入任务
python -m task_manager.cli import <file>

# 导出任务
python -m task_manager.cli export [-f format] [-o output]
```

### 工具命令

```bash
# 查找重复
python -m task_manager.cli duplicates [--threshold 0.8]

# 事件历史
python -m task_manager.cli history [-n limit]

# 插件状态
python -m task_manager.cli plugins
```

### 增强的现有命令

#### add 命令新增参数
```bash
python -m task_manager.cli add "title" [-t tags] [...other options]
```

- `-t, --tags`: 逗号分隔的标签列表

## 使用示例

### 事件系统使用

```python
from task_manager.events import get_event_bus, Event, EventType
from task_manager.models import Task

# 获取事件总线
bus = get_event_bus()

# 订阅事件
def on_task_created(event: Event):
    print(f"New task: {event.payload['title']}")

bus.subscribe(EventType.TASK_CREATED, on_task_created)

# 创建任务（会自动触发事件）
task = Task(title="测试任务")
store.add(task)
```

### 模板系统使用

```python
from task_manager.templates import TaskTemplate, TemplateRegistry

# 创建自定义模板
template = TaskTemplate(
    name="code-review",
    title_pattern="Review: {pr_title}",
    description_pattern="Code review for PR #{pr_number}",
    default_tags=["review"],
    subtask_titles=["Read code", "Test changes", "Provide feedback"]
)

# 注册模板
registry = TemplateRegistry("templates.json")
registry.add(template)

# 使用模板
task = template.render({
    "pr_title": "Fix login bug",
    "pr_number": "123"
})
```

### 批量操作使用

```python
from task_manager.batch import BatchOperations
from task_manager.json_store import JsonStore

store = JsonStore()
batch = BatchOperations(store)

# 导出已完成任务
batch.export_to_json("completed.json", TaskStatus.DONE)

# 批量完成所有高优先级任务
high_priority = store.filter_by_priority(Priority.HIGH)
task_ids = [t.task_id for t in high_priority if t.status == TaskStatus.TODO]
batch.complete_all(task_ids)
```

### 插件开发示例

```python
from task_manager.plugins import BasePlugin, PluginMeta
from task_manager.events import Event, EventType

class SlackPlugin(BasePlugin):
    @property
    def meta(self) -> PluginMeta:
        return PluginMeta(
            name="slack",
            version="1.0.0",
            description="Send notifications to Slack"
        )
    
    def activate(self):
        self.webhook_url = self.config.get("webhook_url")
        self.bus.subscribe(EventType.TASK_COMPLETED, self._notify_slack)
    
    def _notify_slack(self, event: Event):
        # 发送Slack通知的实现
        pass
```

## 相关文档

- [快速开始](../guide/getting-started.md)
- [架构总览](../architecture/overview.md)
- [模块详解](../architecture/modules.md)