---
name: ue-compile-helper
description: Unreal Engine C++ 自动化编译修复。每次编写完 UE C++ 脚本后自动执行编译检查，解析错误报告并自动修复。触发关键词：编译, 热编译, 命令行编译, 编译错误, 自动编译, UE 编译, 虚幻编译, 编译修复, auto compile, Live Coding.
metadata:
  version: 3.0.0
---

# UE Compile Helper - 编译工作流手册

UE C++ 代码编写后的**编译检测 → 错误解析 → AI 修复 → 自动重启**闭环。

---

## ⚠️ 核心规则：根据改动类型选择编译方式

| 改动类型 | 编译方式 | 用户操作 | 耗时 |
|---------|---------|---------|------|
| **添加新类/新文件** | 命令行 UBT + 自动重启 | **零！全自动** | 10-60秒 |
| **修改现有 .cpp** | Live Coding | 按 Ctrl+Alt+F11 | 秒级 |

---

## 全自动工作流（添加新类时）

```
AI 写代码 → 自动检测改动类型 → 是新类？
    │
    ├─ 是新类 → 脚本自动执行：
    │     1. 检测并关闭 UE 编辑器
    │     2. 等待 DLL 解锁
    │     3. UBT 命令行编译
    │     4. 编译成功 → 自动重启 UE
    │     5. 编译失败 → 输出错误报告
    │
    └─ 否（修改现有代码）→ 提示用 Live Coding
```

### 用户只需做一件事：**测试**

---

## 工作流详解

### 场景 1：添加新类/新文件（全自动）

**用户零操作！** AI 触发脚本，脚本自动完成：

1. **检测 UE 进程** → 找到关联的 UnrealEditor.exe
2. **关闭 UE** → 优雅终止，等待 DLL 释放
3. **UBT 编译** → 命令行执行
4. **自动重启** → 编译成功后启动 UE 编辑器
5. **报告结果** → AI 读取错误，自动修复，循环

**触发命令：**
```bash
python "C:\Users\cn133\.config\opencode\skills\ue-compile-helper\scripts\auto_compile_check.py"
```

### 场景 2：修改现有 .cpp（Live Coding）

```
AI 修改 .cpp → 提示用户 → 用户按 Ctrl+Alt+F11 → 秒级生效
```

---

## 编译错误解析

| 错误代码 | 原因 | 修复 |
|---------|------|------|
| C2065 | 未声明标识符 | 添加 #include |
| C2011 | 重复定义 | 添加 #pragma once |
| C2660 | 函数签名不匹配 | 对比 .h 和 .cpp |
| C2653 | 不是类或命名空间 | 检查拼写或 include |

---

## UE C++ 标准模板

### 头文件 (.h)

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "ClassName.generated.h"  // 必须在最后

UCLASS()
class MYPROJECT_API AClassName : public AActor
{
    GENERATED_BODY()

public:
    AClassName();

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Custom")
    int32 MyVariable;

    UFUNCTION(BlueprintCallable, Category="Custom")
    void MyFunction();
};
```

### 源文件 (.cpp)

```cpp
#include "ClassName.h"  // 必须是第一个 include

AClassName::AClassName()
{
    PrimaryActorTick.bCanEverTick = true;
}

void AClassName::MyFunction()
{
    // 实现
}
```

---

## 快速参考

| 快捷键 | 功能 |
|-------|------|
| **Ctrl+Alt+F11** | 打开 Live Coding 控制台 |
| **Ctrl+S** | 保存文件（编译前必须） |

| 编译方式 | 适用场景 | 用户操作 |
|---------|---------|---------|
| 全自动脚本 | 新类/大改动 | 零！ |
| Live Coding | 修改现有 .cpp | Ctrl+Alt+F11 |

---

## 关键原则

1. **新类全自动** - 关闭 → 编译 → 重启，用户只测试
2. **修改现有代码用 Live Coding** - 快速迭代
3. **优先使用 Live Coding** - 效率最高
4. **错误循环修复** - 最多 5 次，AI 自动修复
5. **psutil 依赖** - 脚本需要 psutil 库（用于进程管理）
