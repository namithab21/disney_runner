#version 330 core

// Interpolated inputs from Vertex Shader
in vec3 FragPos;
in vec3 VertexColor;
in vec3 Normal;
in float WorldPosY;

// Lighting & Camera Uniforms
uniform vec3 uLightPos;
uniform vec3 uLightColor;
uniform vec3 uViewPos;

// Atmospheric Distance Fog Uniforms
uniform vec3 uFogColor;
uniform float uFogStart;
uniform float uFogEnd;

out vec4 FragColor;

void main()
{
    // Ambient component with subtle hemisphere tint (sky light vs bounce light)
    vec3 norm = normalize(Normal);
    float hemiFactor = clamp(norm.y * 0.5 + 0.5, 0.0, 1.0);
    vec3 skyAmbient = vec3(0.42, 0.44, 0.50) * uLightColor;
    vec3 groundAmbient = vec3(0.20, 0.18, 0.16) * uLightColor;
    vec3 ambient = mix(groundAmbient, skyAmbient, hemiFactor);

    // Diffuse component (Lambertian with wrap-around light for softer shadows)
    vec3 lightDir = normalize(uLightPos - FragPos);
    float NdotL = dot(norm, lightDir);
    float diff = max(NdotL, 0.0);
    // Subtle wrap lighting
    float wrappedDiff = clamp((NdotL + 0.2) / 1.2, 0.0, 1.0);
    vec3 diffuse = (diff * 0.8 + wrappedDiff * 0.2) * uLightColor;

    // Specular component (Blinn-Phong)
    float specularStrength = 0.35;
    vec3 viewDir = normalize(uViewPos - FragPos);
    vec3 halfwayDir = normalize(lightDir + viewDir);
    float spec = pow(max(dot(norm, halfwayDir), 0.0), 32.0);
    vec3 specular = specularStrength * spec * uLightColor;

    // Subtle Rim Lighting (Disney style glow on edges)
    float rimFactor = 1.0 - max(dot(viewDir, norm), 0.0);
    rimFactor = pow(clamp(rimFactor, 0.0, 1.0), 3.0);
    vec3 rim = rimFactor * 0.25 * uLightColor;

    // Combined lighting with surface color
    vec3 litColor = (ambient + diffuse + specular + rim) * VertexColor;

    // Contact ambient shadow near road plane (y close to 0)
    if (WorldPosY < 0.25 && WorldPosY >= 0.0) {
        float shadowFactor = clamp(WorldPosY / 0.25, 0.65, 1.0);
        litColor *= shadowFactor;
    }

    // Atmospheric Distance Fog calculation
    if (uFogEnd > uFogStart) {
        float dist = length(uViewPos - FragPos);
        float fogFactor = clamp((dist - uFogStart) / (uFogEnd - uFogStart), 0.0, 1.0);
        fogFactor = smoothstep(0.0, 1.0, fogFactor);
        vec3 finalColor = mix(litColor, uFogColor, fogFactor);
        FragColor = vec4(finalColor, 1.0);
    } else {
        FragColor = vec4(litColor, 1.0);
    }
}
