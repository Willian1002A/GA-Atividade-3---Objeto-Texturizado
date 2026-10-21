import os
import ctypes
import numpy as np
from PIL import Image
from OpenGL.GL import *
import glm


def parse_mtl(mtl_path):
    # Valores padrão de material caso o .mtl não exista
    material = {
        "Ka": glm.vec3(0.2, 0.2, 0.2),
        "Kd": glm.vec3(0.8, 0.8, 0.8),
        "Ks": glm.vec3(0.5, 0.5, 0.5),
        "shininess": 32.0,
        "texture_path": None
    }

    if not mtl_path or not os.path.exists(mtl_path):
        return material

    mtl_dir = os.path.dirname(mtl_path)
    with open(mtl_path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            parts = line.strip().split()
            if not parts or parts[0].startswith("#"):
                continue

            tag = parts[0]
            if tag == "Ka" and len(parts) >= 4:
                material["Ka"] = glm.vec3(float(parts[1]), float(parts[2]), float(parts[3]))
            elif tag == "Kd" and len(parts) >= 4:
                material["Kd"] = glm.vec3(float(parts[1]), float(parts[2]), float(parts[3]))
            elif tag == "Ks" and len(parts) >= 4:
                material["Ks"] = glm.vec3(float(parts[1]), float(parts[2]), float(parts[3]))
            elif tag == "Ns" and len(parts) >= 2:
                material["shininess"] = float(parts[1])
            elif tag == "map_Kd" and len(parts) >= 2:
                material["texture_path"] = os.path.join(mtl_dir, " ".join(parts[1:]))

    return material


def load_texture(image_path):
    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id)

    # Se a textura existir, carrega com Pillow; senão, cria textura branca 1x1
    if image_path and os.path.exists(image_path):
        img = Image.open(image_path).transpose(Image.FLIP_TOP_BOTTOM).convert("RGBA")
        width, height = img.size
        data = img.tobytes()
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, data)
        glGenerateMipmap(GL_TEXTURE_2D)
    else:
        white_pixel = np.array([255, 255, 255, 255], dtype=np.uint8)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, 1, 1, 0, GL_RGBA, GL_UNSIGNED_BYTE, white_pixel)

    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR if (image_path and os.path.exists(image_path)) else GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glBindTexture(GL_TEXTURE_2D, 0)
    return texture_id


def load_obj(obj_path):
    positions, texcoords, normals = [], [], []
    vertices = []

    with open(obj_path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            parts = line.strip().split()
            if not parts or parts[0].startswith("#"):
                continue

            tag = parts[0]
            if tag == "v":
                positions.append([float(parts[1]), float(parts[2]), float(parts[3])])
            elif tag == "vt":
                texcoords.append([float(parts[1]), float(parts[2])])
            elif tag == "vn":
                normals.append([float(parts[1]), float(parts[2]), float(parts[3])])
            elif tag == "f":
                face_tokens = parts[1:]
                for i in range(1, len(face_tokens) - 1):
                    tri = [face_tokens[0], face_tokens[i], face_tokens[i + 1]]

                    p_tri, uv_tri, n_tri = [], [], []
                    for tok in tri:
                        vals = tok.split("/")
                        p_idx = int(vals[0]) - 1 if int(vals[0]) > 0 else len(positions) + int(vals[0])
                        p_tri.append(positions[p_idx])

                        uv = texcoords[int(vals[1]) - 1] if len(vals) > 1 and vals[1] else [0.0, 0.0]
                        uv_tri.append(uv)

                        norm = normals[int(vals[2]) - 1] if len(vals) > 2 and vals[2] else None
                        n_tri.append(norm)

                    if n_tri[0] is None:
                        p0, p1, p2 = glm.vec3(*p_tri[0]), glm.vec3(*p_tri[1]), glm.vec3(*p_tri[2])
                        cross_n = glm.normalize(glm.cross(p1 - p0, p2 - p0))
                        calc_norm = [cross_n.x, cross_n.y, cross_n.z]
                    else:
                        calc_norm = [0.0, 1.0, 0.0]

                    for k in range(3):
                        n = n_tri[k] if n_tri[k] is not None else calc_norm
                        p = p_tri[k]
                        uv = uv_tri[k]
                        vertices.extend([p[0], p[1], p[2], n[0], n[1], n[2], uv[0], uv[1]])

    data = np.array(vertices, dtype=np.float32)
    vertex_count = len(data) // 8

    vao = glGenVertexArrays(1)
    vbo = glGenBuffers(1)

    glBindVertexArray(vao)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, data.nbytes, data, GL_STATIC_DRAW)

    stride = 8 * ctypes.sizeof(ctypes.c_float)
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))

    glEnableVertexAttribArray(1)
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(12))

    glEnableVertexAttribArray(2)
    glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(24))

    glBindVertexArray(0)
    glBindBuffer(GL_ARRAY_BUFFER, 0)

    return vao, vbo, vertex_count
