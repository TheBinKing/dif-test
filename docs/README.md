# TaskManager

一个任务管理系统，支持持久化存储和统计分析。通过命令行创建、查看和管理任务。

## 功能特性

- 创建任务（支持标题、描述、优先级、指派人）
- 查看任务列表（支持按状态过滤、按指派人过滤）
- 标记任务完成或取消
- 支持四种优先级：低、中、高、关键
- 支持四种状态：待办、进行中、已完成、已取消
- 任务分配功能
- 标签系统
- 子任务支持
- 任务截止日期和逾期提醒
- 任务搜索功能
- 统计分析功能
- 持久化存储（JSON文件）

## 安装和使用

### 添加新任务
```bash
python -m task_manager.cli add "完成项目文档" -d "编写用户手册和API文档" -p high -a "张三"
```

### 查看所有任务
```bash
python -m task_manager.cli list
```

### 按状态过滤任务
```bash
python -m task_manager.cli list -s todo
```

### 按指派人过滤任务
```bash
python -m task_manager.cli list -a "张三"
```

### 标记任务完成
```bash
python -m task_manager.cli done <task_id>
```

### 搜索任务
```bash
python -m task_manager.cli search "文档"
```

### 查看统计信息
```bash
python -m task_manager.cli stats
```

### 删除任务
```bash
python -m task_manager.cli remove <task_id>
```

## 版本信息

当前版本：0.2.0