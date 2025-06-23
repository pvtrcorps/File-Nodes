# Addendum: Evaluación en vivo

La versión actual de File Nodes modifica directamente la escena activa durante la ejecución de cada grafo. Los modificadores registran los valores originales de los datablocks que afectan y, antes de cada evaluación, restauran dicho estado para garantizar resultados deterministas. De este modo se evita duplicar escenas temporales y se mantiene la naturaleza no destructiva del flujo.
