# Unreal-skill

UE Compile Helper
Unreal Engine C++ Automated Compile & Fix Tool - Let AI Agents intelligently choose the optimal compilation path. No more pointless waiting.
License: MIT (LICENSE)
Python (https://python.org)
Platform (https://microsoft.com/windows)

---
Why This Tool Exists
When you use AI Agents to write UE C++ code, you hit a major bottleneck: AI doesn't understand Unreal Engine architecture.
After writing code, AI always chooses the safest way to verify compilation — close the editor, full rebuild, restart the project. Even if you only changed a function parameter, it takes 30-60 seconds.
But here's what actually works:
Change Type	Compilation Method
New class / new file	Full UBT compile + auto restart
Modify existing .cpp	Live Coding hot reload
That's a 20x efficiency gap.

---
Core Idea: Black Box Testing
Let AI perform a black box test on every script it generates — automatically verify if the code compiles, but always choose the lowest-cost verification path.
> Use Live Coding whenever possible. Use full compile only when necessary. Automate everything, require zero user intervention.
---

How It Works
🤖 Smart Change Detection
- New class / new file → Full automatic UBT compile + auto restart UE
- Modify existing .cpp → Prompt user to use Live Coding (Ctrl+Alt+F11)
🔧 Full Automatic Workflow (For New Classes)
AI writes code → Detect change type → Close UE → UBT compile →
    ├─ Success → Auto restart UE → User tests
    └─ Failure → Parse errors → Auto fix → Recompile (up to 5 times
    
🐞 Smart Error Resolution
Automatically handles common UE compilation errors:
Error Code	Cause	Auto Fix
C2065	Undeclared identifier	Add missing #include
C2011	Redefinition	Add #pragma once
C2660	Function signature mismatch	Align .h and .cpp
C2653	Not a class or namespace	Fix spelling or include
C2504	Base class undefined	Add base class header

---
Quick Start
Install Dependency
pip install psutil
Usage
Method 1: Command Line (Recommended)
Run in your UE project directory:
python "path/to/ue-compile-helper/scripts/auto_compile_check.py"
Method 2: Specify File Path
python "path/to/ue-compile-helper/scripts/auto_compile_check.py" "MyProject/Source/MyActor.cpp"
Daily Development Best Practices
1. Writing a new class → AI generates code → Auto triggers full compile → Auto restarts UE → You test immediately
2. Modifying existing code → AI changes .cpp → Save file → Press Ctrl+Alt+F11 → Live Coding in seconds
---

Features
✅ Auto engine detection - Finds UE engine path and project files automatically  
✅ Process management - Gracefully closes/restarts UE editor, waits for DLL release  
✅ UBT integration - Directly calls Unreal Build Tool command line  
✅ Error parsing - Extracts MSVC/Clang compilation errors precisely  
✅ Auto repair ready - AI can fix code based on error reports  
✅ Cross-version - Supports UE 4.x and UE 5.x
---

Output Example
❌ Compilation failed. 3 errors, 1 warning
Build time: 12.5s
Error 1: MyProject/Source/MyActor.h(45): error C2065: 'UObject': undeclared identifier
Error 2: MyProject/Source/MyActor.cpp(12): error C2011: 'AMyActor': 'class' type redefinition
Error 3: MyProject/Source/MyActor.cpp(67): error C2660: 'AMyActor::BeginPlay': function does not match declaration
---

Philosophy
> If you use AI to write code, let AI take responsibility for its output.
Not just generating code and walking away — but completing the full delivery loop: Write → Verify → Fix → Deliver working results.
---
Compatibility
- OS: Windows (UE's officially supported platform)
- Unreal Engine: 4.26+ / 5.0+
- Python: 3.7+
---

Contributing
Issues and Pull Requests are welcome! If you encounter problems or have new error types to support, please open an issue.
---
Let UE C++ development return to its efficient essence. No more pointless waiting.
