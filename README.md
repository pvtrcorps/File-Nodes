# File Nodes

File Nodes es un prototipo de addon para Blender que extiende el paradigma procedural hacia la gestión de archivos y datablocks. Su objetivo es permitir flujos de trabajo nodales que lean, combinen y apliquen datos de múltiples archivos `.blend` de forma no destructiva.

## Objetivos del MVP
- Crear un nuevo `NodeTree` personalizado.
- Implementar nodos básicos para leer y manipular datablocks.
- Integrar una pila de *modificadores de archivo* a nivel de `Scene`.

## Nodos principales
- **Group Input**: expone datablocks del archivo actual.
- **Read Blend File**: importa escenas, colecciones, objetos y mundos desde archivos externos.
- **Create List** y **Get Item by Name**: operan sobre listas de datablocks.
- **Set World to Scene**: ejemplo de nodo de acción que modifica una `Scene`.

## Arquitectura general
1. **NodeTree personalizado**: contenedor del grafo.
2. **Nodos**: clases que heredan de `bpy.types.Node`.
3. **Sockets**: tipos propios para listas de objetos, escenas, etc.
4. **File Modifiers**: colección en `Scene` que permite apilar varios grafos.

## Modelo de ejecución
Los nodos se evalúan de forma determinista sin almacenar estado entre ejecuciones. Antes de calcular cada grafo se restauran los valores originales de la escena. Esto asegura que los mismos inputs producen siempre los mismos resultados.

## Gestión de datablocks
- Los datos externos se vinculan mediante *library linking* para mantener la no destructividad.
- Se recomienda marcar los `NodeTree` con *Fake User* para no perderlos al cerrar el archivo.
- Al desactivar un modificador se restauran los valores previos de la escena.

## Requisitos
- Blender 4.4 o superior.
- Python 3.10 o superior.

## Conclusión
File Nodes sienta las bases para gestionar escenas y recursos de varios archivos con un enfoque nodal. Aunque este MVP es limitado, abre la puerta a expandir el concepto de **Everything Nodes** también a la organización de proyectos.

