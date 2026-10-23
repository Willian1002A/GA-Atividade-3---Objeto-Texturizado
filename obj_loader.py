import os
import ctypes
import numpy as np
from PIL import Image
from OpenGL.GL import *


def parse_mtl(mtl_path):
    if not mtl_path or not os.path.exists(mtl_path):
        return None

    mtl_dir = os.path.dirname(mtl_path)
    with open(mtl_path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            parts = line.strip().split()
            if not parts or parts[0].startswith("#"):
                continue
            if parts[0] == "map_Kd" and len(parts) >= 2:
                texture_filename = " ".join(parts[1:])
                return os.path.join(mtl_dir, texture_filename)
    return None


def load_texture(image_path):
    """Carrega a imagem de textura usando Pillow e gera a textura no OpenGL."""
    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id)

    # Se a textura existir, carrega com Pillow; senão, cria textura branca 1x1
    if image_path and os.path.exists(image_path):
        img = Image.open(image_path).transpose(Image.Transpose.FLIP_TOP_BOTTOM).convert("RGBA")
        width, height = img.size
        data = img.tobytes()
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, data)
        glGenerateMipmap(GL_TEXTURE_2D)
    else:
        white_pixel = np.array([255, 255, 255, 255], dtype=np.uint8)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, 1, 1, 0, GL_RGBA, GL_UNSIGNED_BYTE, white_pixel)

    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glBindTexture(GL_TEXTURE_2D, 0)
    return texture_id


def load_obj(obj_path):
    positions = []
    texcoords = []
    vertices = []
    mtl_filename = None

    with open(obj_path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            parts = line.strip().split()
            if not parts or parts[0].startswith("#"):
                continue

            tag = parts[0]
            if tag == "mtllib":
                mtl_filename = " ".join(parts[1:])
            elif tag == "v":
                positions.append([float(parts[1]), float(parts[2]), float(parts[3])])
            elif tag == "vt":
                texcoords.append([float(parts[1]), float(parts[2])])
            elif tag == "f":
                face_tokens = parts[1:]
                for i in range(1, len(face_tokens) - 1):
                    tri = [face_tokens[0], face_tokens[i], face_tokens[i + 1]]

                    for tok in tri:
                        vals = tok.split("/")
                        p_idx = int(vals[0]) - 1 if int(vals[0]) > 0 else len(positions) + int(vals[0])
                        p = positions[p_idx]

                        uv = [0.0, 0.0]
                        if len(vals) > 1 and vals[1]:
                            uv_idx = int(vals[1]) - 1 if int(vals[1]) > 0 else len(texcoords) + int(vals[1])
                            uv = texcoords[uv_idx]

                        vertices.extend([p[0], p[1], p[2], uv[0], uv[1]])

    data = np.array(vertices, dtype=np.float32)
    vertex_count = len(data) // 5


    vao = glGenVertexArrays(1)
    vbo = glGenBuffers(1)

    glBindVertexArray(vao)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, data.nbytes, data, GL_STATIC_DRAW)

    stride = 5 * ctypes.sizeof(ctypes.c_float)
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))

    glEnableVertexAttribArray(1)
    glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(12))

    glBindVertexArray(0)
    glBindBuffer(GL_ARRAY_BUFFER, 0)

    return vao, vertex_count, mtl_filename