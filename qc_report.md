# Seismic Data QC Report
_Generated: 2026-05-21T10:47:28.803670Z_
**Total features processed:** 3

---
## Summary
| Metric | Count |
| --- | --- |
| 🟢 High Confidence (≥70%) | 1 |
| 🟡 Moderate Confidence (40–69%) | 2 |
| 🔴 Low Confidence (<40%) | 0 |
| Features with QC Flags | 2 |

---


## Feature `F-001`
**Confidence:** 🟢 HIGH (100.0%)

### Extracted Fields
| Field | Value |
| --- | --- |
| Fault Type | `reverse` |
| Structure Type | ⚠ _missing_ |
| Depth (m) | `3500.0` |
| Depth (raw) | `depth of 3500 m` |
| Strike (°) | `90.0` |
| Dip (°) | `45.0` |
| Dip Direction | ⚠ _missing_ |
| Amplitude | `high amplitude` |
| Frequency | ⚠ _missing_ |
| Reflector Continuity | `continuous` |
| Velocity (m/s) | ⚠ _missing_ |
| Age | `Jurassic` |
| Formation/Horizon | `Jurassic Fulmar Formation` |


---

## Feature `F-002`
**Confidence:** 🟡 MODERATE (62.0%)

### Extracted Fields
| Field | Value |
| --- | --- |
| Fault Type | `normal` |
| Structure Type | ⚠ _missing_ |
| Depth (m) | `548.6` |
| Depth (raw) | `1800 ft` |
| Strike (°) | ⚠ _missing_ |
| Dip (°) | ⚠ _missing_ |
| Dip Direction | ⚠ _missing_ |
| Amplitude | ⚠ _missing_ |
| Frequency | ⚠ _missing_ |
| Reflector Continuity | `discontinuous` |
| Velocity (m/s) | ⚠ _missing_ |
| Age | ⚠ _missing_ |
| Formation/Horizon | `No formation` |

**Missing required fields:** `strike`, `dip`

### QC Flags
- ⚑ `MISSING_DIP`
- ⚑ `MISSING_STRIKE`
- ⚑ `MISSING_AMPLITUDE`

### Recommendations
- Add dip angle and direction for structural analysis.
- Add strike azimuth for fault/structure orientation.
- Include amplitude description for DHI (Direct Hydrocarbon Indicator) analysis.

---

## Feature `F-003`
**Confidence:** 🟡 MODERATE (65.0%)

### Extracted Fields
| Field | Value |
| --- | --- |
| Fault Type | `strike-slip` |
| Structure Type | ⚠ _missing_ |
| Depth (m) | `4200.0` |
| Depth (raw) | `4.2 km depth` |
| Strike (°) | ⚠ _missing_ |
| Dip (°) | ⚠ _missing_ |
| Dip Direction | ⚠ _missing_ |
| Amplitude | `moderate amplitude` |
| Frequency | ⚠ _missing_ |
| Reflector Continuity | `chaotic` |
| Velocity (m/s) | ⚠ _missing_ |
| Age | `Cretaceous` |
| Formation/Horizon | ⚠ _missing_ |

**Missing required fields:** `strike`, `dip`, `formation`

### QC Flags
- ⚑ `MISSING_DIP`
- ⚑ `MISSING_STRIKE`
- ⚑ `MISSING_FORMATION`

### Recommendations
- Add dip angle and direction for structural analysis.
- Add strike azimuth for fault/structure orientation.
- Link feature to a named stratigraphic formation or horizon.

---
