#version 330 core

// Vertex Attributes
layout (location = 0) in vec3 aPos;
layout (location = 1) in vec3 aColor;
layout (location = 2) in vec3 aNormal;

// Uniform Transformation Matrices
uniform mat4 uModel;
uniform mat4 uView;
uniform mat4 uProjection;

// Varying Outputs to Fragment Shader
out vec3 FragPos;
out vec3 VertexColor;
out vec3 Normal;
out float WorldPosY;

void main()
{
    // Compute world-space position
    vec4 worldPos = uModel * vec4(aPos, 1.0);
    FragPos = vec3(worldPos);
    WorldPosY = worldPos.y;

    // Compute normal matrix to preserve direction under non-uniform scaling
    mat3 normalMatrix = mat3(transpose(inverse(uModel)));
    Normal = normalize(normalMatrix * aNormal);

    // Pass-through interpolated color
    VertexColor = aColor;

    // Projected clip space position
    gl_Position = uProjection * uView * worldPos;
}
