# TaskManager

一个功能完整的任务管理系统，支持持久化存储、统计分析和灵活的命令行界面。

## 主要特性

- **任务管理** - 创建、更新、删除和搜索任务
- **状态跟踪** - TODO、进行中、完成、取消等状态管理
- **优先级分级** - 低、中、高、紧急四个优先级别
- **子任务支持** - 任务分解为可跟踪的子任务
- **截止日期** - 任务截止时间设置和逾期提醒
- **分配功能** - 任务可指派给特定用户
- **持久化存储** - JSON文件存储，数据不丢失
- **统计报表** - 任务完成率、状态分布等统计信息
- **命令行界面** - 简洁易用的CLI工具

## 快速开始

查看 [快速开始](guide/getting-started.md) 了解安装和基础使用方法。

## 系统架构

了解系统设计请参考 [架构总览](architecture/overview.md) 和 [模块详解](architecture/modules.md)。

## API 文档

完整的接口文档请查看 [API 参考](api/reference.md)。

## 技术栈

- **Python** 3.8+
- **架构模式** - 分层架构，抽象存储接口
- **存储后端** - 内存存储 / JSON文件存储
- **CLI框架** - argparse
- **数据模型** - dataclass + enum

## 相关文档

- [快速开始](guide/getting-started.md)
- [架构总览](architecture/overview.md)
- [API 参考](api/reference.md)