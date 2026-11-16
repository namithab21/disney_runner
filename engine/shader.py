"""
shader.py - Modern OpenGL GLSL Shader Program Abstraction.
Handles loading, compiling, linking, uniform binding, and cleanup.
"""

from pathlib import Path
import numpy as np
from OpenGL.GL import (
    glCreateShader, glShaderSource, glCompileShader, glGetShaderiv,
    glGetShaderInfoLog, glCreateProgram, glAttachShader, glLinkProgram,
    glGetProgramiv, glGetProgramInfoLog, glDeleteShader, glDeleteProgram,
    glUseProgram, glGetUniformLocation, glUniform1i, glUniform1f,
    glUniform3f, glUniform4f, glUniformMatrix4fv,
    GL_VERTEX_SHADER, GL_FRAGMENT_SHADER, GL_COMPILE_STATUS, GL_LINK_STATUS, GL_FALSE
)


class ShaderProgram:
    """Manages GLSL vertex and fragment shader compilation, linking, and uniform updates."""

    def __init__(self, vertex_path: str | Path, fragment_path: str | Path):
        self.program_id = glCreateProgram()
        self._uniform_locations: dict[str, int] = {}

        vertex_src = self._read_file(vertex_path)
        fragment_src = self._read_file(fragment_path)

        vertex_shader = self._compile_shader(vertex_src, GL_VERTEX_SHADER, str(vertex_path))
        fragment_shader = self._compile_shader(fragment_src, GL_FRAGMENT_SHADER, str(fragment_path))

        glAttachShader(self.program_id, vertex_shader)
        glAttachShader(self.program_id, fragment_shader)
        glLinkProgram(self.program_id)

        # Check linking status
        linked = glGetProgramiv(self.program_id, GL_LINK_STATUS)
        if not linked:
            log = glGetProgramInfoLog(self.program_id).decode('utf-8')
            raise RuntimeError(f"Shader program linking failed:\n{log}")

        # Shaders are linked into program, intermediate shader objects can be released
        glDeleteShader(vertex_shader)
        glDeleteShader(fragment_shader)

    @staticmethod
    def _read_file(path: str | Path) -> str:
        file_path = Path(path)
        if not file_path.exists():
            raise FileNotFoundError(f"Shader file not found: {file_path}")
        return file_path.read_text(encoding="utf-8")

    @staticmethod
    def _compile_shader(source: str, shader_type: int, name: str) -> int:
        shader = glCreateShader(shader_type)
        glShaderSource(shader, source)
        glCompileShader(shader)

        compiled = glGetShaderiv(shader, GL_COMPILE_STATUS)
        if not compiled:
            log = glGetShaderInfoLog(shader).decode('utf-8')
            shader_type_str = "Vertex" if shader_type == GL_VERTEX_SHADER else "Fragment"
            raise RuntimeError(f"{shader_type_str} shader compilation failed for '{name}':\n{log}")
        return shader

    def use(self) -> None:
        """Binds the shader program for subsequent draw calls."""
        glUseProgram(self.program_id)

    def unbind(self) -> None:
        """Unbinds the shader program."""
        glUseProgram(0)

    def get_uniform_location(self, name: str) -> int:
        """Caches and returns the uniform location index."""
        if name not in self._uniform_locations:
            loc = glGetUniformLocation(self.program_id, name)
            self._uniform_locations[name] = loc
        return self._uniform_locations[name]

    def set_int(self, name: str, value: int) -> None:
        loc = self.get_uniform_location(name)
        if loc != -1:
            glUniform1i(loc, value)

    def set_float(self, name: str, value: float) -> None:
        loc = self.get_uniform_location(name)
        if loc != -1:
            glUniform1f(loc, float(value))

    def set_vec3(self, name: str, x: float | np.ndarray | list, y: float = None, z: float = None) -> None:
        loc = self.get_uniform_location(name)
        if loc == -1:
            return
        if y is None or z is None:
            # Assumed array or list of length 3
            glUniform3f(loc, float(x[0]), float(x[1]), float(x[2]))
        else:
            glUniform3f(loc, float(x), float(y), float(z))

    def set_vec4(self, name: str, x: float, y: float, z: float, w: float) -> None:
        loc = self.get_uniform_location(name)
        if loc != -1:
            glUniform4f(loc, float(x), float(y), float(z), float(w))

    def set_mat4(self, name: str, matrix) -> None:
        """
        Pass a 4x4 matrix (from Pyrr or NumPy) into the uniform.
        Pyrr Matrix44 objects convert seamlessly via numpy array conversion.
        """
        loc = self.get_uniform_location(name)
        if loc != -1:
            mat_arr = np.ascontiguousarray(matrix, dtype=np.float32)
            glUniformMatrix4fv(loc, 1, GL_FALSE, mat_arr)

    def delete(self) -> None:
        """Cleans up the OpenGL program resource."""
        if self.program_id != 0:
            glDeleteProgram(self.program_id)
            self.program_id = 0
