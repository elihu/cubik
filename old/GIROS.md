# Lógica de los giros de las caras adyacentes:

## Giro Horario de la Cara F (Frontal)
Cuando giramos la cara F en sentido horario, las piezas de los bordes de las caras U (Arriba), R (Derecha), D (Abajo) y L (Izquierda) se mueven en un ciclo. Aquí están los cambios exactos de posición entre las caras adyacentes:

| Posición Original | Nueva Posición | Descripción |
|-------------------|---------------|-------------|
| U1.0              | R0.0          | La pieza inferior izquierda de U va a la superior izquierda de R. |
| U1.1              | R1.0          | La pieza inferior derecha de U va a la inferior izquierda de R. |
| R0.0              | D0.1          | La pieza superior izquierda de R va a la superior derecha de D. |
| R1.0              | D0.0          | La pieza inferior izquierda de R va a la superior izquierda de D. |
| D0.0              | L0.1          | La pieza superior izquierda de D va a la superior derecha de L. |
| D0.1              | L1.1          | La pieza superior derecha de D va a la inferior derecha de L. |
| L0.1              | U1.1          | La pieza superior derecha de L va a la inferior derecha de U. |
| L1.1              | U1.0          | La pieza inferior derecha de L va a la inferior izquierda de U. |

## Giro Antihorario de la Cara F (Frontal)
Cuando giramos la cara F en sentido antihorario, las piezas de los bordes de las caras U (Arriba), L (Izquierda), D (Abajo) y R (Derecha) se mueven en un ciclo inverso al giro horario. Aquí están los cambios de posición que propongo:

|-------------------|---------------|-------------|
| Posición Original | Nueva Posición | Descripción |
|-------------------|---------------|-------------|
| U1.0              | L1.1          | La pieza inferior izquierda de U va a la inferior derecha de L. |
| U1.1              | L0.1          | La pieza inferior derecha de U va a la superior derecha de L. |
| L0.1              | D0.0          | La pieza superior derecha de L va a la superior izquierda de D. |
| L1.1              | D0.1          | La pieza inferior derecha de L va a la superior derecha de D. |
| D0.0              | R1.0          | La pieza superior izquierda de D va a la inferior izquierda de R. |
| D0.1              | R0.0          | La pieza superior derecha de D va a la superior izquierda de R. |
| R0.0              | U1.0          | La pieza superior izquierda de R va a la inferior izquierda de U. |
| R1.0              | U1.1          | La pieza inferior izquierda de R va a la inferior derecha de U. |

## Giro Horario de la Cara U (Arriba)
Cuando giramos la cara U en sentido horario, las piezas de la fila superior (fila 0) de las caras adyacentes F (Frontal), L (Izquierda), B (Atrás) y R (Derecha) se mueven en un ciclo. El flujo correcto es: F → L → B → R → F.

Aquí están los cambios exactos de posición entre las caras adyacentes:

| Posición Original | Nueva Posición | Descripción |
|-------------------|---------------|-------------|
| F0.0              | L0.0          | La pieza superior izquierda de F va a la superior izquierda de L. |
| F0.1              | L0.1          | La pieza superior derecha de F va a la superior derecha de L. |
| L0.0              | B0.0          | La pieza superior izquierda de L va a la superior izquierda de B. |
| L0.1              | B0.1          | La pieza superior derecha de L va a la superior derecha de B. |
| B0.0              | R0.0          | La pieza superior izquierda de B va a la superior izquierda de R. |
| B0.1              | R0.1          | La pieza superior derecha de B va a la superior derecha de R. |
| R0.0              | F0.0          | La pieza superior izquierda de R va a la superior izquierda de F. |
| R0.1              | F0.1          | La pieza superior derecha de R va a la superior derecha de F. |


## Giro Antihorario de la Cara U (Arriba)
Cuando giramos la cara U en sentido antihorario, las piezas de la fila superior (fila 0) de las caras adyacentes F (Frontal), R (Derecha), B (Atrás) y L (Izquierda) se mueven en un ciclo inverso al giro horario. El flujo correcto es: F → R → B → L → F.

Aquí están los cambios exactos de posición entre las caras adyacentes:

| Posición Original | Nueva Posición | Descripción |
|-------------------|---------------|-------------|
| F0.0              | R0.0          | La pieza superior izquierda de F va a la superior izquierda de R. |
| F0.1              | R0.1          | La pieza superior derecha de F va a la superior derecha de R. |
| R0.0              | B0.0          | La pieza superior izquierda de R va a la superior izquierda de B. |
| R0.1              | B0.1          | La pieza superior derecha de R va a la superior derecha de B. |
| B0.0              | L0.0          | La pieza superior izquierda de B va a la superior izquierda de L. |
| B0.1              | L0.1          | La pieza superior derecha de B va a la superior derecha de L. |
| L0.0              | F0.0          | La pieza superior izquierda de L va a la superior izquierda de F. |
| L0.1              | F0.1          | La pieza superior derecha de L va a la superior derecha de F. |

## Giro Horario de la Cara D (Abajo)
Cuando giramos la cara D en sentido horario, las piezas de la fila inferior (fila 1) de las caras adyacentes F (Frontal), R (Derecha), B (Atrás) y L (Izquierda) se mueven en un ciclo. El flujo correcto es: F → R → B → L → F.

Aquí están los cambios exactos de posición entre las caras adyacentes:

| Posición Original | Nueva Posición | Descripción |
|-------------------|---------------|-------------|
| F1.0              | R1.0          | La pieza inferior izquierda de F va a la inferior izquierda de R. |
| F1.1              | R1.1          | La pieza inferior derecha de F va a la inferior derecha de R. |
| R1.0              | B1.0          | La pieza inferior izquierda de R va a la inferior izquierda de B. |
| R1.1              | B1.1          | La pieza inferior derecha de R va a la inferior derecha de B. |
| B1.0              | L1.0          | La pieza inferior izquierda de B va a la inferior izquierda de L. |
| B1.1              | L1.1          | La pieza inferior derecha de B va a la inferior derecha de L. |
| L1.0              | F1.0          | La pieza inferior izquierda de L va a la inferior izquierda de F. |
| L1.1              | F1.1          | La pieza inferior derecha de L va a la inferior derecha de F. |

## Giro Antihorario de la Cara D (Abajo)
Cuando giramos la cara D en sentido antihorario, las piezas de la fila inferior (fila 1) de las caras adyacentes F (Frontal), L (Izquierda), B (Atrás) y R (Derecha) se mueven en un ciclo inverso al giro horario. El flujo correcto es: F → L → B → R → F.

Aquí están los cambios exactos de posición entre las caras adyacentes:

| Posición Original | Nueva Posición | Descripción |
|-------------------|---------------|-------------|
| F1.0              | L1.0          | La pieza inferior izquierda de F va a la inferior izquierda de L. |
| F1.1              | L1.1          | La pieza inferior derecha de F va a la inferior derecha de L. |
| L1.0              | B1.0          | La pieza inferior izquierda de L va a la inferior izquierda de B. |
| L1.1              | B1.1          | La pieza inferior derecha de L va a la inferior derecha de B. |
| B1.0              | R1.0          | La pieza inferior izquierda de B va a la inferior izquierda de R. |
| B1.1              | R1.1          | La pieza inferior derecha de B va a la inferior derecha de R. |
| R1.0              | F1.0          | La pieza inferior izquierda de R va a la inferior izquierda de F. |
| R1.1              | F1.1          | La pieza inferior derecha de R va a la inferior derecha de F. |
