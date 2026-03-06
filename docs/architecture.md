# TaskManager 架构设计

## 系统概述

TaskManager 是一个基于 Python 的简单任务管理系统，采用分层架构设计，包含数据模型层、存储层和用户接口层。

## 核心组件

### 数据模型层 (models.py)

#### Task 类
核心任务实体，包含以下属性：
- `task_id`: 唯一标识符（8位UUID）
- `title`: 任务标题
- `description`: 任务描述
- `status`: 任务状态（TaskStatus枚举）
- `priority`: 优先级（Priority枚举）
- `assignee`: 指派人员
- `tags`: 标签列表
- `created_at`: 创建时间
- `updated_at`: 更新时间

核心方法：
- `mark_done()`: 标记任务完成
- `start()`: 开始任务
- `assign_to(user)`: 分配任务

#### 枚举类型
- `TaskStatus`: TODO, IN_PROGRESS, DONE
- `Priority`: LOW(1), MEDIUM(2), HIGH(3)

### 存储层 (storage.py)

#### TaskStore 类
内存存储实现，提供：
- `add(task)`: 添加任务
- `get(task_id)`: 获取单个任务
- `remove(task_id)`: 删除任务
- `list_all()`: 获取所有任务（按优先级排序）
- `filter_by_status(status)`: 按状态过滤
- `filter_by_assignee(assignee)`: 按指派人过滤

### 用户接口层 (cli.py)

命令行接口，支持三个主要命令：
1. `add`: 创建新任务
2. `list`: 列出任务（可按状态过滤）
3. `done`: 标记任务完成

## 数据流

1. 用户通过CLI输入命令
2. CLI解析参数并调用相应处理函数
3. 处理函数操作TaskStore实例
4. TaskStore操作Task对象
5. 结果反馈给用户

## 设计原则

- **单一职责**: 每个模块负责特定功能
- **低耦合**: 层间依赖清晰，易于测试和扩展
- **类型安全**: 使用类型注解和枚举确保数据完整性
- **可扩展性**: 存储层抽象化，便于后续支持持久化存储