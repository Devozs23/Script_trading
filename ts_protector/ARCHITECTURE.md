# TS Protector Pro - Architecture Documentation

## Overview

TS Protector Pro follows a modular architecture with clear separation of concerns between UI, business logic, and system integration layers.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         UI Layer                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │            MainWindow (PyQt6)                        │   │
│  │  - Status Display                                    │   │
│  │  - Control Buttons                                   │   │
│  │  - Settings UI                                       │   │
│  │  - Activity Log Display                              │   │
│  └──────────────────────────────────────────────────────┘   │
└───────────────────────────┬─────────────────────────────────┘
                            │ Signals/Slots
┌───────────────────────────▼─────────────────────────────────┐
│                   Application Layer                          │
│  ┌──────────────────────────────────────────────────────┐   │
│  │          TSProtectorApp (main.py)                    │   │
│  │  - Component Integration                             │   │
│  │  - Event Coordination                                │   │
│  │  - State Management                                  │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────┬──────────────┬──────────────┬────────────┬────────┘
          │              │              │            │
┌─────────▼──────┐ ┌────▼──────┐ ┌────▼────┐ ┌────▼─────┐
│  VPNManager    │ │  Process  │ │Settings │ │  Logger  │
│                │ │  Monitor  │ │         │ │          │
│ - connect()    │ │           │ │- load() │ │- log()   │
│ - disconnect() │ │- monitor()│ │- save() │ │- info()  │
│ - status()     │ │           │ │         │ │- error() │
└────────┬───────┘ └─────┬─────┘ └────┬────┘ └──────────┘
         │               │             │
┌────────▼───────────────▼─────────────▼──────────────────────┐
│                    Utilities Layer                           │
│  ┌─────────────────────┐    ┌──────────────────────────┐   │
│  │   NetworkUtils      │    │    SystemUtils           │   │
│  │  - get_ip()         │    │  - check_warp()          │   │
│  │  - test_latency()   │    │  - install_warp()        │   │
│  │  - test_connection()│    │  - registry_ops()        │   │
│  └─────────────────────┘    └──────────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
                            │
┌───────────────────────────▼──────────────────────────────────┐
│                   External Systems                           │
│                                                               │
│  ┌──────────────┐  ┌─────────────┐  ┌──────────────────┐   │
│  │ Cloudflare   │  │  TeamSpeak  │  │  Windows APIs    │   │
│  │ WARP CLI     │  │  Process    │  │  (Registry, etc) │   │
│  └──────────────┘  └─────────────┘  └──────────────────┘   │
└──────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. UI Layer (`ui/`)

#### MainWindow (`main_window.py`)
- **Responsibility**: User interface and user interaction
- **Technology**: PyQt6 widgets
- **Key Features**:
  - Responsive dark-themed UI
  - Signal/slot event system
  - Real-time status updates
  - System tray integration

**Public API**:
```python
class MainWindow(QMainWindow):
    # Signals
    connect_clicked: pyqtSignal
    disconnect_clicked: pyqtSignal
    auto_detect_changed: pyqtSignal(bool)

    # Methods
    def update_connection_status(connected: bool)
    def update_ip_address(ip: str)
    def append_log(message: str, level: str)
```

### 2. Application Layer

#### TSProtectorApp (`main.py`)
- **Responsibility**: Application lifecycle and component orchestration
- **Pattern**: Facade pattern
- **Key Features**:
  - Component initialization
  - Event routing
  - State synchronization
  - Resource cleanup

**Workflow**:
```
1. Initialize all components
2. Setup signal/slot connections
3. Load user settings
4. Start monitoring (if enabled)
5. Handle UI events
6. Cleanup on exit
```

### 3. Core Layer (`core/`)

#### VPNManager (`vpn_manager.py`)
- **Responsibility**: VPN connection management
- **External Dependency**: Cloudflare WARP CLI
- **Pattern**: Adapter pattern (wraps WARP CLI)

**State Machine**:
```
       connect()
  ┌──────────────────┐
  │                  │
  ▼                  │
Disconnected ──────▶ Connected
  ▲                  │
  │                  │
  └──────────────────┘
      disconnect()
```

**Key Methods**:
```python
def connect() -> Tuple[bool, str]
def disconnect() -> Tuple[bool, str]
def get_status() -> str
def is_connected() -> bool
```

#### ProcessMonitor (`process_monitor.py`)
- **Responsibility**: TeamSpeak process detection
- **Technology**: psutil + threading
- **Pattern**: Observer pattern

**Monitoring Loop**:
```
Start → Check processes every N seconds
      ↓
   Is TeamSpeak running?
      ├─ Yes (and wasn't before) → Trigger on_started callback
      ├─ No (and was before) → Trigger on_stopped callback
      └─ No change → Continue
      ↓
   Sleep N seconds → Repeat
```

**Key Methods**:
```python
def start_monitoring() -> bool
def stop_monitoring()
def is_teamspeak_running() -> bool
def set_callbacks(on_started, on_stopped)
```

#### Settings (`settings.py`)
- **Responsibility**: Configuration persistence
- **Storage**: JSON file in AppData
- **Pattern**: Singleton-like behavior

**Configuration Flow**:
```
Load → Merge with defaults → Validate → Use
                                        ↓
User changes → Update in memory → Save to disk
```

**Key Methods**:
```python
def load_settings() -> Dict
def save_settings(data: Dict) -> bool
def get(key: str, default: Any) -> Any
def set(key: str, value: Any, save: bool)
def add_to_startup() -> bool
```

#### ActivityLogger (`logger.py`)
- **Responsibility**: Logging and activity tracking
- **Outputs**: File + UI callback
- **Pattern**: Observer pattern

**Logging Flow**:
```
log(message, level)
  ├─ Format with timestamp
  ├─ Add to in-memory queue (max N items)
  ├─ Write to log file
  └─ Trigger UI callback
```

### 4. Utilities Layer (`utils/`)

#### NetworkUtils (`network.py`)
- **Responsibility**: Network operations
- **Dependencies**: requests library
- **Fault Tolerance**: Multiple service fallbacks

**IP Detection Strategy**:
```
Try service 1 (ipify.org)
  ├─ Success → Return IP
  └─ Fail → Try service 2 (my-ip.io)
      ├─ Success → Return IP
      └─ Fail → Try service 3 (ipapi.co)
          ├─ Success → Return IP
          └─ Fail → Return None
```

**Key Methods**:
```python
def get_current_ip() -> Optional[str]
def test_latency(url: str) -> Optional[int]
def test_connection() -> bool
def get_location_info(ip: str) -> Optional[dict]
```

#### SystemUtils (`system.py`)
- **Responsibility**: OS-level operations
- **Platform**: Windows-specific (with guards)
- **Security**: Admin privilege checks

**Key Methods**:
```python
def check_warp_installed() -> Tuple[bool, Path]
def download_warp_installer() -> Optional[Path]
def install_warp() -> bool
def is_admin() -> bool
```

## Data Flow

### Connection Flow
```
User clicks "Connect"
  ↓
UI emits connect_clicked signal
  ↓
TSProtectorApp.on_connect_vpn()
  ↓
VPNManager.connect()
  ↓
Execute: warp-cli connect
  ↓
Check result
  ├─ Success
  │   ├─ Update UI status
  │   ├─ Log success
  │   └─ Refresh IP
  └─ Failure
      ├─ Show error dialog
      └─ Log error
```

### Auto-Detection Flow
```
ProcessMonitor loop (every 5s)
  ↓
Detect TeamSpeak process
  ↓
State changed?
  ├─ Started
  │   ├─ Call on_teamspeak_started callback
  │   ├─ TSProtectorApp.on_teamspeak_started()
  │   └─ Auto-connect VPN
  └─ Stopped
      ├─ Call on_teamspeak_stopped callback
      ├─ TSProtectorApp.on_teamspeak_stopped()
      └─ Auto-disconnect VPN
```

### Settings Update Flow
```
User changes setting
  ↓
UI emits setting_changed signal
  ↓
TSProtectorApp handler
  ↓
Settings.set(key, value, save=True)
  ↓
Save to config.json
  ↓
Apply setting
  ├─ Auto-detect → Start/stop monitoring
  ├─ Startup → Modify registry
  └─ Other → Update internal state
```

## Threading Model

### Main Thread (UI Thread)
- PyQt6 event loop
- UI updates
- User interactions
- Timer callbacks

### Background Thread
- Process monitoring (ProcessMonitor)
- Runs continuously when enabled
- Sleeps between checks (5 seconds default)

### Synchronization
- **UI Updates**: Use Qt signals (thread-safe)
- **Callbacks**: Emit signals to UI thread
- **No shared mutable state** between threads

## State Management

### Application State
```python
{
    'vpn_connected': bool,
    'teamspeak_running': bool,
    'monitoring_enabled': bool,
    'current_ip': str,
    'last_ping': int
}
```

### State Transitions
- **VPN State**: Managed by VPNManager
- **TeamSpeak State**: Managed by ProcessMonitor
- **UI State**: Managed by MainWindow
- **Settings State**: Managed by Settings

## Error Handling

### Strategy
1. **Defensive Programming**: Validate all inputs
2. **Graceful Degradation**: Continue operation on non-critical errors
3. **User Feedback**: Show clear error messages
4. **Logging**: Log all errors for debugging

### Error Levels
- **Critical**: App cannot function (WARP not installed)
- **Warning**: Feature degraded (IP detection failed)
- **Info**: Normal operation events

## Performance Considerations

### Optimization Techniques
1. **Lazy Loading**: Load components only when needed
2. **Caching**: Cache IP address (30s TTL)
3. **Throttling**: Limit network requests
4. **Async Operations**: Use QTimer for periodic tasks

### Resource Limits
- **Memory**: < 100MB target
- **CPU**: < 1% idle, < 3% active
- **Network**: Minimal (periodic checks only)
- **Disk I/O**: Write-through logging only

## Security

### Threat Model
- **Trusted Environment**: Runs on user's local machine
- **No Remote Attacks**: No network server component
- **Local Privilege Escalation**: Registry access for startup

### Mitigations
1. **Input Validation**: Sanitize all user inputs
2. **Timeout Protection**: All network requests timeout
3. **No Credential Storage**: No passwords or API keys
4. **Least Privilege**: Request admin only when needed

## Testing Strategy

### Unit Tests
- VPNManager connection logic
- ProcessMonitor detection logic
- Settings persistence
- Network utility functions

### Integration Tests
- VPN + Process Monitor interaction
- Settings + UI synchronization
- Full connection workflow

### Manual Testing
- UI responsiveness
- System tray behavior
- Windows startup integration
- Cross-version compatibility

## Deployment

### Build Process
```
1. Install dependencies (requirements.txt)
2. Run PyInstaller with build.spec
3. Test executable on clean Windows VM
4. Package with optional Inno Setup
5. Distribute via GitHub Releases
```

### Distribution Formats
- **Standalone EXE**: Single-file executable (onefile mode)
- **Directory**: Executable + dependencies (onedir mode)
- **Installer**: Inno Setup installer (.exe)

## Future Enhancements

### Planned Architecture Changes
1. **Plugin System**: Allow custom VPN providers
2. **Event Bus**: Decouple components further
3. **Async/Await**: Use Python asyncio for network ops
4. **State Machine**: Formal state machine for VPN states
5. **Dependency Injection**: Better testability

### Scalability
- Support for multiple processes (not just TeamSpeak)
- Multiple VPN connections simultaneously
- Custom routing rules per application

## Dependencies

### Direct Dependencies
```
PyQt6 (6.6.1)          → UI framework
psutil (5.9.8)         → Process monitoring
requests (2.31.0)      → HTTP requests
pywin32 (306)          → Windows APIs
```

### External Dependencies
```
Cloudflare WARP CLI    → VPN service
Windows Registry       → Startup integration
```

## Version History

### v1.0.0 (Current)
- Initial release
- Core functionality complete
- Windows support only

---

**Last Updated**: 2026-01-14
**Author**: Development Team
