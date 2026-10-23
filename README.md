# Atividade 3 - Objeto Texturizado (Computação Gráfica)

Aplicação desenvolvida em Python com PyOpenGL e GLFW para leitura de malhas Wavefront (`.obj` e `.mtl`), extração de coordenadas de textura (`vt`), carregamento de imagens e renderização de objetos texturizados.

## Execução e Setup

1. Instalar as dependências:
```bash
pip install -r requirements.txt

```

2. Executar a aplicação:

```bash
python main.py

```

## Controles

* **ESC:** Encerra a aplicação.

## Estrutura do Projeto

* **main.py:** Inicialização do GLFW, criação da janela, gerenciamento do loop gráfico e matrizes MVP.
* **obj_loader.py:** Parser para leitura de vértices (`v`), coordenadas de textura (`vt`), leitura do arquivo de material (`.mtl`) via `map_Kd` e criação dos buffers (VAO/VBO).
* **shader.py:** Classe utilitária para leitura, compilação e gerenciamento de Shaders GLSL.
* **shaders/vertex_shader.glsl:** Pipeline geométrico e repasse das coordenadas UV.
* **shaders/fragment_shader.glsl:** Amostragem da textura 2D no fragmento.
* **requirements.txt:** Lista de dependências (PyOpenGL, GLFW, PyGLM, Pillow, Numpy).
