"""
mesh.py - Modern OpenGL Mesh Abstraction (VAO, VBO, EBO).
Encapsulates buffer management, layout specifications, and rendering.
"""

from typing import Optional, List, Tuple
import ctypes
import numpy as np
from OpenGL.GL import (
    glGenVertexArrays, glBindVertexArray, glDeleteVertexArrays,
    glGenBuffers, glBindBuffer, glBufferData, glDeleteBuffers,
    glEnableVertexAttribArray, glVertexAttribPointer,
    glDrawArrays, glDrawElements,
    GL_ARRAY_BUFFER, GL_ELEMENT_ARRAY_BUFFER, GL_STATIC_DRAW,
    GL_FLOAT, GL_UNSIGNED_INT, GL_TRIANGLES
)


class VertexAttribute:
    """Defines a single vertex attribute layout in an interleaved buffer."""
    def __init__(self, location: int, size: int, attr_type: int = GL_FLOAT, normalized: bool = False):
        self.location = location
        self.size = size
        self.type = attr_type
        self.normalized = normalized


class Mesh:
    """
    Encapsulates a modern OpenGL Vertex Array Object (VAO) with associated
    Vertex Buffer Object (VBO) and optional Element Buffer Object (EBO).
    """

    def __init__(
        self,
        vertices: np.ndarray,
        attributes: List[VertexAttribute],
        indices: Optional[np.ndarray] = None,
        stride: Optional[int] = None
    ):
        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)
        self.ebo: Optional[int] = glGenBuffers(1) if indices is not None else None

        self.vertex_count = len(vertices)
        self.index_count = len(indices) if indices is not None else 0
        self.is_indexed = indices is not None

        glBindVertexArray(self.vao)

        # Upload vertex data
        vertex_data = np.ascontiguousarray(vertices, dtype=np.float32)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, vertex_data.nbytes, vertex_data, GL_STATIC_DRAW)

        # Upload index data if present
        if self.is_indexed and self.ebo is not None:
            index_data = np.ascontiguousarray(indices, dtype=np.uint32)
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo)
            glBufferData(GL_ELEMENT_ARRAY_BUFFER, index_data.nbytes, index_data, GL_STATIC_DRAW)

        # Compute total stride if not provided
        float_size = ctypes.sizeof(ctypes.c_float)
        if stride is None:
            total_elements = sum(attr.size for attr in attributes)
            stride_bytes = total_elements * float_size
        else:
            stride_bytes = stride

        # Configure vertex attributes
        offset = 0
        for attr in attributes:
            glEnableVertexAttribArray(attr.location)
            glVertexAttribPointer(
                attr.location,
                attr.size,
                attr.type,
                attr.normalized,
                stride_bytes,
                ctypes.c_void_p(offset)
            )
            offset += attr.size * float_size

        # Unbind VAO (do NOT unbind EBO while VAO is bound)
        glBindVertexArray(0)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

    def draw(self, mode: int = GL_TRIANGLES) -> None:
        """Binds the VAO and executes the appropriate draw call."""
        glBindVertexArray(self.vao)
        if self.is_indexed:
            glDrawElements(mode, self.index_count, GL_UNSIGNED_INT, None)
        else:
            glDrawArrays(mode, 0, self.vertex_count)
        glBindVertexArray(0)

    def delete(self) -> None:
        """Cleans up GPU buffers and vertex array."""
        if self.vbo:
            glDeleteBuffers(1, [self.vbo])
            self.vbo = 0
        if self.ebo:
            glDeleteBuffers(1, [self.ebo])
            self.ebo = None
        if self.vao:
            glDeleteVertexArrays(1, [self.vao])
            self.vao = 0
