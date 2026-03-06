# TaskManager 架构设计

## 系统概述

TaskManager 是一个基于 Python 的任务管理系统，采用分层架构设计，支持持久化存储和统计分析。系统包含数据模型层、存储抽象层、存储实现层、统计分析层和用户接口层。

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
- `subtasks`: 子任务列表
- `due_date`: 截止日期
- `created_at`: 创建时间
- `updated_at`: 更新时间

核心方法：
- `mark_done()`: 标记任务完成
- `cancel()`: 取消任务
- `start()`: 开始任务
- `assign_to(user)`: 分配任务
- `add_subtask(title)`: 添加子任务
- `to_dict()`: 序列化为字典
- `from_dict(data)`: 从字典反序列化

计算属性：
- `progress`: 基于子任务的完成进度
- `is_overdue`: 逾期检测

#### SubTask 类
轻量级子任务实体：
- `title`: 子任务标题
- `done`: 完成状态
- `subtask_id`: 6位唯一标识符
- `complete()`: 标记完成

#### 枚举类型
- `TaskStatus`: TODO, IN_PROGRESS, DONE, CANCELLED
- `Priority`: LOW(1), MEDIUM(2), HIGH(3), CRITICAL(4)

### 存储抽象层 (base_store.py)

#### BaseTaskStore 抽象基类
定义存储接口规范：
- `add(task)`: 添加任务
- `get(task_id)`: 获取单个任务
- `update(task)`: 更新任务
- `remove(task_id)`: 删除任务
- `list_all()`: 获取所有任务（按优先级排序）
- `filter_by_status(status)`: 按状态过滤
- `filter_by_assignee(assignee)`: 按指派人过滤
- `search(keyword)`: 关键字搜索
- `count`: 任务总数（属性）

### 存储实现层

#### MemoryStore (storage.py)
内存存储实现（原TaskStore）：
- 非持久化，程序重启数据丢失
- 适用于临时测试和开发环境
- 实现BaseTaskStore的所有抽象方法

#### JsonStore (json_store.py)
持久化JSON文件存储：
- 数据保存在本地JSON文件（默认tasks.json）
- 自动加载和保存数据
- 支持序列化和反序列化
- 默认存储后端

### 统计分析层 (stats.py)

提供任务统计和报告功能：
- `summary(store)`: 生成统计摘要（总数、状态分布、优先级分布、逾期数量、完成率）
- `format_summary(stats)`: 格式化统计报告

### 用户接口层 (cli.py)

命令行接口，支持以下命令：
1. `add`: 创建新任务（支持描述、优先级、指派人）
2. `list`: 列出任务（可按状态或指派人过滤）
3. `done`: 标记任务完成
4. `search`: 关键字搜索任务
5. `stats`: 显示统计信息
6. `remove`: 删除任务

## 架构特性

### 存储后端解耦
- 通过BaseTaskStore抽象接口实现存储解耦
- CLI层通过`_get_store()`函数获取存储实例
- 默认使用JsonStore提供持久化
- 可轻松切换存储后端

### 数据持久化
- JsonStore提供自动序列化/反序列化
- Task.to_dict()/from_dict()支持完整数据转换
- 所有修改操作自动触发保存

### 扩展功能
- 子任务系统支持任务分解
- 截止日期和逾期提醒
- 任务搜索和统计分析
- 多状态和优先级支持

## 数据流

1. 用户通过CLI输入命令
2. CLI解析参数并调用相应处理函数
3. 处理函数通过存储抽象接口操作数据
4. 存储后端（JsonStore）执行实际的数据操作
5. 数据变更自动持久化到JSON文件
6. 结果反馈给用户

## 设计原则

- **单一职责**: 每个模块负责特定功能
- **接口抽象**: BaseTaskStore抽象存储实现细节
- **低耦合**: 层间依赖通过接口，便于测试和扩展
- **类型安全**: 广泛使用类型注解和枚举
- **可扩展性**: 模块化设计支持功能扩展
- **数据完整性**: 序列化/反序列化保证数据一致性