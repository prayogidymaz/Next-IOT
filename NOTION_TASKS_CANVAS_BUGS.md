# [BUG] Automation Studio Canvas Interactions & Disconnect Line



| Field | Value |

| --- | --- |

| **Notion Database** | Next-IOT Development Tasks |

| **Status** | Done |

| **Priority** | High |

| **Module** | P7 - Next-IOT Dashboard (Automation Studio) |

| **Assignee AI** | Cursor Agent |

| **Last Sync** | 2026-09-16 (2-step click wiring) |



> **Notion:** Task dibuat otomatis via MCP `user-next-iot-notion` ke database **Next-IOT Development Tasks**.

> Update log: `NOTION_UPDATE.md`



---



## Summary Issue



### 1. Multi-Node Connection Failed (Node Ke-3 / Action)



- **Problem:** Port RIGHT milik node Condition tidak memicu draft line baru untuk disambungkan ke node Action ke-3 (`MAVLink ARM`).

- **Root Cause:** State `connectingFromNodeId` tidak ter-reset penuh; tap pada port input terhubung memicu disconnect alih-alih complete connection.

- **Fix:** `resetConnectingState()` + port tap priority (`onTap` before disconnect) + cumulative `addConnection`.



**Implementation:**



- `resetConnectingState()` — `automation_builder_provider.dart`

- Output port enabled untuk Trigger / Condition / Action (multi-chain)

- `PipelinePortWidget._handleTap` — connect wins over disconnect when wiring



---



### 2. Multi-Node Selection & Canvas Deselect



- **Problem:** Klik area kosong canvas tidak melepas seleksi node/edge.

- **Fix:** Background `onTapDown` → `deselectAll()` — `pipeline_canvas.dart`



---



### 3. Disconnect Line Option (Putus Sambungan)



- **Problem:** Garis antar-port tidak bisa dilepas tanpa Clear Canvas.

- **Fix:**

  - Port input terhubung → hover × → disconnect

  - **Edge selection** via hit targets along bezier

  - **Selection Inspector** → tombol **Disconnect**

  - **Delete / Backspace** keyboard shortcut



**Implementation:**



- `selectEdge` / `removeSelectedEdge` / `hitTestEdge` — provider

- `PipelineSelectionInspector` — inspector bar

- Edge highlight in `_EdgePainter`



---



### 4. Port Connector — 2-Step Click Wiring (`TOP/RIGHT/BOTTOM/LEFT`)



- **Problem:** Drag pada port masih memicu node movement & selection box (garis kuning terputus/stuck).

- **Root Cause:** Pointer drag pada port bersaing dengan node pan gesture dan `InteractiveViewer`; overlay opaque menangkap pointer tapi UX drag tetap konflik.

- **Fix (drag + click hybrid):**
  - **Pointer down** port asal → garis preview langsung muncul & ikuti kursor (via `PointerRouter`, tanpa overlay blocking)
  - **Drag release / klik** port tujuan → `completeConnection()` dengan port eksplisit (TOP/RIGHT/BOTTOM/LEFT)
  - **Cancel:** Esc atau klik canvas kosong → `resetConnectingState()`
  - Node lain **tetap bisa digeser** saat wiring (overlay opaque dihapus)
  - Visual: port asal pulse kuning; port tujuan hover highlight hijau
  - Bug fix: `addConnection` tidak lagi override `toPort` yang dipilih user



**Implementation:** `automation_builder_provider.dart`, `pipeline_port_widget.dart`, `pipeline_node_widget.dart`, `pipeline_ports.dart`, `pipeline_canvas.dart`, `automation_builder_screen.dart`



---



## Verification Checklist



- [x] Trigger → Condition → Action (3-node chain) connect via port RIGHT

- [x] Klik canvas kosong → node & edge deselect

- [x] Drag satu node → hanya node itu bergerak

- [x] Hover port input terhubung → ikon × muncul

- [x] Tap port terhubung → edge hilang

- [x] Select edge → Disconnect button + Delete key

- [x] Klik port asal (TOP/RIGHT/BOTTOM/LEFT) → garis preview kuning mengikuti kursor
- [x] Klik port tujuan → edge terbentuk; Esc / klik kosong → cancel wiring
- [x] Port hit target 40×40 px
- [x] `flutter test` → 126+ passed



---



## Key Files



```

apps/dashboard/lib/features/automation/providers/automation_builder_provider.dart

apps/dashboard/lib/features/automation/widgets/pipeline_canvas.dart

apps/dashboard/lib/features/automation/widgets/pipeline_node_widget.dart

apps/dashboard/lib/features/automation/widgets/pipeline_port_widget.dart

apps/dashboard/lib/features/automation/widgets/pipeline_selection_inspector.dart

```



---



## Manual QA Commands



```bash

cd apps/dashboard

flutter test

```



Login dev: `admin@nextiot.com` / `admin123` → Automation Studio (`/studio`).

