# API 参考文档

## 数据模型

### Task

任务对象表示系统中的一个任务项。

#### 属性

| 属性 | 类型 | 默认值 | 描述 |
|------|------|--------|----- |
| `title` | `str` | 必需 | 任务标题 |
| `description` | `str` | `""` | 任务描述 |
| `status` | `TaskStatus` | `TaskStatus.TODO` | 任务状态 |
| `priority` | `Priority` | `Priority.MEDIUM` | 优先级 |
| `assignee` | `Optional[str]` | `None` | 指派人员 |
| `tags` | `list[str]` | `[]` | 标签列表 |
| `subtasks` | `list[SubTask]` | `[]` | 子任务列表 |
| `due_date` | `Optional[datetime]` | `None` | 截止日期 |
| `created_at` | `datetime` | 当前时间 | 创建时间 |
| `updated_at` | `datetime` | 当前时间 | 更新时间 |
| `task_id` | `str` | 自动生成 | 唯一标识符 |

#### 方法

##### `mark_done() -> None`
标记任务为已完成状态。
- 设置 `status` 为 `TaskStatus.DONE`
- 更新 `updated_at` 时间戳

##### `cancel() -> None`
取消任务。
- 设置 `status` 为 `TaskStatus.CANCELLED`
- 更新 `updated_at` 时间戳

##### `start() -> None`
将任务状态设置为进行中。
- 设置 `status` 为 `TaskStatus.IN_PROGRESS`
- 更新 `updated_at` 时间戳

##### `assign_to(user: str) -> None`
将任务分配给指定用户。
- 参数：`user` - 用户名称
- 更新 `assignee` 和 `updated_at`

##### `add_subtask(title: str) -> SubTask`
添加子任务并返回。
- 参数：`title` - 子任务标题
- 返回：新创建的SubTask实例
- 更新 `updated_at` 时间戳

#### 只读属性

##### `progress -> float`
基于子任务完成情况返回进度（0.0到1.0）。
- 无子任务时：已完成任务返回1.0，其他返回0.0
- 有子任务时：返回已完成子任务的比例

##### `is_overdue -> bool`
检查任务是否已逾期。
- 无截止日期时返回False
- 有截止日期且已超时且状态非已完成时返回True

##### `to_dict() -> dict`
将任务序列化为字典。
- 返回包含所有任务属性的字典

##### `from_dict(data: dict) -> Task` (类方法)
从字典反序列化任务。
- 参数：`data` - 任务数据字典
- 返回：Task实例

### SubTask

轻量级子任务，属于父任务。

#### 属性

| 属性 | 类型 | 默认值 | 描述 |
|------|------|--------|----- |
| `title` | `str` | 必需 | 子任务标题 |
| `done` | `bool` | `False` | 完成状态 |
| `subtask_id` | `str` | 自动生成 | 唯一标识符（6位） |

#### 方法

##### `complete() -> None`
标记子任务为完成状态。

### 枚举类型

#### TaskStatus
任务状态枚举。

- `TODO = "todo"` - 待办
- `IN_PROGRESS = "in_progress"` - 进行中
- `DONE = "done"` - 已完成
- `CANCELLED = "cancelled"` - 已取消

#### Priority
优先级枚举。

- `LOW = 1` - 低优先级
- `MEDIUM = 2` - 中优先级
- `HIGH = 3` - 高优先级
- `CRITICAL = 4` - 关键优先级

## 存储接口

### BaseTaskStore (抽象基类)

任务存储的抽象接口。

#### `add(task: Task) -> str`
添加任务并返回其ID。
- 参数：`task` - Task实例
- 返回：任务ID字符串

#### `get(task_id: str) -> Optional[Task]`
根据ID获取任务。
- 参数：`task_id` - 任务ID
- 返回：Task实例或None

#### `update(task: Task) -> None`
持久化已有任务的更改。
- 参数：`task` - 要更新的Task实例

#### `remove(task_id: str) -> bool`
删除指定任务。
- 参数：`task_id` - 任务ID
- 返回：删除成功返回True，否则False

#### `list_all() -> list[Task]`
获取所有任务，按优先级降序排列。
- 返回：Task对象列表

#### `filter_by_status(status: TaskStatus) -> list[Task]`
按状态筛选任务。
- 参数：`status` - TaskStatus枚举值
- 返回：匹配的Task对象列表

#### `filter_by_assignee(assignee: str) -> list[Task]`
按指派人筛选任务。
- 参数：`assignee` - 用户名称
- 返回：匹配的Task对象列表

#### `search(keyword: str) -> list[Task]`
在任务标题和描述中搜索关键字。
- 参数：`keyword` - 搜索关键字
- 返回：匹配的Task对象列表

#### `count -> int`
获取任务总数量（只读属性）。
- 返回：整数任务数量

### MemoryStore (原TaskStore)

内存存储实现（非持久化）。继承BaseTaskStore的所有方法。

### JsonStore

基于JSON文件的持久化存储实现。

#### `__init__(file_path: str = "tasks.json") -> None`
初始化JSON存储。
- 参数：`file_path` - JSON文件路径，默认"tasks.json"
- 自动加载现有数据

## 统计分析

### stats.summary(store: BaseTaskStore) -> dict
生成任务统计摘要。
- 参数：`store` - 存储后端实例
- 返回：包含统计信息的字典

### stats.format_summary(stats: dict) -> str
将统计信息格式化为可读字符串。
- 参数：`stats` - 统计数据字典
- 返回：格式化的统计报告字符串

## CLI 命令

### add
创建新任务。

```bash
taskm add <title> [-d DESCRIPTION] [-p {low,medium,high,critical}] [-a ASSIGNEE]
```

- `title`: 任务标题（必需）
- `-d, --description`: 任务描述（可选）
- `-p, --priority`: 优先级，默认medium
- `-a, --assignee`: 指派人（可选）

### list
列出任务。

```bash
taskm list [-s {todo,in_progress,done,cancelled}] [-a ASSIGNEE]
```

- `-s, --status`: 按状态过滤（可选）
- `-a, --assignee`: 按指派人过滤（可选）

### done
标记任务完成。

```bash
taskm done <task_id>
```

- `task_id`: 要标记完成的任务ID

### search
搜索任务。

```bash
taskm search <keyword>
```

- `keyword`: 在标题和描述中搜索的关键字

### stats
显示任务统计信息。

```bash
taskm stats
```

### remove
删除任务。

```bash
taskm remove <task_id>
```

- `task_id`: 要删除的任务ID