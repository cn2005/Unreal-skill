# UE Compile Helper

Unreal Engine C++ 自动化编译检查工具。

## 文件结构

```
ue-compile-helper/
├── SKILL.md           # Skill 说明文档
└── scripts/
    └── auto_compile_check.py  # 自动编译检查脚本
```

## 使用方法

### 方式 1：命令行直接运行（推荐）

在 UE 项目目录中运行：

```bash
python "C:\Users\cn133\.config\opencode\skills\ue-compile-helper\scripts\auto_compile_check.py"
```

### 方式 2：传入文件路径

```bash
python "C:\Users\cn133\.config\opencode\skills\ue-compile-helper\scripts\auto_compile_check.py" "C:\MyProject\Source\MyActor.cpp"
```

## 工作流程

1. **自动检测 UE 引擎路径** - 从环境变量或常见安装位置查找
2. **自动检测 UE 项目** - 向上查找 .uproject 文件
3. **UBT 命令行编译** - 不关闭 UE 编辑器
4. **解析编译输出** - 提取错误和警告
5. **输出报告** - 返回给 AI 自动修复

## 编译报告格式

```
❌ 编译失败。3 个错误, 1 个警告

编译耗时: 12.5s

错误 1: C:\MyProject\Source\MyActor.h(45): error C2065: 'UObject': undeclared identifier
错误 2: C:\MyProject\Source\MyActor.cpp(12): error C2011: 'AMyActor': 'class' type redefinition
错误 3: C:\MyProject\Source\MyActor.cpp(67): error C2660: 'AMyActor::BeginPlay': function does not match declaration
```

## 常见错误修复

- **C2065**: 缺少头文件 include
- **C2011**: 重复定义，添加 `#pragma once`
- **C2660**: 函数签名不匹配
- **Missing GENERATED_BODY**: 添加 `GENERATED_BODY()`
