# 快速开始

本指南将帮助您快速安装和开始使用 TaskManager。

## 安装要求

- Python 3.8 或更高版本

## 安装步骤

1. 克隆项目仓库：
   ```bash
   git clone <repository-url>
   cd taskmanager
   ```

2. 安装依赖（如果有）：
   ```bash
   pip install -r requirements.txt
   ```

3. 验证安装：
   ```bash
   python -m task_manager.cli --help
   ```

## 基础使用

### 添加任务

```bash
# 添加简单任务
python -m task_manager.cli add "完成项目文档"

# 添加带描述和优先级的任务
python -m task_manager.cli add "修复登录BUG" -d "用户无法正常登录系统" -p high

# 添加任务并指派给用户
python -m task_manager.cli add "代码审查" -a "张三" -p medium
```

### 查看任务

```bash
# 查看所有任务
python -m task_manager.cli list

# 按状态筛选
python -m task_manager.cli list -s todo
python -m task_manager.cli list -s done

# 按负责人筛选
python -m task_manager.cli list -a "张三"
```

### 更新任务状态

```bash
# 标记任务为完成
python -m task_manager.cli done <task_id>
```

### 搜索任务

```bash
# 根据关键词搜索
python -m task_manager.cli search "登录"
```

### 查看统计信息

```bash
# 显示任务统计
python -m task_manager.cli stats
```

### 删除任务

```bash
# 删除指定任务
python -m task_manager.cli remove <task_id>
```

## 任务属性说明

### 优先级
- `low` - 低优先级
- `medium` - 中等优先级（默认）
- `high` - 高优先级  
- `critical` - 紧急优先级

### 状态
- `todo` - 待办（默认）
- `in_progress` - 进行中
- `done` - 已完成
- `cancelled` - 已取消

## 数据存储

默认情况下，所有任务数据保存在当前目录的 `tasks.json` 文件中。系统会自动处理数据的加载和保存。

## 示例工作流

```bash
# 1. 添加几个任务
python -m task_manager.cli add "设计用户界面" -p high
python -m task_manager.cli add "实现后端API" -p medium -a "李四"
python -m task_manager.cli add "编写测试用例" -p low

# 2. 查看任务列表
python -m task_manager.cli list

# 3. 完成一个任务
python -m task_manager.cli done <task_id>

# 4. 查看完成情况统计
python -m task_manager.cli stats
```

## 相关文档

- [配置说明](configuration.md)
- [架构总览](../architecture/overview.md)
- [API 参考](../api/reference.md)