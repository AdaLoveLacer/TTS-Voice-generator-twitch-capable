## 🎙️ Speakerbot Multi-Engine System - Arquitetura Completa

### Visão Geral do Sistema

```
┌─────────────────────────────────────────────────────────────────────┐
│                         FRONTEND (web_ui.html)                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────────────────────────────────────────────────┐     │
│  │ Form: Synthesize Tab                                     │     │
│  ├──────────────────────────────────────────────────────────┤     │
│  │  Text Input                                              │     │
│  │  Language Select                                         │     │
│  │  Voice Select                                            │     │
│  │  ┌────────────────────────────────────────────────────┐ │     │
│  │  │ 🎤 Motor TTS: [XTTS v2 ▼]                         │ │     │
│  │  │ Description: ⭐ XTTS v2: Máxima qualidade...      │ │     │
│  │  │ Status: ⭐ XTTS v2 (Alta Qualidade)              │ │     │
│  │  └────────────────────────────────────────────────────┘ │     │
│  │  Speed, Temperature, Top-K, Top-P, Length-Scale        │     │
│  │  [Sintetizar] button                                    │     │
│  └──────────────────────────────────────────────────────────┘     │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────┐     │
│  │ JavaScript Functions                                     │     │
│  ├──────────────────────────────────────────────────────────┤     │
│  │                                                          │     │
│  │  synthesize(event) {                                    │     │
│  │    ✅ const engine = tts-engine.value                   │     │
│  │    ✅ formData.append('engine', engine)                 │     │
│  │    → POST /v1/synthesize                                │     │
│  │  }                                                       │     │
│  │                                                          │     │
│  │  cloneVoice(event) {                                    │     │
│  │    ✅ const engine = tts-engine.value                   │     │
│  │    ✅ formData.append('engine', engine)                 │     │
│  │    → POST /v1/clone-voice                               │     │
│  │  }                                                       │     │
│  │                                                          │     │
│  │  localStorage Management:                               │     │
│  │    ✅ saveEngineSelection()  - Save to localStorage     │     │
│  │    ✅ loadEngineSelection()  - Load from localStorage   │     │
│  │    ✅ updateEngineDescription() - Update UI             │     │
│  │    ✅ setupEngineDescriptionListener() - Event handler  │     │
│  │                                                          │     │
│  └──────────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────────┘
                                ↓
                    HTTP POST with FormData
                    (including engine param)
                                ↓
┌─────────────────────────────────────────────────────────────────────┐
│                      BACKEND (main.py)                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Routes:                                                            │
│  ┌────────────────────────────────────────────────────────┐        │
│  │ POST /v1/synthesize                                   │        │
│  │   engine: str = Form(DEFAULT_ENGINE)  ✅              │        │
│  │   → _do_synthesis(engine=engine)                      │        │
│  └────────────────────────────────────────────────────────┘        │
│                                                                     │
│  ┌────────────────────────────────────────────────────────┐        │
│  │ POST /v1/clone-voice                                  │        │
│  │   engine: str = Form(DEFAULT_ENGINE)  ✅              │        │
│  │   → _do_synthesis(engine=engine)                      │        │
│  └────────────────────────────────────────────────────────┘        │
│                                                                     │
│  ┌────────────────────────────────────────────────────────┐        │
│  │ GET /v1/engines                                       │        │
│  │   → Returns all available engines with specs          │        │
│  │   {"engines": {"xtts-v2": {...}, "stylets2": {...}}} │        │
│  └────────────────────────────────────────────────────────┘        │
│                                                                     │
│  Engine Registry (Lines 78-100):                                   │
│  ┌────────────────────────────────────────────────────────┐        │
│  │ ENGINES = {                                            │        │
│  │   "xtts-v2": XTTSv2Engine,      ✅ High Quality       │        │
│  │   "stylets2": StyleTTS2Engine   ✅ Fast (2-3x)        │        │
│  │ }                                                       │        │
│  │                                                         │        │
│  │ DEFAULT_ENGINE = "xtts-v2"                             │        │
│  │ active_engines = {}  # Lazy initialization             │        │
│  │ monitor_selected_engine = DEFAULT_ENGINE               │        │
│  └────────────────────────────────────────────────────────┘        │
│                                                                     │
│  _do_synthesis() function:                                         │
│  ┌────────────────────────────────────────────────────────┐        │
│  │ def _do_synthesis(text, language, voice, engine):     │        │
│  │   ✅ if engine not in ENGINES:                        │        │
│  │       raise HTTPException(400, "Invalid engine")      │        │
│  │                                                         │        │
│  │   active_engine = get_active_engine(engine)           │        │
│  │   audio = active_engine.synthesize(...)               │        │
│  │   return audio                                         │        │
│  └────────────────────────────────────────────────────────┘        │
│                                                                     │
│  Engine Classes:                                                    │
│  ┌─────────────────────────────┬─────────────────────────┐        │
│  │     XTTS v2 Engine          │  StyleTTS2 Engine       │        │
│  ├─────────────────────────────┼─────────────────────────┤        │
│  │ Quality: ⭐ High            │ Quality: ⭐ Good        │        │
│  │ Speed: 15-20 seconds        │ Speed: 5-7 seconds      │        │
│  │ Languages: 16               │ Languages: 11           │        │
│  │ VRAM: ~6GB                  │ VRAM: ~2GB              │        │
│  │ Default: Yes                │ Default: No             │        │
│  └─────────────────────────────┴─────────────────────────┘        │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
                                ↓
                    Audio Stream (WAV format)
                                ↓
                   Browser Audio Player/Download
```

### Fluxo de Dados: Síntese com Engine Selection

```
User selects engine in dropdown
         ↓
Engine selector stores value
         ↓
User clicks "Sintetizar"
         ↓
synthesize() function runs
         ↓
const engine = document.getElementById('tts-engine').value
         ↓
formData.append('engine', engine)
         ↓
POST /v1/synthesize with engine parameter
         ↓
Backend receives engine in Form parameter
         ↓
_do_synthesis() validates engine in ENGINES registry
         ↓
get_active_engine(engine) initializes/retrieves engine
         ↓
Engine synthesizes text with selected model
         ↓
Returns audio stream (WAV)
         ↓
Frontend receives audio
         ↓
Plays in audio element or allows download
         ↓
Saves engine selection to localStorage
         ↓
Next page visit: restored from localStorage
```

### localStorage Keys

```
┌─────────────────────────────────────────────┐
│ Browser LocalStorage (Persistent State)    │
├─────────────────────────────────────────────┤
│                                             │
│ speakerbot_synthesis_config                │
│   └─ Text, language, voice settings        │
│      Speed, temperature, top-k, etc.       │
│                                             │
│ speakerbot_clone_config                    │
│   └─ Clone voice settings                  │
│      Language, speed, temperature, etc.    │
│                                             │
│ speakerbot_tts_engine  ✅ NEW             │
│   └─ Current engine selection              │
│      Values: "xtts-v2" or "stylets2"      │
│      Default: "xtts-v2"                    │
│      Restored on page load                 │
│                                             │
└─────────────────────────────────────────────┘
```

### Event Listeners

```
┌──────────────────────────────────────────────────┐
│ DOMContentLoaded Event                          │
├──────────────────────────────────────────────────┤
│ 1. loadConfig()                                 │
│ 2. loadCloneConfig()                            │
│ 3. updateConfigIndicator()                      │
│ 4. initCustomPresets()                          │
│ 5. ✅ loadEngineSelection()           [NEW]     │
│ 6. ✅ updateEngineDescription()       [NEW]     │
│ 7. ✅ setupEngineDescriptionListener()[NEW]     │
└──────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────┐
│ Document 'change' Event                         │
├──────────────────────────────────────────────────┤
│ Triggers on any form input change:              │
│   • saveConfig()                                │
│   • saveCloneConfig()                           │
│   • ✅ if (event.target.id === 'tts-engine')   │
│       saveEngineSelection()           [NEW]     │
└──────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────┐
│ Engine Select 'change' Event               [NEW] │
├──────────────────────────────────────────────────┤
│ Triggers on #tts-engine selection change:       │
│   • updateEngineDescription()                   │
│   • saveEngineSelection()                       │
└──────────────────────────────────────────────────┘
```

### Engine Specifications

```
┌─────────────────────────────────┬───────────────────────────────┐
│ XTTS v2 (Default)               │ StyleTTS2 (Fast)              │
├─────────────────────────────────┼───────────────────────────────┤
│ Quality: ⭐⭐⭐⭐⭐            │ Quality: ⭐⭐⭐⭐             │
│ Speed: 15-20 seconds            │ Speed: 5-7 seconds (2-3x)     │
│ Languages: 16                   │ Languages: 11                 │
│ VRAM Required: ~6GB             │ VRAM Required: ~2GB           │
│ Memory Efficient: No             │ Memory Efficient: Yes         │
│ API Key Required: No             │ API Key Required: No          │
│ Local Only: Yes                 │ Local Only: Yes               │
│ Cloning Support: Yes             │ Cloning Support: Limited      │
│ Best For: Production, Quality    │ Best For: Testing, Speed      │
│                                 │                               │
│ Use Case: Official deployments  │ Use Case: Demo, testing       │
│           High-quality content  │           Fast iterations     │
│           Premium services      │           Resource limited    │
└─────────────────────────────────┴───────────────────────────────┘
```

### Files Changed Summary

```
web_ui.html (3435+ lines)
├── HTML Changes
│   └── Engine Selector (line ~650)
│       └── Select element with XTTS v2 / StyleTTS2 options
│       └── Description div (#engine-description)
│       └── Status div (#engine-status)
│
├── JavaScript Function Updates
│   ├── synthesize() (line ~1711)
│   │   ├── Extract: const engine = document.getElementById('tts-engine').value
│   │   └── Append: formData.append('engine', engine)
│   │
│   ├── cloneVoice() (line ~1765)
│   │   ├── Extract: const engine = document.getElementById('tts-engine').value
│   │   └── Append: formData.append('engine', engine)
│   │
│   └── New Functions (line ~1358-1548)
│       ├── saveEngineSelection()
│       ├── loadEngineSelection()
│       ├── updateEngineDescription()  ✅ NEW
│       └── setupEngineDescriptionListener()  ✅ NEW
│
├── localStorage (line ~1361)
│   └── ENGINE_STORAGE_KEY = 'speakerbot_tts_engine'  ✅ NEW
│
├── Initialization (line ~1550)
│   ├── loadEngineSelection()  ✅ NEW
│   ├── updateEngineDescription()  ✅ NEW
│   └── setupEngineDescriptionListener()  ✅ NEW
│
└── Cleanup (line ~1510)
    └── localStorage.removeItem(ENGINE_STORAGE_KEY)  ✅ NEW
```

### Testing Hierarchy

```
Level 1: Unit Tests
├── Engine selector renders
├── localStorage save/load
├── Function syntax validation
└── Event listeners attached

Level 2: Integration Tests
├── Frontend can select engine
├── Backend receives engine parameter
├── synthesize endpoint accepts engine
├── clone-voice endpoint accepts engine
└── /v1/engines returns both engines

Level 3: End-to-End Tests
├── Select XTTS v2 → synthesize → get audio
├── Select StyleTTS2 → synthesize → get audio
├── Select engine → reload page → engine restored
└── Compare audio quality between engines

Level 4: Performance Tests
├── XTTS v2: 15-20s synthesis time
├── StyleTTS2: 5-7s synthesis time
├── Memory usage comparison
└── GPU utilization comparison
```

---

**Última Atualização:** 29 de Novembro, 2025
**Status:** ✅ Arquitetura Completa
**Próxima Fase:** Execução de Testes (Phase 4.2)
