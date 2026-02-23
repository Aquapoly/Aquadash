# Camera Service Refactoring Changelog

## Summary

Completed major refactoring of the camera service installation and architecture to simplify deployment, improve security, and follow standard Unix patterns.

## Changes Made

### 1. Installation Model: Run-from-Source → System Installation

**Previous approach (attempted):**
- Run daemon directly from source directory in user's home
- Symlink `camera-ctl` to PATH

**Issue encountered:**
- SELinux/systemd security policies prevent execution from home directories
- Exit code 203 (EXEC) errors

**Final approach:**
- Install daemon files to `/opt/aquadash-camera/` (standard system location)
- Create wrapper script at `/usr/local/bin/camera-ctl` with restricted permissions
- Service file references installed location

**Benefits:**
- Works with SELinux enforcing mode
- Standard Unix filesystem hierarchy
- Clear separation between source and installed files

### 2. Daemon Lifecycle Management: Hybrid → Pure systemd

**Previous:**
- `camera-ctl shutdown` command to stop daemon
- Mixed responsibility between `camera-ctl` and systemctl

**Current:**
- Removed `SHUTDOWN` command from protocol
- All daemon lifecycle operations use systemctl
- `camera-ctl` only manages cameras (add/remove/list)

**Benefits:**
- Clear separation of concerns
- Leverages systemd features (restart policies, logging, dependencies)
- Standard Linux service management pattern

### 3. Socket Naming: Random → Deterministic

**Previous:**
- Random socket names with symlinks in `current/` directory
- Complex symlink management logic

**Current:**
- Deterministic names based on device path (e.g., `/dev/video0` → `video0.sock`)
- No symlinks needed
- Direct socket discovery via glob pattern

**Benefits:**
- Simpler code
- Easier debugging
- No stale symlink issues

### 4. Security Model: Wrapper-based Access Control

**Implementation:**
- `/usr/local/bin/camera-ctl` wrapper script with `0750 root:host-dev` permissions
- Source `camera-ctl` in `/opt/aquadash-camera/` has normal permissions
- Wrapper enforces group membership requirement

**Benefits:**
- Source files remain editable without permission issues
- Access control enforced at wrapper level
- No git permission tracking problems

### 5. Dependency Management

**Added:**
- Automatic `imageio` installation in `install.sh`
- Checks if dependency exists before installing
- Uses `--break-system-packages` flag for modern pip

**Benefits:**
- One-command installation
- No manual dependency setup required
- Works on systems with externally-managed Python

### 6. Bug Fixes

**Fixed issues:**
1. **SELinux context on `/usr/bin/python3.14`**
   - Had `user_home_t` instead of `bin_t` context
   - Fixed with `restorecon`
   - Documented in README troubleshooting

2. **PosixPath socket binding**
   - `socket.bind()` requires string, not Path object
   - Fixed in both `camera_daemon.py` and `camera.py`
   - Added `str()` conversion

3. **Path calculation in `install.sh`**
   - Incorrect relative path to `backend-container.service`
   - Fixed `DEPLOYMENT_DIR` calculation

4. **Line endings in `camera-ctl`**
   - Windows CRLF causing shebang errors
   - Applied `dos2unix` conversion
   - Fixed shebang to `#!/usr/bin/env python3`

5. **Module import in `camera-ctl`**
   - Couldn't import `camera_commands` when installed
   - Made self-contained by inlining constants
   - Later reverted when switching to installation model

## Files Modified

### Core Daemon Files
- `camera_daemon.py` — Removed sys.path manipulation, fixed socket.bind()
- `camera.py` — Removed random naming, fixed socket.bind()
- `camera_paths.py` — Removed CURRENT_DIR constant
- `camera_commands.py` — Removed SHUTDOWN command
- `camera-ctl` — Removed shutdown subcommand, restored imports

### Installation Scripts
- `install.sh` — Complete rewrite for system installation model
  - Install to `/opt/aquadash-camera/`
  - Create wrapper script
  - Add imageio dependency check
  - Path substitution for service file
- `uninstall.sh` — Updated to match new installation
  - Remove `/opt/aquadash-camera/`
  - Remove wrapper script
  - Clean up user/group

### Service Configuration
- `camera-daemon.service` — Use `__CAMERA_DIR__` placeholder for path substitution

### Backend Integration
- `app/services/camera.py` — Updated to use deterministic socket names
- `tests/test_services_camera.py` — Rewrote to mock `_fetch_frame`
- `tests/conftest.py` — Fixed `set_last_image` fixture

### Documentation
- `README.md` — Comprehensive documentation (new)
- `CHANGELOG.md` — This file (new)

## Testing

### Verified Working
- ✅ Installation via `install.sh`
- ✅ Uninstallation via `uninstall.sh`
- ✅ Daemon starts successfully with systemctl
- ✅ Control socket created at `/run/camera/control.sock`
- ✅ `camera-ctl list` returns empty list (no cameras added yet)
- ✅ Proper permissions on `/run/camera/` directory (0750 root:host-dev)
- ✅ Proper permissions on control socket (0660 root:host-dev)

### Not Yet Tested
- ⏳ Adding actual camera device with `camera-ctl add /dev/video0`
- ⏳ Frame capture from camera socket
- ⏳ Backend container integration
- ⏳ Backend tests with mocked daemon

## Migration Notes

### For Existing Installations

If you previously installed the camera service:

1. **Uninstall old version:**
   ```bash
   sudo systemctl stop camera-daemon.service
   sudo rm -f /usr/local/bin/camera-daemon.py
   sudo rm -f /usr/local/bin/camera-ctl
   sudo rm -rf /usr/local/lib/aquadash-camera
   ```

2. **Install new version:**
   ```bash
   cd backend/deployment/devices/camera
   sudo ./install.sh
   ```

3. **Start daemon:**
   ```bash
   sudo systemctl start camera-daemon.service
   ```

### For Development

- Source files remain in `backend/deployment/devices/camera/`
- Edit source files normally
- Run `sudo ./uninstall.sh && sudo ./install.sh` to apply changes
- No permission issues with source files

## Known Issues

### SELinux Context
On some systems, `/usr/bin/python3.x` may have incorrect SELinux context after Python updates. If daemon fails with exit code 203:
```bash
sudo restorecon -v /usr/bin/python3*
```

### Group Membership
Users must log out and back in after being added to `host-dev` group for permissions to take effect.

## Future Improvements

### Potential Enhancements
1. **Hot-reload:** Detect code changes and auto-restart daemon
2. **Systemd socket activation:** Start daemon on-demand when socket is accessed
3. **Multiple camera support:** Better handling of multiple simultaneous cameras
4. **Frame caching:** Cache frames in daemon to reduce camera access
5. **Configuration file:** Support for daemon configuration (frame rate, resolution, etc.)
6. **Metrics:** Expose prometheus metrics for monitoring
7. **Health checks:** Periodic camera health verification

### Code Quality
1. Add type hints throughout
2. Add unit tests for daemon logic
3. Add integration tests with mock camera devices
4. Add CI/CD pipeline for testing

## Lessons Learned

1. **SELinux matters:** Always check SELinux contexts when systemd services fail with exit code 203
2. **Path objects need conversion:** Socket operations require strings, not Path objects
3. **System locations work better:** `/opt/` is more reliable than home directories for system services
4. **Separation of concerns:** Systemd for lifecycle, custom tools for domain logic
5. **Documentation is essential:** Complex setups need comprehensive docs for troubleshooting
