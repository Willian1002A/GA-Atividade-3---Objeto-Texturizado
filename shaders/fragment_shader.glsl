#version 330 core
in vec3 FragPos;
in vec3 Normal;
in vec2 TexCoords;

out vec4 FragColor;

struct Light {
    bool enabled;
    vec3 position;
    vec3 ambient;
    vec3 diffuse;
    vec3 specular;
    float constant;
    float linear;
    float quadratic;
};

struct Material {
    vec3 Ka;
    vec3 Kd;
    vec3 Ks;
    float shininess;
};

uniform Light lights[3];
uniform Material material;
uniform vec3 viewPos;
uniform sampler2D texture_diffuse;
uniform bool useTexture;

void main()
{
    vec3 norm = normalize(Normal);
    vec3 viewDir = normalize(viewPos - FragPos);
    vec3 baseColor = useTexture ? texture(texture_diffuse, TexCoords).rgb : vec3(1.0);

    vec3 totalLight = vec3(0.0);

    for (int i = 0; i < 3; ++i) {
        if (!lights[i].enabled) continue;

        vec3 lightDir = normalize(lights[i].position - FragPos);

        // Atenuação por distância
        float distance = length(lights[i].position - FragPos);
        float attenuation = 1.0 / (lights[i].constant + lights[i].linear * distance + lights[i].quadratic * (distance * distance));

        // 1. Componente Ambiente
        vec3 ambient = lights[i].ambient * material.Ka * baseColor;

        // 2. Componente Difusa
        float diff = max(dot(norm, lightDir), 0.0);
        vec3 diffuse = lights[i].diffuse * (diff * material.Kd) * baseColor;

        // 3. Componente Especular
        vec3 reflectDir = reflect(-lightDir, norm);
        float spec = pow(max(dot(viewDir, reflectDir), 0.0), max(material.shininess, 1.0));
        vec3 specular = lights[i].specular * (spec * material.Ks);

        // Aplica atenuação nas parcelas difusa e especular
        diffuse *= attenuation;
        specular *= attenuation;

        totalLight += ambient + diffuse + specular;
    }

    FragColor = vec4(clamp(totalLight, 0.0, 1.0), 1.0);
}