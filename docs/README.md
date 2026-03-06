# TaskManager

一个简单的任务管理系统，支持通过命令行创建、查看和管理任务。

## 功能特性

- 创建任务（支持标题、描述、优先级）
- 查看任务列表（支持按状态过滤）
- 标记任务完成
- 支持三种优先级：低、中、高
- 支持三种状态：待办、进行中、已完成
- 任务分配功能
- 标签系统

## 安装和使用

### 添加新任务
```bash
python -m task_manager.cli add "完成项目文档" -d "编写用户手册和API文档" -p high
```

### 查看所有任务
```bash
python -m task_manager.cli list
```

### 按状态过滤任务
```bash
python -m task_manager.cli list -s todo
```

### 标记任务完成
```bash
python -m task_manager.cli done <task_id>
```

## 版本信息

当前版本：0.1.0