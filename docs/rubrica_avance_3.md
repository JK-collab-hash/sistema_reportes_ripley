# Relación del proyecto con la rúbrica del Avance 3

## 1. Descripción técnica de la solución
La solución es un sistema web de reportes de garita para registrar ingresos de mercadería por camión. Incluye un módulo inteligente de Machine Learning que predice riesgo operativo.

## 2. Obtención y descripción del conjunto de datos
El dataset del módulo ML se genera de forma simulada con variables de stock, demanda, reposición, cantidad, incidencias, camión y categoría.

## 3. Análisis exploratorio de datos
El panel ML muestra:
- Distribución del riesgo operativo.
- Histograma de cantidad total.
- Boxplot del tiempo de reposición.
- Gráfico de dispersión entre stock y demanda.
- Matriz de correlación.

## 4. Preparación y limpieza de datos
El servicio `ml_service.py` convierte la variable objetivo a formato numérico y codifica variables categóricas mediante `get_dummies`.

## 5. Implementación del modelo ML
Se usa Árbol de Decisión porque permite clasificar y explicar las condiciones que generan riesgo operativo.

## 6. Evaluación del modelo
El panel muestra:
- Accuracy.
- Precision.
- Recall.
- F1 Score.
- Matriz de confusión.

## 7. Interpretación de resultados
El panel muestra las variables más importantes del modelo, permitiendo explicar qué factores influyen en el riesgo operativo.

## 8. Impacto en transformación digital
La solución transforma un registro operativo manual en una gestión digital, trazable y predictiva, apoyando decisiones logísticas y reduciendo riesgos por quiebre de stock o incidencias.
