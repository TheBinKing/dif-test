# API 参考文档

## 数据模型

### Task

任务对象表示系统中的一个任务项。

#### 属性

| 属性 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| `title` | `str` | 必需 | 任务标题 |
| `description` | `str` | `""` | 任务描述 |
| `status` | `TaskStatus` | `TaskStatus.TODO` | 任务状态 |
| `priority` | `Priority` | `Priority.MEDIUM` | 优先级 |
| `assignee` | `Optional[str]` | `None` | 指派人员 |
| `tags` | `list[str]` | `[]` | 标签列表 |
| `created_at` | `datetime` | 当前时间 | 创建时间 |
| `updated_at` | `datetime` | 当前时间 | 更新时间 |
| `task_id` | `str` | 自动生成 | 唯一标识符 |

#### 方法

##### `mark_done() -> None`
标记任务为已完成状态。
- 设置 `status` 为 `TaskStatus.DONE`
- 更新 `updated_at` 时间戳

##### `start() -> None`
将任务状态设置为进行中。
- 设置 `status` 为 `TaskStatus.IN_PROGRESS`
- 更新 `updated_at` 时间戳

##### `assign_to(user: str) -> None`
将任务分配给指定用户。
- 参数：`user` - 用户名称
- 更新 `assignee` 和 `updated_at`

### 枚举类型

#### TaskStatus
任务状态枚举。

- `TODO = "todo"` - 待办
- `IN_PROGRESS = "in_progress"` - 进行中
- `DONE = "done"` - 已完成

#### Priority
优先级枚举。

- `LOW = 1` - 低优先级
- `MEDIUM = 2` - 中优先级
- `HIGH = 3` - 高优先级

## 存储接口

### TaskStore

任务存储管理类。

#### `add(task: Task) -> str`
添加新任务到存储中。
- 参数：`task` - Task实例
- 返回：任务ID字符串

#### `get(task_id: str) -> Optional[Task]`
根据ID获取任务。
- 参数：`task_id` - 任务ID
- 返回：Task实例或None

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

#### `count -> int`
获取任务总数量（只读属性）。
- 返回：整数任务数量

## CLI 命令

### add
创建新任务。

```bash
taskm add <title> [-d DESCRIPTION] [-p {low,medium,high}]
```

- `title`: 任务标题（必需）
- `-d, --description`: 任务描述（可选）
- `-p, --priority`: 优先级，默认medium

### list
列出任务。

```bash
taskm list [-s {todo,in_progress,done}]
```

- `-s, --status`: 按状态过滤（可选）

### done
标记任务完成。

```bash
taskm done <task_id>
```

- `task_id`: 要标记完成的任务ID