#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
UE Auto Compile & Relaunch - 全自动编译并重启
================================================

关闭运行中的 UE 编辑器 → 命令行编译 → 编译成功后自动重启 UE。
用户只需测试，完全自动化。

放置位置: .config/opencode/skills/ue-compile-helper/scripts/auto_compile_check.py
"""

import subprocess
import os
import re
import sys
import time
import psutil
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Tuple


@dataclass
class CompileError:
    file_path: str
    line_number: int
    column: int
    severity: str
    code: str
    message: str

    def to_dict(self) -> dict:
        return asdict(self)

    def __str__(self) -> str:
        return f"{self.file_path}({self.line_number}): {self.severity} {self.code}: {self.message}"


@dataclass
class CompileResult:
    success: bool
    errors: List[CompileError]
    warnings: List[CompileError]
    raw_output: str
    build_time: float

    def to_report(self) -> str:
        lines = []
        if self.success:
            lines.append("✅ 编译成功！无错误。")
        else:
            lines.append(f"❌ 编译失败。{len(self.errors)} 个错误, {len(self.warnings)} 个警告")
            lines.append(f"\n编译耗时: {self.build_time:.1f}s\n")
            for i, err in enumerate(self.errors, 1):
                lines.append(f"错误 {i}: {err}")
            if self.warnings:
                lines.append("\n警告:")
                for i, warn in enumerate(self.warnings[:5], 1):
                    lines.append(f"  警告 {i}: {warn}")
        return "\n".join(lines)


def find_ue_engine() -> Optional[Path]:
    """自动查找 UE 引擎路径"""
    env_path = os.environ.get("UE_ENGINE_PATH")
    if env_path and Path(env_path).exists():
        return Path(env_path)

    candidates = [
        Path("E:/UNREAL"),
        Path("D:/UNREAL"),
        Path("C:/UNREAL"),
        Path(os.environ.get("PROGRAMFILES", "C:/Program Files")) / "Epic Games",
        Path(os.environ.get("ProgramFiles(x86)", "C:/Program Files (x86)")) / "Epic Games",
        Path("E:/Epic Games"),
        Path("D:/Epic Games"),
    ]

    for base in candidates:
        if base.exists():
            versions = sorted(base.glob("UE_*"), reverse=True)
            if versions:
                return versions[0]

    return None


def find_ue_project(start_dir: Optional[Path] = None) -> Optional[Path]:
    """向上查找 .uproject 文件"""
    if start_dir is None:
        start_dir = Path.cwd()

    for parent in [start_dir] + list(start_dir.parents):
        for uproject in parent.glob("*.uproject"):
            return uproject
    return None


def find_ue_editor_process(project_path: Optional[Path] = None) -> Optional[psutil.Process]:
    """查找与项目相关的 UE Editor 进程"""
    project_name = project_path.stem if project_path else ""

    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if 'UnrealEditor.exe' not in proc.name():
                continue
            cmdline = proc.cmdline()
            if project_name and any(project_name in arg for arg in cmdline):
                return proc
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    # 找不到关联项目的进程，找任意 UnrealEditor 进程
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if 'UnrealEditor.exe' in proc.name():
                return proc
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    return None


def close_ue_editor(process: Optional[psutil.Process], wait_timeout: float = 30.0) -> bool:
    """关掉 UE 编辑器，等待 DLL 释放"""
    if process is None:
        return True  # 没在运行

    print(f"关闭 UE 编辑器... (PID: {process.pid})")
    process.terminate()

    deadline = time.time() + wait_timeout
    while time.time() < deadline:
        if not process.is_running():
            print("UE 编辑器已关闭")
            return True
        time.sleep(0.5)

    # 超时后强制关闭
    if process.is_running():
        print("强制关闭 UE 编辑器")
        process.kill()
    return True


def wait_for_dll_unlock(project_path: Path, max_wait: float = 15.0) -> None:
    """等待项目 DLL 文件解锁"""
    dll_path = (
        project_path.parent / "Binaries" / "Win64" /
        f"UnrealEditor-{project_path.stem}.dll"
    )

    if not dll_path.exists():
        return

    deadline = time.time() + max_wait
    while time.time() < deadline:
        try:
            with open(dll_path, 'rb') as f:
                _ = f.read(1)
            return  # 可以读取，文件已解锁
        except PermissionError:
            time.sleep(0.5)
            continue


def compile_project(project_path: Path, engine_path: Optional[Path] = None,
                    module_name: Optional[str] = None) -> CompileResult:
    """执行 UBT 命令行编译"""
    start_time = time.time()

    if engine_path is None:
        engine_path = find_ue_engine()
        if engine_path is None:
            return CompileResult(
                success=False,
                errors=[CompileError("", 0, 0, "error", "", "无法检测 UE 引擎路径")],
                warnings=[], raw_output="", build_time=0
            )

    project_name = project_path.stem
    project_dir = project_path.parent

    build_exe = engine_path / "Engine" / "Build" / "BatchFiles" / "Build.bat"
    target = f"{project_name}Editor"

    cmd = [
        str(build_exe),
        target,
        "Win64",
        "Development",
        f'-Project="{project_path}"',
        "-NoHotReloadFromIDE",
        "-Progress",
    ]

    if module_name:
        cmd.append(f"-Module={module_name}")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            cwd=str(project_dir),
            timeout=600
        )

        build_time = time.time() - start_time
        output = result.stdout + result.stderr

        errors, warnings = _parse_output(output, project_dir)
        is_success = result.returncode == 0 and not any(e.severity == "error" for e in errors)

        return CompileResult(
            success=is_success,
            errors=errors,
            warnings=warnings,
            raw_output=output,
            build_time=build_time
        )

    except subprocess.TimeoutExpired:
        return CompileResult(
            success=False,
            errors=[CompileError("", 0, 0, "error", "", "编译超时（>10分钟）")],
            warnings=[], raw_output="", build_time=600
        )
    except Exception as e:
        return CompileResult(
            success=False,
            errors=[CompileError("", 0, 0, "error", "", f"编译执行失败: {str(e)}")],
            warnings=[],
            raw_output=str(e),
            build_time=time.time() - start_time
        )


def launch_ue_editor(project_path: Path, engine_path: Optional[Path] = None) -> bool:
    """重启 UE 编辑器"""
    project_dir = project_path.parent

    # 通过引擎路径查找编辑器
    if engine_path is None:
        engine_path = find_ue_engine()

    editor_exe = engine_path / "Engine" / "Binaries" / "Win64" / "UnrealEditor.exe"
    if not editor_exe.exists():
        print(f"⚠️ 找不到 UnrealEditor.exe，无法自动重启")
        return False

    print(f"启动 UE 编辑器...")
    cmd = [str(editor_exe), str(project_path)]

    try:
        process = subprocess.Popen(cmd, cwd=str(project_dir))
        print(f"UE 编辑器已启动 (PID: {process.pid})")
        return True
    except Exception as e:
        print(f"⚠️ 启动 UE 失败: {e}")
        return False


def _parse_output(output: str, project_dir: Path) -> Tuple[List[CompileError], List[CompileError]]:
    """解析编译输出"""
    errors = []
    warnings = []

    msvc_pattern = re.compile(
        r'(?P<file>[a-zA-Z]:[\\\w\s.\-:]+[.](?:cpp|h|hpp))\((?P<line>\d+)(?:,(?P<col>\d+))?\)\s*:\s*'
        r'(?P<severity>error|warning)\s+(?P<code>\w+)\s*:\s*'
        r'(?P<message>.+)',
        re.IGNORECASE
    )

    clang_pattern = re.compile(
        r'(?P<file>[a-zA-Z]:[\\\w\s.\-:]+[.](?:cpp|h|hpp)):(?P<line>\d+):(?P<col>\d+):\s*'
        r'(?P<severity>error|warning|note):\s*'
        r'(?P<message>.+)',
        re.IGNORECASE
    )

    for line in output.split('\n'):
        line = line.strip()
        if not line:
            continue

        m = msvc_pattern.search(line)
        if m:
            severity = m.group("severity").lower()
            if severity == "note":
                continue
            err = CompileError(
                file_path=m.group("file").strip(),
                line_number=int(m.group("line")),
                column=int(m.group("col")) if m.group("col") else 0,
                severity=severity,
                code=m.group("code") or "",
                message=m.group("message").strip()
            )
            if severity == "error":
                errors.append(err)
            else:
                warnings.append(err)
            continue

        m = clang_pattern.search(line)
        if m:
            severity = m.group("severity").lower()
            if severity == "note":
                continue
            err = CompileError(
                file_path=m.group("file").strip(),
                line_number=int(m.group("line")),
                column=int(m.group("col")),
                severity=severity,
                code="",
                message=m.group("message").strip()
            )
            if severity == "error":
                errors.append(err)
            else:
                warnings.append(err)

    return errors, warnings


def auto_compile_and_relaunch(
    project_path: Optional[Path] = None,
    engine_path: Optional[Path] = None,
    module_name: Optional[str] = None,
    close_editor: bool = True
) -> CompileResult:
    """
    全自动编译流程：

    1. 检测运行中的 UE 编辑器
    2. 关闭 UE 编辑器（释放 DLL）
    3. 等待 DLL 解锁
    4. 执行 UBT 编译
    5. 编译成功后自动重启 UE

    Args:
        project_path: .uproject 路径，None 自动查找
        engine_path: 引擎路径，None 自动查找
        module_name: 编译模块，None 编译全部
        close_editor: 是否关闭编辑器

    Returns:
        CompileResult
    """
    if project_path is None:
        project_path = find_ue_project()
        if project_path is None:
            result = CompileResult(
                success=False,
                errors=[CompileError("", 0, 0, "error", "", "未找到 UE 项目")],
                warnings=[], raw_output="", build_time=0
            )
            print(result.to_report())
            return result

    print("=" * 60)
    print("UE 全自动编译 & 重启工具")
    print("=" * 60)

    # Step 1: 检测并关闭 UE
    ue_process = find_ue_editor_process(project_path)
    if ue_process and close_editor:
        close_ue_editor(ue_process)
        wait_for_dll_unlock(project_path)
    elif close_editor:
        print("未发现运行中的 UE 编辑器")

    # Step 2: 编译
    print(f"\n开始编译 {project_path.stem}...")
    result = compile_project(project_path, engine_path, module_name)

    # Step 3: 报告
    print(f"\n{result.to_report()}")

    # Step 4: 重启 UE
    if result.success:
        if engine_path is None:
            engine_path = find_ue_engine()
        launch_ue_editor(project_path, engine_path)

    return result


if __name__ == "__main__":
    auto_compile_and_relaunch()
