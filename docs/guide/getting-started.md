# 快速开始

本指南将帮助您快速安装和开始使用 TaskManager v0.3.0。

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

# 添加带描述、优先级和标签的任务
python -m task_manager.cli add "修复登录BUG" -d "用户无法正常登录系统" -p high -t "bug,urgent"

# 添加任务并指派给用户
python -m task_manager.cli add "代码审查" -a "张三" -p medium
```

### 查看任务

```bash
# 查看所有任务（显示标签和进度）
python -m task_manager.cli list

# 按状态筛选
python -m task_manager.cli list -s todo
python -m task_manager.cli list -s done

# 按负责人筛选
python -m task_manager.cli list -a "张三"
```

### 使用任务模板

```bash
# 查看可用模板
python -m task_manager.cli template list

# 使用内置bug修复模板
python -m task_manager.cli template use bug-fix -v summary="登录失败" -v steps="1. 打开应用 2. 输入错误密码" -a "李四"

# 使用功能开发模板
python -m task_manager.cli template use feature -v feature_name="用户头像上传" -v role="用户" -v goal="上传个人头像"
```

### 批量操作

```bash
# 批量完成任务
python -m task_manager.cli batch complete abc123 def456

# 批量完成所有待办任务
python -m task_manager.cli batch complete

# 查找重复任务
python -m task_manager.cli duplicates --threshold 0.8
```

### 导入导出

```bash
# 导出任务为JSON格式
python -m task_manager.cli export -f json -o tasks_backup.json

# 导出为CSV格式
python -m task_manager.cli export -f csv -o tasks.csv

# 导出为Markdown格式
python -m task_manager.cli export -f markdown -o tasks.md

# 从JSON文件导入任务
python -m task_manager.cli import tasks_backup.json
```

### 更新任务状态

```bash
# 标记任务为完成
python -m task_manager.cli done <task_id>
```

### 搜索和统计

```bash
# 根据关键词搜索
python -m task_manager.cli search "登录"

# 显示任务统计
python -m task_manager.cli stats

# 查看事件历史
python -m task_manager.cli history
```

### 插件管理

```bash
# 查看加载的插件
python -m task_manager.cli plugins
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

### 标签
使用逗号分隔的标签来组织任务：
```bash
python -m task_manager.cli add "新功能开发" -t "feature,frontend,v2.0"
```

## 内置模板

系统提供以下内置模板：

- **bug-fix** - Bug修复模板，包含复现、分析、修复、测试等步骤
- **feature** - 功能开发模板，包含设计、实现、测试、文档等子任务
- **release** - 版本发布模板，包含完整的发布检查清单

## 数据存储

默认情况下，所有任务数据保存在当前目录的 `tasks.json` 文件中。模板数据保存在 `templates.json` 文件中。系统会自动处理数据的加载和保存。

## 示例工作流

```bash
# 1. 使用模板创建Bug修复任务
python -m task_manager.cli template use bug-fix -v summary="登录页面崩溃" -a "张三"

# 2. 添加常规任务
python -m task_manager.cli add "更新文档" -p low -t "docs"

# 3. 查看任务列表
python -m task_manager.cli list

# 4. 完成一个任务
python -m task_manager.cli done <task_id>

# 5. 查看统计和事件历史
python -m task_manager.cli stats
python -m task_manager.cli history

# 6. 导出备份
python -m task_manager.cli export -f json -o backup.json
```

## 相关文档

- [配置说明](configuration.md)
- [架构总览](../architecture/overview.md)
- [API 参考](../api/reference.md)