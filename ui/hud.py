"""
hud.py - Modern 2D Heads-Up Display (HUD) and World Transition Overlay.
Phase 7 Polish: Enhanced typography hierarchy, subtle drop shadows, metallic rim badges,
animated world transition banners, and glowing pursuit danger alerts.
"""

from typing import Tuple, Optional, Any
import ctypes
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from OpenGL.GL import (
    glGenTextures, glBindTexture, glTexImage2D, glTexParameteri,
    glTexSubImage2D, glDeleteTextures, glActiveTexture,
    glGenVertexArrays, glBindVertexArray, glDeleteVertexArrays,
    glGenBuffers, glBindBuffer, glBufferData, glDeleteBuffers,
    glEnableVertexAttribArray, glVertexAttribPointer,
    glDrawElements, glEnable, glDisable, glBlendFunc,
    GL_TEXTURE_2D, GL_TEXTURE0, GL_RGBA, GL_UNSIGNED_BYTE,
    GL_LINEAR, GL_CLAMP_TO_EDGE, GL_TEXTURE_MIN_FILTER, GL_TEXTURE_MAG_FILTER,
    GL_TEXTURE_WRAP_S, GL_TEXTURE_WRAP_T,
    GL_ARRAY_BUFFER, GL_ELEMENT_ARRAY_BUFFER, GL_STATIC_DRAW,
    GL_FLOAT, GL_UNSIGNED_INT, GL_TRIANGLES,
    GL_BLEND, GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA, GL_DEPTH_TEST
)
from config import settings
from engine.shader import ShaderProgram
from systems.scoring import ScoreManager


class HUD:
    """Modern 2D HUD, World Introduction Banner, and Overlay Renderer."""

    def __init__(self, width: int = settings.WINDOW_WIDTH, height: int = settings.WINDOW_HEIGHT):
        self.width = width
        self.height = height

        # Typography fonts
        try:
            self.font_banner = ImageFont.truetype("arialbd.ttf", 36)
            self.font_title = ImageFont.truetype("arialbd.ttf", 46)
            self.font_header = ImageFont.truetype("arialbd.ttf", 24)
            self.font_body = ImageFont.truetype("arialbd.ttf", 18)
            self.font_small = ImageFont.truetype("arial.ttf", 14)
        except Exception:
            try:
                self.font_banner = ImageFont.truetype("arial.ttf", 34)
                self.font_title = ImageFont.truetype("arial.ttf", 44)
                self.font_header = ImageFont.truetype("arial.ttf", 22)
                self.font_body = ImageFont.truetype("arial.ttf", 16)
                self.font_small = ImageFont.truetype("arial.ttf", 13)
            except Exception:
                self.font_banner = ImageFont.load_default()
                self.font_title = ImageFont.load_default()
                self.font_header = ImageFont.load_default()
                self.font_body = ImageFont.load_default()
                self.font_small = ImageFont.load_default()

        # Compile 2D Screen-space Shader
        vert_path = settings.SHADERS_DIR / "hud_vertex.glsl"
        frag_path = settings.SHADERS_DIR / "hud_fragment.glsl"
        self.shader = ShaderProgram(vert_path, frag_path)

        # Full-Screen Orthographic Quad (NDC coordinates)
        quad_vertices = np.array([
            -1.0, -1.0,   0.0, 1.0,   # Bottom-Left
             1.0, -1.0,   1.0, 1.0,   # Bottom-Right
             1.0,  1.0,   1.0, 0.0,   # Top-Right
            -1.0,  1.0,   0.0, 0.0,   # Top-Left
        ], dtype=np.float32)

        quad_indices = np.array([
            0, 1, 2,
            2, 3, 0
        ], dtype=np.uint32)

        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)
        self.ebo = glGenBuffers(1)

        glBindVertexArray(self.vao)

        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, quad_vertices.nbytes, quad_vertices, GL_STATIC_DRAW)

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, quad_indices.nbytes, quad_indices, GL_STATIC_DRAW)

        stride = 4 * ctypes.sizeof(ctypes.c_float)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 2, GL_FLOAT, False, stride, ctypes.c_void_p(0))
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, False, stride, ctypes.c_void_p(2 * ctypes.sizeof(ctypes.c_float)))

        glBindVertexArray(0)

        # Initialize Texture
        self.texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)

        blank_data = bytes(self.width * self.height * 4)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self.width, self.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, blank_data)
        glBindTexture(GL_TEXTURE_2D, 0)

        # Reusable PIL image buffer
        self.img = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        self.draw = ImageDraw.Draw(self.img)

    def on_resize(self, width: int, height: int) -> None:
        if width <= 0 or height <= 0:
            return
        self.width = width
        self.height = height

        glBindTexture(GL_TEXTURE_2D, self.texture_id)
        blank_data = bytes(self.width * self.height * 4)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self.width, self.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, blank_data)
        glBindTexture(GL_TEXTURE_2D, 0)

        self.img = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        self.draw = ImageDraw.Draw(self.img)

    def update_and_render(
        self,
        score_mgr: ScoreManager,
        world_mgr: Optional[Any] = None,
        transition: Optional[Any] = None,
        spawner: Optional[Any] = None,
        chase_mgr: Optional[Any] = None,
        powerup_mgr: Optional[Any] = None,
        show_debug: bool = False
    ) -> None:
        """Update HUD contents only when visible data changes.

        Tracks previous rendered values (score, collectibles, distance, world index,
        world timer, chase state, proximity ratio, etc.) and rebuilds the texture
        only if any of those have changed since the last frame. This reduces the
        expensive Pillow rasterization and the full `glTexSubImage2D` upload that
        previously occurred every frame (~70 ms per frame).
        """
        # Gather current state values that affect HUD appearance
        curr_world = world_mgr.current_world if world_mgr is not None else None
        accent_color = curr_world.hud_accent if curr_world is not None else (65, 140, 240)
        collectible_name = curr_world.collectible_name if curr_world is not None else "Coins"
        # Core HUD values
        cur_vals = {
            "collectibles_count": score_mgr.collectibles_count,
            "score": score_mgr.score,
            "distance": int(score_mgr.distance),
            "world_index": getattr(curr_world, "index", -1),
            "world_name": getattr(curr_world, "name", ""),
            "world_timer": getattr(world_mgr, "world_time_remaining", 0.0) if world_mgr else 0.0,
            "world_progress": getattr(world_mgr, "world_progress", 0.0) if world_mgr else 0.0,
            "chase_state": getattr(chase_mgr, "state", "") if chase_mgr else "",
            "proximity_ratio": getattr(chase_mgr, "proximity_ratio", 0.0) if chase_mgr else 0.0,
            "chase_distance": getattr(chase_mgr, "current_distance", 0.0) if chase_mgr else 0.0,
            "show_debug": show_debug,
        }
        # Determine if any tracked value changed since last frame
        dirty = False
        if not hasattr(self, "_prev_vals"):
            dirty = True
        else:
            for k, v in cur_vals.items():
                if self._prev_vals.get(k) != v:
                    dirty = True
                    break
        # Store current values for next frame
        self._prev_vals = cur_vals

        # Always clear the image buffer
        self.img.paste((0, 0, 0, 0), [0, 0, self.width, self.height])

        if dirty:
            # -------------------------------------------------------------
            # 1. Top HUD Status Bar Elements
            # -------------------------------------------------------------
            # Badge 1: Collectibles Counter & Item Name (Top Left)
            coin_box = [25, 20, 245, 70]
            self._draw_pill_badge(coin_box, fill_color=(15, 18, 30, 215), border_color=(*accent_color, 255))
            # Glowing Emblem
            self.draw.ellipse([36, 28, 64, 56], fill=(*accent_color, 255), outline=(255, 255, 255, 255), width=2)
            # Drop shadow on number
            self.draw.text((75, 28), f"{score_mgr.collectibles_count}", fill=(0, 0, 0, 180), font=self.font_header)
            self.draw.text((73, 26), f"{score_mgr.collectibles_count}", fill=(255, 255, 255, 255), font=self.font_header)
            self.draw.text((73, 50), f"{collectible_name.upper()}", fill=(210, 225, 250, 230), font=self.font_small)

            # Active Power-Up Cluster (Directly beneath Coin Badge, Top-Left)
            if powerup_mgr is not None:
                active_list = powerup_mgr.get_active_display_list()
                p_y0 = 80
                for item in active_list:
                    p_box = [25, p_y0, 245, p_y0 + 36]
                    p_border = (255, 60, 60, 255) if item["is_critical"] else (*item["color"], 240)
                    self._draw_pill_badge(p_box, fill_color=(16, 20, 32, 220), border_color=p_border, radius=8)

                    # Icon circle indicator
                    self.draw.ellipse([32, p_y0 + 7, 52, p_y0 + 27], fill=(*item["color"], 255), outline=(255, 255, 255, 255), width=1)
                    # Name and countdown
                    p_txt = f"{item['name'].upper()}: {item['time_left']:.1f}s"
                    txt_color = (255, 90, 90, 255) if item["is_critical"] else (240, 245, 255, 255)
                    self.draw.text((58, p_y0 + 9), p_txt, fill=txt_color, font=self.font_small)

                    # Countdown progress bar under badge
                    bar_w = 200
                    fill_w = max(2, int(bar_w * item["ratio"]))
                    self.draw.rounded_rectangle([32, p_y0 + 29, 32 + bar_w, p_y0 + 32], radius=2, fill=(35, 42, 58, 255))
                    self.draw.rounded_rectangle([32, p_y0 + 29, 32 + fill_w, p_y0 + 32], radius=2, fill=(*item["color"], 255))

                    p_y0 += 42

            # Badge 2: World Info & Timer Progress (Top Center)
            center_x = self.width // 2
            w_box = [center_x - 225, 20, center_x + 225, 70]
            self._draw_pill_badge(w_box, fill_color=(14, 18, 28, 225), border_color=(*accent_color, 255))
            world_title = f"WORLD {curr_world.index + 1}: {curr_world.name.upper()}" if curr_world else "DISNEY RUNNER"
            self.draw.text((center_x - 204, 27), world_title, fill=(0, 0, 0, 160), font=self.font_header)
            self.draw.text((center_x - 205, 25), world_title, fill=(255, 255, 255, 255), font=self.font_header)
            if world_mgr is not None:
                time_str = f"{int(world_mgr.world_time_remaining)}s"
                self.draw.text((center_x + 172, 26), time_str, fill=(255, 225, 100, 255), font=self.font_body)
                bar_w, bar_h = 410, 7
                bar_x = center_x - 205
                bar_y = 54
                self.draw.rounded_rectangle([bar_x, bar_y, bar_x + bar_w, bar_y + bar_h], radius=3, fill=(30, 36, 50, 255))
                fill_w = max(2, int(bar_w * (1.0 - world_mgr.world_progress)))
                self.draw.rounded_rectangle([bar_x, bar_y, bar_x + fill_w, bar_y + bar_h], radius=3, fill=(*accent_color, 255))

            # Badge 3: Score & Distance (Top Right)
            score_box = [self.width - 275, 20, self.width - 25, 70]
            self._draw_pill_badge(score_box, fill_color=(15, 18, 30, 215), border_color=(90, 210, 110, 255))
            score_str = f"SCORE: {score_mgr.score:06d}"
            dist_str = f"DIST: {int(score_mgr.distance)}m"
            self.draw.text((self.width - 258, 27), score_str, fill=(0, 0, 0, 160), font=self.font_header)
            self.draw.text((self.width - 260, 25), score_str, fill=(255, 255, 255, 255), font=self.font_header)
            self.draw.text((self.width - 260, 49), dist_str, fill=(130, 225, 255, 255), font=self.font_small)

            # -------------------------------------------------------------
            # 2. Villain Chase Proximity Meter
            # -------------------------------------------------------------
            if chase_mgr is not None and not score_mgr.is_game_over:
                c_state = chase_mgr.state
                prox_ratio = chase_mgr.proximity_ratio
                dist_val = chase_mgr.current_distance
                villain_name = curr_world.villain_name.upper() if curr_world else "PURSUIT"
                if c_state == "safe":
                    meter_border = (60, 220, 100, 240)
                    meter_bar_fill = (50, 220, 80, 255)
                    state_label = f"{villain_name}: SAFE"
                    label_color = (120, 255, 150, 255)
                elif c_state == "warning":
                    meter_border = (255, 205, 30, 240)
                    meter_bar_fill = (255, 195, 25, 255)
                    state_label = f"{villain_name}: CLOSE!"
                    label_color = (255, 225, 70, 255)
                else:
                    meter_border = (255, 50, 50, 255)
                    meter_bar_fill = (255, 45, 45, 255)
                    state_label = f"{villain_name}: CRITICAL!"
                    label_color = (255, 70, 70, 255)
                mw, mh = 430, 34
                m_box = [center_x - mw // 2, 78, center_x + mw // 2, 78 + mh]
                self._draw_pill_badge(m_box, fill_color=(14, 18, 28, 220), border_color=meter_border, radius=10)
                self.draw.text((center_x - 200, 85), state_label, fill=label_color, font=self.font_small)
                bar_x0, bar_y0 = center_x + 40, 87
                bar_w, bar_h = 120, 13
                self.draw.rounded_rectangle([bar_x0, bar_y0, bar_x0 + bar_w, bar_y0 + bar_h], radius=4, fill=(30, 36, 50, 255))
                fill_w = max(4, int(bar_w * prox_ratio))
                self.draw.rounded_rectangle([bar_x0, bar_y0, bar_x0 + fill_w, bar_y0 + bar_h], radius=4, fill=meter_bar_fill)
                self.draw.text((bar_x0 + bar_w + 14, 85), f"{dist_val:.1f}m", fill=(225, 230, 240, 255), font=self.font_small)

            # -------------------------------------------------------------
            # 3. World Transition Introduction Banner
            # -------------------------------------------------------------
            if transition is not None and transition.show_banner and transition.banner_alpha > 0.01:
                alpha = int(transition.banner_alpha * 240)
                banner_w, banner_h = 700, 115
                by0 = self.height // 3
                by1 = by0 + banner_h
                bx0 = center_x - banner_w // 2
                bx1 = center_x + banner_w // 2
                to_w = transition.to_world
                border_c = (*to_w.hud_accent, alpha) if to_w else (255, 220, 80, alpha)
                self.draw.rounded_rectangle([bx0 + 5, by0 + 5, bx1 + 5, by1 + 5], radius=18, fill=(0, 0, 0, int(alpha * 0.5)))
                self.draw.rounded_rectangle([bx0, by0, bx1, by1], radius=18, fill=(10, 14, 24, alpha), outline=border_c, width=3)
                title_text = f"WELCOME TO {transition.title_text}!"
                self.draw.text((center_x - 288, by0 + 20), title_text, fill=(0, 0, 0, int(transition.banner_alpha * 180)), font=self.font_banner)
                self.draw.text((center_x - 290, by0 + 18), title_text, fill=(255, 240, 120, int(transition.banner_alpha * 255)), font=self.font_banner)
                self.draw.text((center_x - 228, by0 + 72), transition.subtitle_text, fill=(0, 0, 0, int(transition.banner_alpha * 180)), font=self.font_body)
                self.draw.text((center_x - 230, by0 + 70), transition.subtitle_text, fill=(200, 225, 255, int(transition.banner_alpha * 255)), font=self.font_body)

            # -------------------------------------------------------------
            # 4. Screen flash effect at transition switch point
            # -------------------------------------------------------------
            if transition is not None and transition.screen_flash_alpha > 0.01:
                flash_a = int(transition.screen_flash_alpha * 255)
                self.draw.rectangle([0, 0, self.width, self.height], fill=(255, 255, 255, flash_a))

            # -------------------------------------------------------------
            # 5. Debug Information Overlay (Bottom-Left)
            # -------------------------------------------------------------
            if show_debug and spawner is not None:
                stats = spawner.get_debug_stats()
                chase_stats = chase_mgr.get_debug_stats() if chase_mgr is not None else {}
                w_stats = world_mgr.get_debug_stats() if world_mgr is not None else {}
                dbg_lines = [
                    f"[SYSTEM DEBUG] (F3 to hide)",
                    f"Active World:     {w_stats.get('world_name', 'N/A')} ({w_stats.get('world_index', 0)+1}/8)",
                    f"World Timer:      {w_stats.get('world_timer', 0.0):.1f}s / {w_stats.get('world_duration', 60.0):.1f}s",
                    f"Transitions:      {w_stats.get('total_transitions', 0)}",
                    f"Waves Spawned:    {stats['waves_spawned']}",
                    f"Active Hazards:   {stats['active_obstacles']} obs, {stats['active_collectibles']} items",
                    f"Villain Pursuit:  {chase_stats.get('chase_distance', 0.0):.2f}m ({chase_stats.get('state', 'N/A')})",
                ]
                dbg_w, dbg_h = 320, 20 + len(dbg_lines) * 20
                dbg_y0 = self.height - dbg_h - 20
                self._draw_pill_badge([20, dbg_y0, 20 + dbg_w, dbg_y0 + dbg_h], fill_color=(12, 16, 26, 225), border_color=(100, 180, 255, 200), radius=8)
                for idx, line in enumerate(dbg_lines):
                    c = (255, 220, 60, 255) if idx == 0 else (220, 230, 245, 255)
                    self.draw.text((30, dbg_y0 + 8 + idx * 20), line, fill=c, font=self.font_small)

            # -------------------------------------------------------------
            # 6. Game Over Banner Overlay
            # -------------------------------------------------------------
            if score_mgr.is_game_over:
                self.draw.rectangle([0, 0, self.width, self.height], fill=(8, 10, 16, 195))
                cw, ch = 580, 360
                cx0, cy0 = center_x - cw // 2, (self.height // 2) - ch // 2
                cx1, cy1 = cx0 + cw, cy0 + ch
                self.draw.rounded_rectangle([cx0 + 6, cy0 + 6, cx1 + 6, cy1 + 6], radius=16, fill=(0, 0, 0, 160))
                self._draw_pill_badge([cx0, cy0, cx1, cy1], fill_color=(16, 20, 32, 250), border_color=(255, 75, 75, 255), radius=16)
                title_text = "GAME OVER"
                self.draw.text((center_x - 147, cy0 + 26), title_text, fill=(0, 0, 0, 180), font=self.font_title)
                self.draw.text((center_x - 145, cy0 + 24), title_text, fill=(255, 80, 80, 255), font=self.font_title)
                reason_text = score_mgr.game_over_reason if score_mgr.game_over_reason else "RUN ENDED"
                self.draw.text((center_x - 170, cy0 + 82), f"Reason: {reason_text}", fill=(255, 190, 60, 255), font=self.font_small)
                y_stat = cy0 + 120
                self.draw.text((center_x - 170, y_stat), "Final Score:", fill=(200, 205, 220, 255), font=self.font_header)
                self.draw.text((center_x + 50, y_stat), f"{score_mgr.score}", fill=(255, 225, 60, 255), font=self.font_header)
                y_stat += 36
                self.draw.text((center_x - 170, y_stat), "Distance Run:", fill=(200, 205, 220, 255), font=self.font_header)
                self.draw.text((center_x + 50, y_stat), f"{int(score_mgr.distance)}m", fill=(120, 215, 255, 255), font=self.font_header)
                y_stat += 36
                self.draw.text((center_x - 170, y_stat), f"{collectible_name} Picked:", fill=(200, 205, 220, 255), font=self.font_header)
                self.draw.text((center_x + 50, y_stat), f"{score_mgr.collectibles_count}", fill=(255, 210, 40, 255), font=self.font_header)
                y_stat += 36
                w_reached = f"World {curr_world.index + 1}: {curr_world.name}" if curr_world else "N/A"
                self.draw.text((center_x - 170, y_stat), "World Reached:", fill=(200, 205, 220, 255), font=self.font_header)
                self.draw.text((center_x + 50, y_stat), w_reached, fill=(160, 220, 255, 255), font=self.font_header)
                restart_prompt = "PRESS [SPACE] OR [R] TO RETRY"
                self.draw.text((center_x - 160, cy0 + 305), restart_prompt, fill=(120, 255, 150, 255), font=self.font_body)

        # -------------------------------------------------------------
        # 7. Upload Dynamic Texture & Render 2D Quad (throttled to 20 Hz)
        # -------------------------------------------------------------
        import time
        now = time.time()
        # Only rebuild HUD texture when visible data changes *and* at most 20 Hz
        if dirty and (now - getattr(self, "_last_upload", 0) >= 0.05):
            # -------------------------------------------------------------
            # 1. Top HUD Status Bar Elements (draw only on throttled updates)
            # -------------------------------------------------------------
            # Badge 1: Collectibles Counter & Item Name (Top Left)
            coin_box = [25, 20, 245, 70]
            self._draw_pill_badge(coin_box, fill_color=(15, 18, 30, 215), border_color=(*accent_color, 255))
            self.draw.ellipse([36, 28, 64, 56], fill=(*accent_color, 255), outline=(255, 255, 255, 255), width=2)
            self.draw.text((75, 28), f"{score_mgr.collectibles_count}", fill=(0, 0, 0, 180), font=self.font_header)
            self.draw.text((73, 26), f"{score_mgr.collectibles_count}", fill=(255, 255, 255, 255), font=self.font_header)
            self.draw.text((73, 50), f"{collectible_name.upper()}", fill=(210, 225, 250, 230), font=self.font_small)

            # Badge 2: World Info & Timer (Top Center)
            center_x = self.width // 2
            w_box = [center_x - 225, 20, center_x + 225, 70]
            self._draw_pill_badge(w_box, fill_color=(14, 18, 28, 225), border_color=(*accent_color, 255))
            world_title = f"WORLD {curr_world.index + 1}: {curr_world.name.upper()}" if curr_world else "DISNEY RUNNER"
            self.draw.text((center_x - 204, 27), world_title, fill=(0, 0, 0, 160), font=self.font_header)
            self.draw.text((center_x - 205, 25), world_title, fill=(255, 255, 255, 255), font=self.font_header)
            if world_mgr is not None:
                time_str = f"{int(world_mgr.world_time_remaining)}s"
                self.draw.text((center_x + 172, 26), time_str, fill=(255, 225, 100, 255), font=self.font_body)
                bar_w, bar_h = 410, 7
                bar_x, bar_y = center_x - 205, 54
                self.draw.rounded_rectangle([bar_x, bar_y, bar_x + bar_w, bar_y + bar_h], radius=3, fill=(30, 36, 50, 255))
                fill_w = max(2, int(bar_w * (1.0 - world_mgr.world_progress)))
                self.draw.rounded_rectangle([bar_x, bar_y, bar_x + fill_w, bar_y + bar_h], radius=3, fill=(*accent_color, 255))

            # Badge 3: Score & Distance (Top Right)
            score_box = [self.width - 275, 20, self.width - 25, 70]
            self._draw_pill_badge(score_box, fill_color=(15, 18, 30, 215), border_color=(90, 210, 110, 255))
            score_str = f"SCORE: {score_mgr.score:06d}"
            dist_str = f"DIST: {int(score_mgr.distance)}m"
            self.draw.text((self.width - 258, 27), score_str, fill=(0, 0, 0, 160), font=self.font_header)
            self.draw.text((self.width - 260, 25), score_str, fill=(255, 255, 255, 255), font=self.font_header)
            self.draw.text((self.width - 260, 49), dist_str, fill=(130, 225, 255, 255), font=self.font_small)

            # Villain Chase Proximity Meter (centered below World Badge)
            if chase_mgr is not None and not score_mgr.is_game_over:
                c_state = chase_mgr.state
                prox_ratio = chase_mgr.proximity_ratio
                dist_val = chase_mgr.current_distance
                villain_name = curr_world.villain_name.upper() if curr_world else "PURSUIT"
                if c_state == "safe":
                    meter_border = (60, 220, 100, 240)
                    meter_bar_fill = (50, 220, 80, 255)
                    state_label = f"{villain_name}: SAFE"
                    label_color = (120, 255, 150, 255)
                elif c_state == "warning":
                    meter_border = (255, 205, 30, 240)
                    meter_bar_fill = (255, 195, 25, 255)
                    state_label = f"{villain_name}: CLOSE!"
                    label_color = (255, 225, 70, 255)
                else:
                    meter_border = (255, 50, 50, 255)
                    meter_bar_fill = (255, 45, 45, 255)
                    state_label = f"{villain_name}: CRITICAL!"
                    label_color = (255, 70, 70, 255)
                mw, mh = 430, 34
                m_box = [center_x - mw // 2, 78, center_x + mw // 2, 78 + mh]
                self._draw_pill_badge(m_box, fill_color=(14, 18, 28, 220), border_color=meter_border, radius=10)
                self.draw.text((center_x - 200, 85), state_label, fill=label_color, font=self.font_small)
                bar_x0, bar_y0 = center_x + 40, 87
                bar_w, bar_h = 120, 13
                self.draw.rounded_rectangle([bar_x0, bar_y0, bar_x0 + bar_w, bar_y0 + bar_h], radius=4, fill=(30, 36, 50, 255))
                fill_w = max(4, int(bar_w * prox_ratio))
                self.draw.rounded_rectangle([bar_x0, bar_y0, bar_x0 + fill_w, bar_y0 + bar_h], radius=4, fill=meter_bar_fill)
                self.draw.text((bar_x0 + bar_w + 14, 85), f"{dist_val:.1f}m", fill=(225, 230, 240, 255), font=self.font_small)

            # World Transition Banner
            if transition is not None and transition.show_banner and transition.banner_alpha > 0.01:
                alpha = int(transition.banner_alpha * 240)
                banner_w, banner_h = 700, 115
                by0 = self.height // 3
                bx0 = center_x - banner_w // 2
                bx1 = center_x + banner_w // 2
                to_w = transition.to_world
                border_c = (*to_w.hud_accent, alpha) if to_w else (255, 220, 80, alpha)
                self.draw.rounded_rectangle([bx0 + 5, by0 + 5, bx1 + 5, by0 + 5 + banner_h], radius=18, fill=(0, 0, 0, int(alpha * 0.5)))
                self.draw.rounded_rectangle([bx0, by0, bx1, by0 + banner_h], radius=18, fill=(10, 14, 24, alpha), outline=border_c, width=3)
                title_text = f"WELCOME TO {transition.title_text}!"
                self.draw.text((center_x - 288, by0 + 20), title_text, fill=(0, 0, 0, int(transition.banner_alpha * 180)), font=self.font_banner)
                self.draw.text((center_x - 290, by0 + 18), title_text, fill=(255, 240, 120, int(transition.banner_alpha * 255)), font=self.font_banner)
                self.draw.text((center_x - 228, by0 + 72), transition.subtitle_text, fill=(0, 0, 0, int(transition.banner_alpha * 180)), font=self.font_body)
                self.draw.text((center_x - 230, by0 + 70), transition.subtitle_text, fill=(200, 225, 255, int(transition.banner_alpha * 255)), font=self.font_body)

            # Screen flash effect
            if transition is not None and transition.screen_flash_alpha > 0.01:
                flash_a = int(transition.screen_flash_alpha * 255)
                self.draw.rectangle([0, 0, self.width, self.height], fill=(255, 255, 255, flash_a))

            # Debug overlay (bottom‑left)
            if show_debug and spawner is not None:
                stats = spawner.get_debug_stats()
                chase_stats = chase_mgr.get_debug_stats() if chase_mgr is not None else {}
                w_stats = world_mgr.get_debug_stats() if world_mgr is not None else {}
                dbg_lines = [
                    f"[SYSTEM DEBUG] (F3 to hide)",
                    f"Active World:     {w_stats.get('world_name', 'N/A')} ({w_stats.get('world_index', 0)+1}/8)",
                    f"World Timer:      {w_stats.get('world_timer', 0.0):.1f}s / {w_stats.get('world_duration', 60.0):.1f}s",
                    f"Transitions:      {w_stats.get('total_transitions', 0)}",
                    f"Waves Spawned:    {stats['waves_spawned']}",
                    f"Active Hazards:   {stats['active_obstacles']} obs, {stats['active_collectibles']} items",
                    f"Villain Pursuit:  {chase_stats.get('chase_distance', 0.0):.2f}m ({chase_stats.get('state', 'N/A')})",
                ]
                dbg_w, dbg_h = 320, 20 + len(dbg_lines) * 20
                dbg_y0 = self.height - dbg_h - 20
                self._draw_pill_badge([20, dbg_y0, 20 + dbg_w, dbg_y0 + dbg_h], fill_color=(12, 16, 26, 225), border_color=(100, 180, 255, 200), radius=8)
                for idx, line in enumerate(dbg_lines):
                    c = (255, 220, 60, 255) if idx == 0 else (220, 230, 245, 255)
                    self.draw.text((30, dbg_y0 + 8 + idx * 20), line, fill=c, font=self.font_small)

            # Game Over banner
            if score_mgr.is_game_over:
                self.draw.rectangle([0, 0, self.width, self.height], fill=(8, 10, 16, 195))
                cw, ch = 580, 360
                cx0, cy0 = center_x - cw // 2, (self.height // 2) - ch // 2
                cx1, cy1 = cx0 + cw, cy0 + ch
                self.draw.rounded_rectangle([cx0 + 6, cy0 + 6, cx1 + 6, cy1 + 6], radius=16, fill=(0, 0, 0, 160))
                self._draw_pill_badge([cx0, cy0, cx1, cy1], fill_color=(16, 20, 32, 250), border_color=(255, 75, 75, 255), radius=16)
                title_text = "GAME OVER"
                self.draw.text((center_x - 147, cy0 + 26), title_text, fill=(0, 0, 0, 180), font=self.font_title)
                self.draw.text((center_x - 145, cy0 + 24), title_text, fill=(255, 80, 80, 255), font=self.font_title)
                reason_text = score_mgr.game_over_reason if score_mgr.game_over_reason else "RUN ENDED"
                self.draw.text((center_x - 170, cy0 + 82), f"Reason: {reason_text}", fill=(255, 190, 60, 255), font=self.font_small)
                y_stat = cy0 + 120
                self.draw.text((center_x - 170, y_stat), "Final Score:", fill=(200, 205, 220, 255), font=self.font_header)
                self.draw.text((center_x + 50, y_stat), f"{score_mgr.score}", fill=(255, 225, 60, 255), font=self.font_header)
                y_stat += 36
                self.draw.text((center_x - 170, y_stat), "Distance Run:", fill=(200, 205, 220, 255), font=self.font_header)
                self.draw.text((center_x + 50, y_stat), f"{int(score_mgr.distance)}m", fill=(120, 215, 255, 255), font=self.font_header)
                y_stat += 36
                self.draw.text((center_x - 170, y_stat), f"{collectible_name} Picked:", fill=(200, 205, 220, 255), font=self.font_header)
                self.draw.text((center_x + 50, y_stat), f"{score_mgr.collectibles_count}", fill=(255, 210, 40, 255), font=self.font_header)
                y_stat += 36
                w_reached = f"World {curr_world.index + 1}: {curr_world.name}" if curr_world else "N/A"
                self.draw.text((center_x - 170, y_stat), "World Reached:", fill=(200, 205, 220, 255), font=self.font_header)
                self.draw.text((center_x + 50, y_stat), w_reached, fill=(160, 220, 255, 255), font=self.font_header)
                restart_prompt = "PRESS [SPACE] OR [R] TO RETRY"
                self.draw.text((center_x - 160, cy0 + 305), restart_prompt, fill=(120, 255, 150, 255), font=self.font_body)

            # -------------------------------------------------------------
            # 8. Upload texture (now that img has been rebuilt)
            # -------------------------------------------------------------
            tex_bytes = self.img.tobytes()
            glActiveTexture(GL_TEXTURE0)
            glBindTexture(GL_TEXTURE_2D, self.texture_id)
            glTexSubImage2D(GL_TEXTURE_2D, 0, 0, 0, self.width, self.height, GL_RGBA, GL_UNSIGNED_BYTE, tex_bytes)
            self._last_upload = now
        # Render the HUD quad every frame (uses the most recently uploaded texture)
        glDisable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        self.shader.use()
        self.shader.set_int("uTexture", 0)
        glBindVertexArray(self.vao)
        glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, None)
        glBindVertexArray(0)
        self.shader.unbind()
        glDisable(GL_BLEND)
        glEnable(GL_DEPTH_TEST)
        self.img.paste((0, 0, 0, 0), [0, 0, self.width, self.height])

        curr_world = world_mgr.current_world if world_mgr is not None else None
        accent_color = curr_world.hud_accent if curr_world is not None else (65, 140, 240)
        collectible_name = curr_world.collectible_name if curr_world is not None else "Coins"

        # -------------------------------------------------------------
        # 1. Top HUD Status Bar Elements
        # -------------------------------------------------------------
        # Badge 1: Collectibles Counter & Item Name (Top Left)
        coin_box = [25, 20, 245, 70]
        self._draw_pill_badge(coin_box, fill_color=(15, 18, 30, 215), border_color=(*accent_color, 255))
        # Glowing Emblem
        self.draw.ellipse([36, 28, 64, 56], fill=(*accent_color, 255), outline=(255, 255, 255, 255), width=2)
        # Drop shadow on number
        self.draw.text((75, 28), f"{score_mgr.collectibles_count}", fill=(0, 0, 0, 180), font=self.font_header)
        self.draw.text((73, 26), f"{score_mgr.collectibles_count}", fill=(255, 255, 255, 255), font=self.font_header)
        self.draw.text((73, 50), f"{collectible_name.upper()}", fill=(210, 225, 250, 230), font=self.font_small)

        # Badge 2: World Info & Timer Progress (Top Center)
        center_x = self.width // 2
        w_box = [center_x - 225, 20, center_x + 225, 70]
        self._draw_pill_badge(w_box, fill_color=(14, 18, 28, 225), border_color=(*accent_color, 255))

        world_title = f"WORLD {curr_world.index + 1}: {curr_world.name.upper()}" if curr_world else "DISNEY RUNNER"
        self.draw.text((center_x - 204, 27), world_title, fill=(0, 0, 0, 160), font=self.font_header)
        self.draw.text((center_x - 205, 25), world_title, fill=(255, 255, 255, 255), font=self.font_header)

        # World progress timer bar
        if world_mgr is not None:
            time_str = f"{int(world_mgr.world_time_remaining)}s"
            self.draw.text((center_x + 172, 26), time_str, fill=(255, 225, 100, 255), font=self.font_body)
            # Progress bar track
            bar_w = 410
            bar_h = 7
            bar_x = center_x - 205
            bar_y = 54
            self.draw.rounded_rectangle([bar_x, bar_y, bar_x + bar_w, bar_y + bar_h], radius=3, fill=(30, 36, 50, 255))
            fill_w = max(2, int(bar_w * (1.0 - world_mgr.world_progress)))
            self.draw.rounded_rectangle([bar_x, bar_y, bar_x + fill_w, bar_y + bar_h], radius=3, fill=(*accent_color, 255))

        # Badge 3: Score & Distance (Top Right)
        score_box = [self.width - 275, 20, self.width - 25, 70]
        self._draw_pill_badge(score_box, fill_color=(15, 18, 30, 215), border_color=(90, 210, 110, 255))
        score_str = f"SCORE: {score_mgr.score:06d}"
        dist_str = f"DIST: {int(score_mgr.distance)}m"
        self.draw.text((self.width - 258, 27), score_str, fill=(0, 0, 0, 160), font=self.font_header)
        self.draw.text((self.width - 260, 25), score_str, fill=(255, 255, 255, 255), font=self.font_header)
        self.draw.text((self.width - 260, 49), dist_str, fill=(130, 225, 255, 255), font=self.font_small)

        # -------------------------------------------------------------
        # 2. Villain Chase Proximity Meter (Centered below World Badge)
        # -------------------------------------------------------------
        if chase_mgr is not None and not score_mgr.is_game_over:
            c_state = chase_mgr.state
            prox_ratio = chase_mgr.proximity_ratio
            dist_val = chase_mgr.current_distance
            villain_name = curr_world.villain_name.upper() if curr_world else "PURSUIT"

            if c_state == "safe":
                meter_border = (60, 220, 100, 240)
                meter_bar_fill = (50, 220, 80, 255)
                state_label = f"{villain_name}: SAFE"
                label_color = (120, 255, 150, 255)
            elif c_state == "warning":
                meter_border = (255, 205, 30, 240)
                meter_bar_fill = (255, 195, 25, 255)
                state_label = f"{villain_name}: CLOSE!"
                label_color = (255, 225, 70, 255)
            else:
                meter_border = (255, 50, 50, 255)
                meter_bar_fill = (255, 45, 45, 255)
                state_label = f"{villain_name}: CRITICAL!"
                label_color = (255, 70, 70, 255)

            mw, mh = 430, 34
            m_box = [center_x - mw // 2, 78, center_x + mw // 2, 78 + mh]
            self._draw_pill_badge(m_box, fill_color=(14, 18, 28, 220), border_color=meter_border, radius=10)

            self.draw.text((center_x - 200, 85), state_label, fill=label_color, font=self.font_small)

            bar_x0 = center_x + 40
            bar_y0 = 87
            bar_w = 120
            bar_h = 13
            self.draw.rounded_rectangle([bar_x0, bar_y0, bar_x0 + bar_w, bar_y0 + bar_h], radius=4, fill=(30, 36, 50, 255))
            fill_w = max(4, int(bar_w * prox_ratio))
            self.draw.rounded_rectangle([bar_x0, bar_y0, bar_x0 + fill_w, bar_y0 + bar_h], radius=4, fill=meter_bar_fill)
            self.draw.text((bar_x0 + bar_w + 14, 85), f"{dist_val:.1f}m", fill=(225, 230, 240, 255), font=self.font_small)

        # -------------------------------------------------------------
        # 3. World Transition Introduction Banner
        # -------------------------------------------------------------
        if transition is not None and transition.show_banner and transition.banner_alpha > 0.01:
            alpha = int(transition.banner_alpha * 240)
            banner_w, banner_h = 700, 115
            by0 = self.height // 3
            by1 = by0 + banner_h
            bx0 = center_x - banner_w // 2
            bx1 = center_x + banner_w // 2

            to_w = transition.to_world
            border_c = (*to_w.hud_accent, alpha) if to_w else (255, 220, 80, alpha)

            # Drop shadow
            self.draw.rounded_rectangle([bx0 + 5, by0 + 5, bx1 + 5, by1 + 5], radius=18, fill=(0, 0, 0, int(alpha * 0.5)))
            self.draw.rounded_rectangle([bx0, by0, bx1, by1], radius=18, fill=(10, 14, 24, alpha), outline=border_c, width=3)

            title_text = f"WELCOME TO {transition.title_text}!"
            self.draw.text((center_x - 288, by0 + 20), title_text, fill=(0, 0, 0, int(transition.banner_alpha * 180)), font=self.font_banner)
            self.draw.text((center_x - 290, by0 + 18), title_text, fill=(255, 240, 120, int(transition.banner_alpha * 255)), font=self.font_banner)

            self.draw.text((center_x - 228, by0 + 72), transition.subtitle_text, fill=(0, 0, 0, int(transition.banner_alpha * 180)), font=self.font_body)
            self.draw.text((center_x - 230, by0 + 70), transition.subtitle_text, fill=(200, 225, 255, int(transition.banner_alpha * 255)), font=self.font_body)

        # Screen flash effect at transition switch point
        if transition is not None and transition.screen_flash_alpha > 0.01:
            flash_a = int(transition.screen_flash_alpha * 255)
            self.draw.rectangle([0, 0, self.width, self.height], fill=(255, 255, 255, flash_a))

        # -------------------------------------------------------------
        # 4. Debug Information Overlay (Bottom-Left)
        # -------------------------------------------------------------
        if show_debug and spawner is not None:
            stats = spawner.get_debug_stats()
            chase_stats = chase_mgr.get_debug_stats() if chase_mgr is not None else {}
            w_stats = world_mgr.get_debug_stats() if world_mgr is not None else {}
            dbg_lines = [
                f"[SYSTEM DEBUG] (F3 to hide)",
                f"Active World:     {w_stats.get('world_name', 'N/A')} ({w_stats.get('world_index', 0)+1}/8)",
                f"World Timer:      {w_stats.get('world_timer', 0.0):.1f}s / {w_stats.get('world_duration', 60.0):.1f}s",
                f"Transitions:      {w_stats.get('total_transitions', 0)}",
                f"Waves Spawned:    {stats['waves_spawned']}",
                f"Active Hazards:   {stats['active_obstacles']} obs, {stats['active_collectibles']} items",
                f"Villain Pursuit:  {chase_stats.get('chase_distance', 0.0):.2f}m ({chase_stats.get('state', 'N/A')})"
            ]
            dbg_w, dbg_h = 320, 20 + len(dbg_lines) * 20
            dbg_y0 = self.height - dbg_h - 20
            self._draw_pill_badge([20, dbg_y0, 20 + dbg_w, dbg_y0 + dbg_h], fill_color=(12, 16, 26, 225), border_color=(100, 180, 255, 200), radius=8)
            for idx, line in enumerate(dbg_lines):
                c = (255, 220, 60, 255) if idx == 0 else (220, 230, 245, 255)
                self.draw.text((30, dbg_y0 + 8 + idx * 20), line, fill=c, font=self.font_small)

        # -------------------------------------------------------------
        # 5. Game Over Banner Overlay
        # -------------------------------------------------------------
        if score_mgr.is_game_over:
            self.draw.rectangle([0, 0, self.width, self.height], fill=(8, 10, 16, 195))

            cw, ch = 580, 360
            cx0, cy0 = center_x - cw // 2, (self.height // 2) - ch // 2
            cx1, cy1 = cx0 + cw, cy0 + ch

            self.draw.rounded_rectangle([cx0 + 6, cy0 + 6, cx1 + 6, cy1 + 6], radius=16, fill=(0, 0, 0, 160))
            self._draw_pill_badge([cx0, cy0, cx1, cy1], fill_color=(16, 20, 32, 250), border_color=(255, 75, 75, 255), radius=16)

            title_text = "GAME OVER"
            self.draw.text((center_x - 147, cy0 + 26), title_text, fill=(0, 0, 0, 180), font=self.font_title)
            self.draw.text((center_x - 145, cy0 + 24), title_text, fill=(255, 80, 80, 255), font=self.font_title)

            reason_text = score_mgr.game_over_reason if score_mgr.game_over_reason else "RUN ENDED"
            self.draw.text((center_x - 170, cy0 + 82), f"Reason: {reason_text}", fill=(255, 190, 60, 255), font=self.font_small)

            y_stat = cy0 + 120
            self.draw.text((center_x - 170, y_stat), "Final Score:", fill=(200, 205, 220, 255), font=self.font_header)
            self.draw.text((center_x + 50, y_stat), f"{score_mgr.score}", fill=(255, 225, 60, 255), font=self.font_header)

            y_stat += 36
            self.draw.text((center_x - 170, y_stat), "Distance Run:", fill=(200, 205, 220, 255), font=self.font_header)
            self.draw.text((center_x + 50, y_stat), f"{int(score_mgr.distance)}m", fill=(120, 215, 255, 255), font=self.font_header)

            y_stat += 36
            self.draw.text((center_x - 170, y_stat), f"{collectible_name} Picked:", fill=(200, 205, 220, 255), font=self.font_header)
            self.draw.text((center_x + 50, y_stat), f"{score_mgr.collectibles_count}", fill=(255, 210, 40, 255), font=self.font_header)

            y_stat += 36
            w_reached = f"World {curr_world.index + 1}: {curr_world.name}" if curr_world else "N/A"
            self.draw.text((center_x - 170, y_stat), "World Reached:", fill=(200, 205, 220, 255), font=self.font_header)
            self.draw.text((center_x + 50, y_stat), w_reached, fill=(160, 220, 255, 255), font=self.font_header)

            restart_prompt = "PRESS [SPACE] OR [R] TO RETRY"
            self.draw.text((center_x - 160, cy0 + 305), restart_prompt, fill=(120, 255, 150, 255), font=self.font_body)

        # -------------------------------------------------------------
        # 6. Upload Dynamic Texture & Render 2D Quad
        # -------------------------------------------------------------
        tex_bytes = self.img.tobytes()

        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.texture_id)
        glTexSubImage2D(GL_TEXTURE_2D, 0, 0, 0, self.width, self.height, GL_RGBA, GL_UNSIGNED_BYTE, tex_bytes)

        glDisable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        self.shader.use()
        self.shader.set_int("uTexture", 0)

        glBindVertexArray(self.vao)
        glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, None)
        glBindVertexArray(0)

        self.shader.unbind()
        glDisable(GL_BLEND)
        glEnable(GL_DEPTH_TEST)

    def _draw_pill_badge(
        self,
        box: list[int],
        fill_color: Tuple[int, int, int, int],
        border_color: Tuple[int, int, int, int],
        radius: int = 12
    ) -> None:
        x0, y0, x1, y1 = box
        # Drop shadow
        self.draw.rounded_rectangle([x0 + 3, y0 + 3, x1 + 3, y1 + 3], radius=radius, fill=(0, 0, 0, 100))
        self.draw.rounded_rectangle([x0, y0, x1, y1], radius=radius, fill=fill_color, outline=border_color, width=2)

    def delete(self) -> None:
        if self.texture_id:
            glDeleteTextures(1, [self.texture_id])
            self.texture_id = 0
        if self.vbo:
            glDeleteBuffers(1, [self.vbo])
            self.vbo = 0
        if self.ebo:
            glDeleteBuffers(1, [self.ebo])
            self.ebo = 0
        if self.vao:
            glDeleteVertexArrays(1, [self.vao])
            self.vao = 0
        if self.shader:
            self.shader.delete()
            self.shader = None
