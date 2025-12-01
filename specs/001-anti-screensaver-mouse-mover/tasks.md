# Tasks: Anti-Screensaver Mouse Mover (Windows)

**Input**: Design documents from `/specs/001-anti-screensaver-mouse-mover/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Platform**: Windows 10/11 only (as specified by user)
**Tests**: Not explicitly requested - implementation tasks only

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

Single desktop application structure:
- Source code: `src/`
- Tests: `tests/`
- Configuration: `config/`
- Documentation: `docs/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and Windows-specific structure

- [X] T001 Create project directory structure (src/core/, src/gui/, src/platform/, tests/, config/, docs/)
- [X] T002 Initialize Python project with pyproject.toml and setup.py for Windows packaging
- [X] T003 [P] Create requirements.txt with PySide6>=6.6.0, pynput>=1.7.6, fasteners>=0.18
- [X] T004 [P] Create requirements-dev.txt with pytest>=7.4.0, pytest-qt>=4.2.0, pytest-cov>=4.1.0
- [X] T005 [P] Create .gitignore for Python project (__pycache__, *.pyc, venv/, dist/, build/, *.egg-info/)
- [X] T006 [P] Create config/default_config.json with default settings (interval_seconds: 30, auto_start: false)
- [X] T007 [P] Create README.md with Windows installation and usage instructions
- [X] T008 [P] Create docs/INSTALL.md with Windows-specific installation steps

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T009 Create base exception classes in src/core/exceptions.py (AntiScreensaverError, ConfigurationError, StateError, EngineError)
- [X] T010 [P] Create data classes and enums in src/core/models.py (RunningState, IconType, Configuration, ApplicationState, MouseMovement)
- [X] T011 [P] Create interface contracts in src/core/contracts.py (IConfigurationManager, IMouseController, IStateManager, IMovementEngine, ITrayIcon, IMainWindow)
- [X] T012 Implement Windows platform detection in src/platform/__init__.py (detect OS, return Windows-specific paths)
- [X] T013 Implement Windows mouse controller in src/platform/windows.py using pynput (move, get_current_position, test_control methods)
- [X] T014 Implement configuration manager in src/core/config.py with Windows paths (%APPDATA%\AntiScreensaver\config.json)
- [X] T015 Implement state manager in src/core/state.py (track running state, movement counts, error counts, state change notifications)
- [X] T016 Implement single-instance lock in src/core/instance_lock.py using fasteners (Windows temp directory lock file)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel ✓ COMPLETE

---

## Phase 3: User Story 1 - Prevent Screen Lock During Remote Meetings (Priority: P0) 🎯 MVP

**Goal**: Enable users to keep their screen unlocked during remote meetings by running periodic micro mouse movements

**Independent Test**: Start application, enable mouse movement with 30-second interval, wait 15 minutes without touching mouse/keyboard, verify screen does not lock

### Implementation for User Story 1

- [ ] T017 [P] [US1] Implement movement engine core in src/core/mouse_mover.py (QTimer-based periodic movements, start/stop methods)
- [ ] T018 [P] [US1] Implement alternating movement pattern in src/core/mouse_mover.py (+1,+1 then -1,-1 pattern)
- [ ] T019 [US1] Integrate movement engine with mouse controller in src/core/mouse_mover.py (execute movements, handle success/failure)
- [ ] T020 [US1] Implement error handling and auto-stop threshold (5 consecutive failures) in src/core/mouse_mover.py
- [ ] T021 [US1] Create minimal main window GUI in src/gui/main_window.py (Start/Stop button using PySide6)
- [ ] T022 [US1] Connect main window Start button to movement engine start() method in src/gui/main_window.py
- [ ] T023 [US1] Connect main window Stop button to movement engine stop() method in src/gui/main_window.py
- [ ] T024 [US1] Implement UI state updates (button text changes, enabled/disabled) in src/gui/main_window.py
- [ ] T025 [US1] Create basic system tray icon in src/gui/tray_icon.py using QSystemTrayIcon
- [ ] T026 [US1] Add tray menu with Start/Stop toggle and Exit options in src/gui/tray_icon.py
- [ ] T027 [US1] Implement tray icon state changes (gray when stopped, green when running) in src/gui/tray_icon.py
- [ ] T028 [US1] Update tray tooltip to show current state and interval in src/gui/tray_icon.py
- [ ] T029 [US1] Create application controller in src/controller.py (coordinate all components, handle startup/shutdown)
- [ ] T030 [US1] Implement main entry point in src/main.py (initialize Qt application, create controller, show UI)
- [ ] T031 [US1] Add minimize to tray functionality when main window is closed in src/gui/main_window.py
- [ ] T032 [US1] Add click on tray icon to restore main window functionality in src/gui/tray_icon.py

**Checkpoint**: At this point, User Story 1 should be fully functional - basic start/stop mouse movement with tray integration

---

## Phase 4: User Story 2 - Monitor Long-Running Processes (Priority: P1)

**Goal**: Allow users to keep monitoring dashboards visible by running from system tray without visible window

**Independent Test**: Start application minimized to tray, enable mouse movement from tray menu, verify tray icon shows running status, confirm screen stays active for 30+ minutes

### Implementation for User Story 2

- [ ] T033 [US2] Add command-line argument --minimized to src/main.py for starting in tray only
- [ ] T034 [US2] Implement startup mode detection in src/main.py (show window or hide to tray based on argument)
- [ ] T035 [US2] Update tray menu to add "Show Window" option in src/gui/tray_icon.py
- [ ] T036 [US2] Implement show window from tray functionality in src/gui/tray_icon.py
- [ ] T037 [US2] Add tray icon tooltip updates with movement count statistics in src/gui/tray_icon.py
- [ ] T038 [US2] Implement last movement timestamp display in tray tooltip in src/gui/tray_icon.py
- [ ] T039 [US2] Add diagnostic information panel in main window (movement count, last movement time, error count) in src/gui/main_window.py
- [ ] T040 [US2] Connect state manager statistics to diagnostic panel updates in src/gui/main_window.py

**Checkpoint**: At this point, User Stories 1 AND 2 should both work - can run headless from tray with status visibility

---

## Phase 5: User Story 3 - Configure Movement Intervals (Priority: P1)

**Goal**: Enable users to customize mouse movement frequency to match their system's idle timeout settings

**Independent Test**: Set interval to 60 seconds via slider, start movement, measure time between movements (should be ~60s ±6s), verify configuration persists after restart

### Implementation for User Story 3

- [ ] T041 [P] [US3] Create interval configuration widget in src/gui/widgets.py (QSlider with range 10-300 seconds)
- [ ] T042 [P] [US3] Add interval value display label (shows current seconds) in src/gui/widgets.py
- [ ] T043 [US3] Integrate interval slider into main window settings section in src/gui/main_window.py
- [ ] T044 [US3] Implement interval change handler in src/controller.py (update movement engine timer interval)
- [ ] T045 [US3] Add real-time interval update (takes effect within 1 second) in src/core/mouse_mover.py
- [ ] T046 [US3] Implement configuration persistence on interval change in src/controller.py (save to config.json)
- [ ] T047 [US3] Load saved interval value on application startup in src/controller.py
- [ ] T048 [US3] Update UI slider to show loaded interval value on startup in src/gui/main_window.py
- [ ] T049 [US3] Add validation warnings for extreme values (<15s or >180s) in src/gui/main_window.py
- [ ] T050 [US3] Update tray tooltip to reflect current interval setting in src/gui/tray_icon.py

**Checkpoint**: All core user stories (1-3) should now be independently functional with full configuration support

---

## Phase 6: User Story 4 - Auto-Start on System Boot (Priority: P2)

**Goal**: Allow users to have the application automatically start when Windows boots

**Independent Test**: Enable auto-start option, restart Windows, verify application starts minimized to tray automatically

### Implementation for User Story 4

- [ ] T051 [P] [US4] Create Windows registry auto-start manager in src/platform/autostart_windows.py (enable/disable/check methods)
- [ ] T052 [P] [US4] Implement registry key path constant (HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run)
- [ ] T053 [US4] Implement enable() method to add registry entry with exe path and --minimized flag in src/platform/autostart_windows.py
- [ ] T054 [US4] Implement disable() method to remove registry entry in src/platform/autostart_windows.py
- [ ] T055 [US4] Implement is_enabled() method to check registry entry existence in src/platform/autostart_windows.py
- [ ] T056 [US4] Add auto-start checkbox widget to main window settings in src/gui/main_window.py
- [ ] T057 [US4] Connect checkbox to auto-start manager enable/disable methods in src/controller.py
- [ ] T058 [US4] Load current auto-start status on startup and update checkbox in src/gui/main_window.py
- [ ] T059 [US4] Persist auto-start preference to config.json in src/controller.py
- [ ] T060 [US4] Add error handling for registry access failures (permission denied) in src/platform/autostart_windows.py
- [ ] T061 [US4] Display user-friendly error message if registry modification fails in src/gui/main_window.py

**Checkpoint**: All user stories should now be independently functional - complete Windows desktop application

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and production readiness

- [ ] T062 [P] Add application icon file (icon.ico) to assets/ directory
- [ ] T063 [P] Integrate application icon in main window and tray icon in src/gui/main_window.py and src/gui/tray_icon.py
- [ ] T064 [P] Create About dialog with version info and license in src/gui/about_dialog.py
- [ ] T065 [P] Add About menu option to tray menu in src/gui/tray_icon.py
- [ ] T066 [P] Implement graceful shutdown (save state, release lock, stop timer) in src/controller.py
- [ ] T067 [P] Add logging configuration in src/core/logging_config.py (file: %APPDATA%\AntiScreensaver\anti-screensaver.log)
- [ ] T068 [P] Add logging statements for key operations (start, stop, config changes, errors) across all modules
- [ ] T069 Add Windows sleep/wake event handling (pause on sleep, resume on wake) in src/platform/windows.py
- [ ] T070 [P] Update README.md with complete usage instructions, screenshots, and troubleshooting
- [ ] T071 [P] Update docs/INSTALL.md with PyInstaller packaging instructions for Windows exe
- [ ] T072 [P] Create build script (build.bat) for creating standalone Windows executable using PyInstaller
- [ ] T073 Test PyInstaller build and verify exe runs on clean Windows system without Python installed
- [ ] T074 [P] Add LICENSE file (choose appropriate license, e.g., MIT)
- [ ] T075 [P] Add version information to application (__version__ in src/__init__.py)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (US1 → US2 → US3 → US4)
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P0)**: Can start after Foundational (Phase 2) - No dependencies on other stories - **MVP Core**
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - Builds on US1 tray integration but independently testable
- **User Story 3 (P1)**: Can start after Foundational (Phase 2) - Adds configuration to US1 but independently testable
- **User Story 4 (P2)**: Can start after Foundational (Phase 2) - Windows-specific, independently testable

### Within Each User Story

- Models before services
- Services before GUI components
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

**Setup Phase (Phase 1)**:
- T003, T004, T005, T006, T007, T008 can all run in parallel

**Foundational Phase (Phase 2)**:
- T010 and T011 can run in parallel (different files)
- Once T010 is done: T013, T014, T015, T016 can run in parallel

**User Story 1 (Phase 3)**:
- T017 and T018 can run in parallel (same file but independent functions)
- T021 and T025 can run in parallel (different files: main_window.py vs tray_icon.py)

**User Story 2 (Phase 4)**:
- T037 and T038 can run in parallel if both editing tray_icon.py carefully
- T039 and T040 can run together

**User Story 3 (Phase 5)**:
- T041 and T042 can run in parallel (same widget file but different components)

**User Story 4 (Phase 6)**:
- T051 and T052 can run in parallel (same file but different components)

**Polish Phase (Phase 7)**:
- T062, T063, T064, T065, T066, T067, T068, T070, T071, T072, T074, T075 can all run in parallel

### Critical Path

The minimum viable path to a working application:

```
T001-T008 (Setup) → T009-T016 (Foundation) → T017-T032 (US1 Core) → T073 (Build Test) → Ready for Use
```

---

## Parallel Example: User Story 1

```bash
# After Foundational phase is complete, these can start together:
Task: "Implement movement engine core in src/core/mouse_mover.py"
Task: "Implement alternating movement pattern in src/core/mouse_mover.py"

# After movement engine is done, these UI components can develop in parallel:
Task: "Create minimal main window GUI in src/gui/main_window.py"
Task: "Create basic system tray icon in src/gui/tray_icon.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only) - Fastest Path to Value

1. Complete Phase 1: Setup (T001-T008) - ~1 hour
2. Complete Phase 2: Foundational (T009-T016) - CRITICAL - ~3-4 hours
3. Complete Phase 3: User Story 1 (T017-T032) - ~5-6 hours
4. **STOP and VALIDATE**: Test User Story 1 independently
   - Can start/stop mouse movement?
   - Does it prevent screen lock?
   - Does tray icon work?
5. Optional: Add minimal polish (T062-T063: icons, T066: graceful shutdown)
6. Deploy/demo if ready - **YOU NOW HAVE A WORKING PRODUCT**

**Total MVP Time Estimate**: ~10-12 hours of development

### Incremental Delivery Strategy

1. **Phase 1 + 2 Complete** → Foundation ready (~4-5 hours)
2. **Add US1** → Test independently → **MVP Release** (~6 hours)
3. **Add US2** → Test independently → **v1.1 Release** (headless mode) (~2 hours)
4. **Add US3** → Test independently → **v1.2 Release** (configurable) (~3 hours)
5. **Add US4** → Test independently → **v1.3 Release** (auto-start) (~3 hours)
6. **Add Polish** → Test system-wide → **v1.5 Production Release** (~4 hours)

Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. **Team completes Setup + Foundational together** (~5 hours)
2. **Once Foundational is done**:
   - Developer A: User Story 1 (T017-T032)
   - Developer B: User Story 3 (T041-T050) - Requires A's engine to be done for integration
   - Developer C: User Story 4 (T051-T061) - Can work independently
3. Developer A completes US1, then starts US2 (T033-T040) which builds on US1
4. Stories integrate and test together

**Team Parallelization Note**: US3 and US4 both depend on US1 being at least partially complete (movement engine and GUI structure), so true parallel work is limited. Best strategy: US1 first, then US2/US3/US4 in parallel.

---

## Windows-Specific Considerations

### Configuration Paths

- **Config file**: `%APPDATA%\AntiScreensaver\config.json`
  - Typically: `C:\Users\<username>\AppData\Roaming\AntiScreensaver\config.json`
- **Log file**: `%APPDATA%\AntiScreensaver\anti-screensaver.log`
- **Lock file**: `%TEMP%\anti-screensaver.lock`
  - Typically: `C:\Users\<username>\AppData\Local\Temp\anti-screensaver.lock`

### Registry Auto-Start

- **Registry Key**: `HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run`
- **Value Name**: `AntiScreensaver`
- **Value Data**: `"C:\Path\To\anti-screensaver.exe" --minimized`

### PyInstaller Build Command

```bash
pyinstaller --onefile --windowed --name anti-screensaver --icon assets/icon.ico src/main.py
```

### Windows Permissions

- No administrator rights required
- User-level registry access (HKEY_CURRENT_USER)
- User-level file system access (%APPDATA%, %TEMP%)
- Mouse control via pynput (no special permissions needed)

### Testing on Windows

- Test on both Windows 10 and Windows 11
- Test with default Windows idle timeout (10 minutes)
- Test with custom idle timeout settings
- Test sleep/wake cycle behavior
- Test registry access on corporate/managed systems (may be restricted)
- Verify no antivirus false positives (pynput mouse control)

---

## Notes

- **[P] tasks** = different files, no dependencies - can run in parallel
- **[Story] label** maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group of related tasks
- Stop at any checkpoint to validate story independently
- **Windows-only**: No Linux/macOS code needed, simplifies platform layer significantly
- **No tests requested**: Focus on implementation only, manual testing via independent test criteria
- **pynput library**: Cross-platform but we're only using Windows functionality
- **Qt/PySide6**: Handles Windows GUI integration (tray, notifications, styling)
- **Avoid**: vague tasks, same file conflicts, cross-story dependencies that break independence

---

## Task Count Summary

- **Phase 1 (Setup)**: 8 tasks
- **Phase 2 (Foundational)**: 8 tasks (BLOCKING)
- **Phase 3 (User Story 1 - MVP)**: 16 tasks
- **Phase 4 (User Story 2)**: 8 tasks
- **Phase 5 (User Story 3)**: 10 tasks
- **Phase 6 (User Story 4)**: 11 tasks
- **Phase 7 (Polish)**: 14 tasks

**Total**: 75 tasks

**MVP Subset** (Phase 1 + 2 + 3): 32 tasks
**Full Feature Set** (Phase 1-6): 61 tasks
**Production Ready** (Phase 1-7): 75 tasks

---

## Validation Checklist

All tasks follow required format:
- ✅ All tasks have checkbox `- [ ]`
- ✅ All tasks have sequential IDs (T001-T075)
- ✅ All tasks marked [P] are truly parallelizable (different files or independent sections)
- ✅ All user story tasks have [Story] labels (US1, US2, US3, US4)
- ✅ All tasks have specific file paths in descriptions
- ✅ Tasks are organized by user story for independent implementation
- ✅ Each user story has independent test criteria
- ✅ Dependencies are clearly documented
- ✅ Parallel opportunities are identified
- ✅ MVP scope is clearly defined (Phase 1-3)
- ✅ Windows-specific adaptations are included throughout
