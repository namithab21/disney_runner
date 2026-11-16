# Disney: Run Through the Stories

A 3D endless runner game inspired by Subway Surfers, built using Python 3.11 and Modern OpenGL (Core Profile 3.3).

---

## Phase 7: Visual Polish, Character Design & World Environment Enhancement

Phase 7 brings high-tier visual polish, detailed procedural 3D character art, and authentic Disney-themed world scenery across all eight story worlds while maintaining 60 FPS performance on Intel UHD Graphics 620:

### 1. Distinct Character Designs (All 8 Runners)
Each runner character is constructed with distinct procedural 3D anatomy, hairstyles, facial expressions, accessories, and silhouettes:
- **Cinderella:** Blue/silver ball gown corset, ballerina hair bun, blue satin headband with diamond jewel, velvet choker necklace, sparkling translucent glass slippers with delicate high heels.
- **Snow White:** Classic blue bodice with yellow front laces, red/blue slashed puff sleeves, high standing white royal collar, dark bob hair with inward curls, iconic bright red ribbon hair bow.
- **Aladdin:** Open purple vest over bare athletic chest, red sash cummerbund, loose baggy white harem pants gathered at ankles, gold wrist bracers, curled-toe golden Arabian slippers, tilted red fez with gold tassel.
- **Rapunzel:** Lavender corset with criss-cross pink ribbon laces, cascading golden hair with an extra-long thick braid falling down her back, pinned blossom hair flowers.
- **Simba:** Full feline stylized humanoid runner, golden fur, majestic red-brown chest & shoulder mane ruff, perked triangular lion ears with dark inner tufts, black lion nose, claws, and animated tail with tuft.
- **Ariel:** Shimmering purple seashell bra top, emerald scaled fin leggings with back fin flair, voluminous cascading crimson red locks, turquoise starfish hair accessory.
- **Peter Pan:** Jagged forest green tunic, leather belt with gold dagger sheath on hip, pointed green Robin Hood cap with a tall scarlet feather, auburn windblown hair.
- **Anna:** Black Nordic bodice with gold rosemaling embroidery, magenta shoulder capelet with brass clasp, auburn twin braided pigtails with teal bows and iconic white streak.

### 2. Iconic Antagonist Designs (All 8 Villains)
The pursuing villains now have unique 3D silhouettes, garments, and weaponry:
- **Lady Tremaine:** Severe gothic burgundy Victorian gown with black velvet apron panel, tall standing fan collar, towering silver-grey pompadour updo, emerald brooch.
- **Evil Queen:** Majestic floor-length royal purple gown with hanging gold tassel cord, high standing white queen fan collar, black balaclava cowl, tall 5-spire golden crown.
- **Jafar:** Sweeping pitch-black and blood-red sorcerer robes with winged shoulder pads, towering black sultan mitre headdress with oval ruby & gold plume, coiled golden cobra serpent staff.
- **Mother Gothel:** Deep burgundy cowl gown, voluminous cascading dark curls flowing down both shoulders, gold belt buckle.
- **Scar:** Sleek tawny predator body with shaggy black mane draping upper chest, sinister vertical facial scar crossing his left eye, extended black claw fingernails.
- **Ursula:** Curvy black decolletage gown with 6 writhing purple-underbellied tentacles around the base, wild gravity-defying sea-witch white hair, beauty mark mole, golden nautilus shell pendant.
- **Captain Hook:** Scarlet officer coat with gold frog braid closures, white lace cravat, curling black handlebar mustache, wide cavalier hat with purple plume, and a gleaming curved steel hook on his left arm.
- **Prince Hans:** Tailored white military dress jacket with gold fringed epaulets, navy high lapels, mutton chop sideburns, grey cavalry boots.

### 3. Rich World-Specific Environments
Each road segment renders authentic roadside props and geometry:
- **Cinderella:** White marble curbs, royal castle towers with conical roofs and sapphire spires, manicured evergreen trees.
- **Snow White:** Enchanted mossy forest, fallen mossy log bridges across the road corridor, giant red toadstool mushrooms with white warts.
- **Aladdin:** Sun-baked Agrabah sandstone arches, rolling desert sand dunes, date palm trees, striped fabric market awning stalls.
- **Tangled:** Stone castle turrets, glowing wooden lantern poles with yellow hanging festival lanterns, golden foliage trees.
- **Lion King:** African savanna terrain, flat-topped umbrella acacia trees, red-brown rock outcrop koppies, dry savanna grass clumps.
- **Little Mermaid:** Deep ocean bed, giant branching coral reefs (pink, coral, teal), luminous kelp forests, floating air bubbles.
- **Peter Pan:** Neverland jungle vegetation, ancient fantasy trees, pirate rum barrels, treasure chest with golden lock.
- **Frozen:** Snow-covered road banks, snow-laden evergreen conifers, giant crystalline ice spires, frozen battlements.

### 4. Advanced Shaders & Lighting
- **Hemispheric ambient lighting:** Differentiates sky light from warm ground bounce reflection.
- **Blinn-Phong wrap lighting:** Softens terminator shadows for a vibrant animation look.
- **Rim lighting glow:** Edge-silhouette highlights inspired by Disney animated films.
- **Contact ground shadows:** Adds grounding depth under characters and obstacles.
- **HUD drop shadows:** High-contrast legible text with subtle drop shadows and pill badges.

---

## Phase 6: Data-Driven Disney World System & Seamless Transitions

Phase 6 transforms the single-world prototype into a multi-world Disney-inspired endless runner with **eight distinct story worlds**, a centralized `WorldManager`, and a **2-second seamless crossfade transition engine**.

### 1. The Eight Disney Worlds

The game cycles through 8 story worlds in sequence (default 60 seconds each), seamlessly looping from World 8 back to World 1:

| # | World | Runner | Villain | Collectible | Environment Theme | Colors |
|:---|:---|:---|:---|:---|:---|:---|
| **1** | **Cinderella** | Cinderella | Evil Stepmother | Glass Slipper | Royal kingdom & palace | Sapphire blue, silver, gold |
| **2** | **Snow White** | Snow White | Evil Queen | Magic Apple | Enchanted forest | Forest green, crimson, purple |
| **3** | **Aladdin** | Aladdin | Jafar | Magic Lamp | Agrabah desert city | Gold, amber, royal purple |
| **4** | **Tangled** | Rapunzel | Mother Gothel | Sun Symbol | Kingdom & lantern festival | Lavender, violet, yellow |
| **5** | **Lion King** | Simba | Scar | Lion Token | African savanna | Orange, amber, earthy brown |
| **6** | **Little Mermaid** | Ariel | Ursula | Seashell | Underwater kingdom | Turquoise, ocean blue, coral |
| **7** | **Peter Pan** | Peter Pan | Captain Hook | Pixie Dust | Neverland & pirate ship | Emerald green, navy, gold |
| **8** | **Frozen** | Anna | Hans | Snowflake | Ice kingdom & snow | Ice blue, arctic white, silver |

### 2. Architecture: One Reusable World Engine

A data-driven architecture where game logic is decoupled from thematic appearance:

- **`worlds/world_config.py`**: Immutable `WorldConfig` definitions for all 8 worlds (sky, fog, lighting, ground, road, runner costume, villain gown, obstacle theme, collectible geometry).
- **`worlds/world_manager.py`**: Central coordinator tracking the active world, active gameplay countdown timer, transition triggers, and listener callback notifications.
- **`worlds/transition.py`**: Seamless 2-second crossfade system that blends sky, fog, and sunlight colors while displaying an animated title card and white screen-flash at the mid-point handoff.
- **`worlds/road_segment.py` & `track.py`**: Environment meshes rebuild their road colors, sidewalks, ground terrain, and world-themed decorations (forest mushrooms, desert dunes, savanna grass, coral pillars, ice crystals, festival lanterns).
- **`entities/collectible.py`**: 8 procedural 3D collectible meshes (Glass Slipper, Apple, Lamp, Sun, Medallion, Shell, Star, Snowflake) managed through `CollectibleMeshCache`.
- **`entities/obstacle.py`**: World-themed obstacle skins for Ground Barriers, Overhead Barriers, and Full Blockers via `ObstacleMeshCache`.
- **`player/player.py` & `entities/villain.py`**: Runner and villain costumes dynamically adapt their materials on world transition while preserving animations, physics, and chase distance.
- **`ui/hud.py`**: Displays active world title badge, real-time world progress bar, collectible type label, animated introduction banner on transition, and pursuit status.

### 3. Gameplay Continuity Guarantees

During world transitions:
- Movement and running physics are **never paused**.
- Player **does not teleport** and camera does not jerk.
- Overall score, distance, and coin counters **strictly persist**.
- Villain pursuit distance and safe/warning/critical states **remain intact**.

---

## Phase 5: Villain Chase System

Phase 5 introduces a full 3D villain — **Lady Tremaine (the Evil Stepmother)** — who actively pursues Cinderella throughout gameplay with a dynamic proximity-based chase engine and a 2D HUD chase meter.

### 1. Villain Character (Evil Stepmother)

A fully procedural low-poly 3D humanoid villain with:

| Body Part | Description |
|:---|:---|
| **Gown** | Flared gothic Victorian skirt — deep burgundy with black velvet tabard apron and gold hem band |
| **Torso** | Aristocratic corset bodice with high standing fan-collar and emerald throat brooch |
| **Head** | Pale severe complexion, dark brow, crimson lips, towering silver-grey pompadour hairdo |
| **Arms** | Long burgundy sleeves with velvet cuffs and pale grasping hands that reach forward |

**Animation:** Independent procedural running cycle. Reaching arm angle scales aggressively from $-35^\circ$ (safe distance) to $-75^\circ$ (critical predatory lunge), with torso forward lean and skirt sway.

### 2. Chase Distance System

The villain always trails the player at a dynamic distance $D \in [0.8, 3.2]$ units:

| State | Distance | HUD Color | Behavior |
|:---|:---|:---|:---|
| **SAFE** | $D > 2.0$ | 🟢 Green | Player runs cleanly; villain gradually falls further behind |
| **WARNING** | $1.4 < D \le 2.0$ | 🟡 Yellow | Villain is closing in; player should collect coins or avoid mistakes |
| **CRITICAL** | $0.8 < D \le 1.4$ | 🔴 Red | Villain is right behind; one more mistake triggers capture |
| **CAUGHT** | $D \le 0.8$ | — | Game Over: "CAUGHT BY EVIL STEPMOTHER!" |

**Clean running recovery:** $+0.16$ units/sec when no mistakes are made.  
**Stumble penalty:** $-0.75$ units when player clips a Ground Barrier or Overhead Barrier (0.75s debounce).  
**Fatal crash:** Crashing into a Full Blocker instantly triggers capture.  
**Collectible bonus:** $+0.05$ units per coin collected.

### 3. Visual Positioning

- Villain trails the player at $Z = D$ behind Cinderella (Z = 0).
- Lateral offset of $X = 0.78$ units prevents visual overlap — Lady Tremaine menacingly flanks over Cinderella's right shoulder.
- Villain tracks the player's current lane with smooth exponential follow ($6.5$ units/sec).
- Camera at $[0, 3.8, 7.6]$ with FOV $55^\circ$ keeps villain fully in-frustum at all distances.

### 4. 2D HUD Chase Proximity Meter

A dynamic progress bar centered below the Score badge:

- Fills from green → yellow → red as villain closes in.
- Displays current state label (PURSUIT: SAFE / WARNING! / CRITICAL!) and numeric distance.
- Game Over overlay shows reason: `CAUGHT BY EVIL STEPMOTHER!` or `CRASHED INTO FULL BLOCKER!`.

---

## Phase 4: Obstacles, Collectibles, Collision System & Continuous Spawning

The runner is a fully playable game featuring interactive hazards, magical collectibles, precise AABB collision detection, scoring progression, an in-game HUD, and a distance-synchronized continuous spawning engine:

1. **Three Distinct Obstacle Types:**
   - **Ground Barrier:** Low hurdle obstacle ($Y \in [0.0, 0.65]$). Player must **jump** over it.
   - **Overhead Barrier:** Elevated clearance archway ($Y \in [1.02, 2.30]$). Player must **slide** underneath it.
   - **Full Lane Blocker:** High stacked crate obstacle ($Y \in [0.0, 2.40]$) occupying the full lane. Player must **switch lanes** to dodge.

2. **Continuous Distance-Synchronized Spawning:**
   - Spawns upcoming obstacle rows and coin trails at a constant horizon ($Z = -180.0$).
   - Wave generation is tied directly to the player's cumulative distance traveled, eliminating coordinate freezing bugs and guaranteeing infinite, uninterrupted gameplay.
   - Enforces fair play: never blocks all 3 lanes; at least one lane is guaranteed safe and passable in every wave.
   - Objects passing behind the player ($Z > 15.0$) are pruned from memory to preserve high performance.

3. **Magical Collectibles:**
   - Shimmering 3D faceted gold Disney coins/tokens with diamond-sheen highlights.
   - Continuous spinning ($180^\circ/\text{sec}$) and floating vertical bobbing.
   - Spawns in straight trails along open lanes and in rainbow arcs leaping over ground barriers.
   - Grants $+50$ points upon pickup and increments the collectible counter.

4. **Precision 3D Collision Detection:**
   - Evaluates 3D Axis-Aligned Bounding Box (AABB) intersections.
   - Dynamic player collision height: adjusts from $1.85$ (standing/jumping) to $0.85$ (sliding).
   - Jumping over ground barriers clears with feet at $Y > 0.70$.
   - Sliding under overhead barriers clears with top of body at $Y \le 0.85$.
   - Hitting any obstacle halts movement and triggers the Game Over screen.

5. **Scoring & Progressive Difficulty:**
   - Continuous distance tracking ($1$ point per meter).
   - Speed starts at $22.0$ units/sec and gradually accelerates with distance (up to $+10.0$ units/sec).
   - High score tracking preserved across attempts.

6. **In-Game 2D Heads-Up Display (HUD):**
   - High-performance 2D screen-space texture overlay rendered with modern OpenGL alpha blending.
   - Displays real-time **Score**, **Distance**, **Coins Collected**, and **Speed**.
   - Features a Game Over modal with score breakdown and instant restart prompt (`[SPACE]` or `[R]`).
   - Built-in real-time spawning diagnostics overlay toggled with **`[F3]`**.

---

## Controls

| Action | Primary Key | Secondary Key | In-Game Mechanics |
| :--- | :--- | :--- | :--- |
| **Move Left** | **`[A]`** | **`[Left Arrow]`** | Switch left one lane (avoids blockers) |
| **Move Right** | **`[D]`** | **`[Right Arrow]`** | Switch right one lane (avoids blockers) |
| **Jump** | **`[W]`** | **`[Up Arrow]`** / **`[Space]`** | Leap over **Ground Barriers** |
| **Slide** | **`[S]`** | **`[Down Arrow]`** | Duck under **Overhead Barriers** |
| **Toggle Debug** | **`[F3]`** | — | Show/hide spawning health & chase diagnostics |
| **Restart** | **`[Space]`** | **`[R]`** | Instantly restart game after Game Over |
| **Exit** | **`[ESC]`** | — | Clean shutdown & GPU resource deallocation |

---

## Directory Architecture

```
disney_runner/
├── assets/
│   ├── audio/                  # Sound effects and world music (future phases)
│   ├── models/                 # 3D models and geometry
│   ├── shaders/                # Modern GLSL 3.30 shaders
│   │   ├── cube_vertex.glsl    # 3D World vertex shader (MVP transformation & normal matrix)
│   │   ├── cube_fragment.glsl  # 3D World fragment shader (Blinn-Phong + distance fog)
│   │   ├── hud_vertex.glsl     # 2D Screen-space HUD vertex shader
│   │   └── hud_fragment.glsl   # 2D Screen-space HUD fragment shader
│   └── textures/               # World textures and atlas maps (future phases)
├── config/
│   ├── __init__.py
│   └── settings.py             # Road, camera, player, villain chase, and game configurations
├── engine/
│   ├── __init__.py
│   ├── camera.py               # 3D third-person camera with smooth follow
│   ├── mesh.py                 # VAO, VBO, and EBO GPU buffer abstraction
│   ├── renderer.py             # Modern OpenGL pipeline state, depth testing, clear, draw passes
│   ├── shader.py               # Shader program compilation, linking, and uniform management
│   └── window.py               # GLFW window lifecycle, delta timing, resize callbacks
├── entities/
│   ├── __init__.py
│   ├── collectible.py          # 3D rotating gold coin entity & procedural mesh
│   ├── cube.py                 # Phase 1 3D cube entity (preserved)
│   ├── obstacle.py             # GroundBarrier, OverheadBarrier, FullBlocker entities & meshes
│   ├── scenery.py              # Procedural geometry for trees, guardrails, boxes, quads
│   └── villain.py              # Evil Stepmother 3D humanoid entity, mesh & animation
├── player/
│   ├── __init__.py
│   ├── animation.py            # Procedural joint animation & state blending
│   ├── movement.py             # Three-lane movement, jump physics, slide timing
│   └── player.py               # 3D humanoid character mesh assembly & kinematics
├── systems/
│   ├── __init__.py
│   ├── chase.py                # ChaseManager: villain proximity states & penalty/recovery logic
│   ├── collision.py            # 3D AABB collision detection system
│   ├── scoring.py              # Distance, score bonus, progressive speed scaling & game-over reason
│   └── spawning.py             # Continuous distance-based spawning manager
├── ui/
│   ├── __init__.py
│   └── hud.py                  # In-game HUD, Chase Proximity Meter & Game Over overlay
├── worlds/
│   ├── __init__.py
│   ├── road_segment.py         # Modular 3-lane road segment entity
│   └── track.py                # Endless track manager with gapless segment recycling
├── main.py                     # Application entry point & game loop (Phase 5)
├── test_chase_system.py        # Phase 5 villain chase verification suite (9 tests)
├── test_full_pipeline_120s.py  # 120-second continuous simulation & stress test
├── test_spawning_120s.py       # Spawning manager 120-second stress test
├── requirements.txt            # Project dependencies
└── README.md                   # Project documentation & run instructions
```

---

## Running the Project

### Interactive Mode
```powershell
.\venv\Scripts\python.exe main.py
```

### Automated Verification Modes
```powershell
# Run Phase 6 multi-world 16-transition test suite (all 8 worlds x 2 cycles):
.\venv\Scripts\python.exe test_world_system.py

# Run Phase 5 villain chase test suite (9 tests):
.\venv\Scripts\python.exe test_chase_system.py

# Run 120-second continuous OpenGL pipeline & spawning test:
.\venv\Scripts\python.exe test_full_pipeline_120s.py

# Run 120-second spawning stress test:
.\venv\Scripts\python.exe test_spawning_120s.py
```
