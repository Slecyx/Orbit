# Orbit Architecture Diagram

```mermaid
graph TD
    UI[Frontend: GTK4/Adwaita] --> Core[Orbit Core Engine]
    
    subgraph Backend [Rust Core]
        Core --> AM[Adapter Manager]
        AM --> APT[APT Adapter]
        AM --> FP[Flatpak Adapter]
        AM --> SN[Snap Adapter]
        AM --> AI[AppImage Scanner]
    end
    
    APT --> SysAPT[System APT/dpkg]
    FP --> SysFP[Flatpak CLI/Lib]
    SN --> SysSN[Snap CLI/Lib]
    AI --> FS[File System Scanning]
    
    subgraph External
        SysAPT
        SysFP
        SysSN
        FS
    end

    UI -.-> PK[PolicyKit]
    PK --> SysAdmin[Privileged Operations]
```

## Module Interactions

1. **Adapters**: Each adapter implements a common `PackageAdapter` trait.
2. **Adapter Manager**: Polls all adapters to build a unified cache of installed applications.
3. **App Cache**: Stores application metadata to prevent redundant system calls.
4. **UI Thread**: Communicates with the Core via async channels to keep the interface responsive during long-running operations (like updates).
