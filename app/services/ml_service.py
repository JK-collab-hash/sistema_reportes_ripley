import os
import joblib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report
from sklearn.cluster import DBSCAN, MeanShift
from sklearn.preprocessing import StandardScaler


BASE_STATIC_IMG = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "img")
ARTIFACT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "ml_artifacts")
os.makedirs(BASE_STATIC_IMG, exist_ok=True)
os.makedirs(ARTIFACT_DIR, exist_ok=True)

CATEGORIAS_ML = ["Ropa", "Electrodoméstico", "Tecnología", "Alimentos", "Muebles"]
ROTACIONES_ML = ["Baja", "Media", "Alta"]
TIPOS_CAMION_ML = ["Camión 01", "Camión 03", "Camión 05", "Camión 06"]

def detectar_anomalias_dbscan(df):
    # Escalar los datos es obligatorio para algoritmos basados en distancia
    scaler = StandardScaler()
    datos_escalados = scaler.fit_transform(df[['cantidad_total', 'tiempo_reposicion_dias']])

    dbscan = DBSCAN(eps=0.5, min_samples=5)
    df['anomalia_dbscan'] = dbscan.fit_predict(datos_escalados)
    return df # Los valores -1 son anomalías

def agrupar_comportamiento_meanshift(df):
    # Escalar datos continuos
    scaler = StandardScaler()
    datos_escalados = scaler.fit_transform(df[['cantidad_total', 'demanda_semanal']])
    
    ms = MeanShift()
    df['cluster_meanshift'] = ms.fit_predict(datos_escalados)
    return df

def crear_dataset_ml(n=1500):
    np.random.seed(42)

    df = pd.DataFrame({
        "categoria": np.random.choice(CATEGORIAS_ML, n),
        "camion": np.random.choice(TIPOS_CAMION_ML, n),
        "cantidad_total": np.random.randint(1, 120, n),
        "numero_productos": np.random.randint(1, 8, n),
        "stock_estimado": np.random.randint(5, 180, n),
        "stock_minimo": np.random.randint(10, 60, n),
        "demanda_semanal": np.random.randint(10, 160, n),
        "unidades_transito": np.random.randint(0, 100, n),
        "tiempo_reposicion_dias": np.random.randint(1, 20, n),
        "dias_sin_reposicion": np.random.randint(1, 40, n),
        "tiene_incidencia": np.random.choice([0, 1], n, p=[0.78, 0.22]),
        "rotacion_producto": np.random.choice(ROTACIONES_ML, n)
    })

    df["riesgo_operativo"] = np.where(
        (df["stock_estimado"] < df["stock_minimo"]) |
        (df["demanda_semanal"] > df["stock_estimado"] + df["unidades_transito"]) |
        ((df["cantidad_total"] > 60) & (df["tiempo_reposicion_dias"] > 8)) |
        ((df["rotacion_producto"] == "Alta") & (df["stock_estimado"] < 45)) |
        ((df["tiene_incidencia"] == 1) & (df["cantidad_total"] > 25)) |
        ((df["dias_sin_reposicion"] > 25) & (df["stock_estimado"] < 70)),
        "Riesgo",
        "Normal"
    )
    return df


def preparar_datos_ml(df):
    df_modelo = df.copy()
    # Eliminar columnas de clustering antes de entrenar el árbol de decisión
    if 'anomalia_dbscan' in df_modelo.columns:
        df_modelo = df_modelo.drop(columns=['anomalia_dbscan'])
    if 'cluster_meanshift' in df_modelo.columns:
        df_modelo = df_modelo.drop(columns=['cluster_meanshift'])

    df_modelo["riesgo_operativo"] = df_modelo["riesgo_operativo"].map({"Normal": 0, "Riesgo": 1})
    X = df_modelo.drop(columns=["riesgo_operativo"])
    y = df_modelo["riesgo_operativo"]
    X = pd.get_dummies(X, drop_first=True)
    return X, y


def entrenar_modelo_ml(force=False):
    model_path = os.path.join(ARTIFACT_DIR, "modelo_riesgo_operativo.pkl")
    columns_path = os.path.join(ARTIFACT_DIR, "columnas_modelo.pkl")

    df = crear_dataset_ml()
    
    # ¡NUEVO! Aplicar algoritmos no supervisados al dataset generado
    df = detectar_anomalias_dbscan(df)
    df = agrupar_comportamiento_meanshift(df)

    X, y = preparar_datos_ml(df)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.30, random_state=42, stratify=y
    )

    modelo = DecisionTreeClassifier(
        criterion="gini",
        max_depth=6,
        min_samples_split=20,
        min_samples_leaf=8,
        random_state=42
    )
    modelo.fit(X_train, y_train)
    y_pred = modelo.predict(X_test)

    metricas = {
        "accuracy": accuracy_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred),
        "recall": recall_score(y_test, y_pred),
        "f1": f1_score(y_test, y_pred),
        "matriz": confusion_matrix(y_test, y_pred),
        "reporte_texto": classification_report(y_test, y_pred, target_names=["Normal", "Riesgo"]),
    }

    importancia = pd.DataFrame({
        "Variable": X.columns,
        "Importancia": modelo.feature_importances_
    }).sort_values(by="Importancia", ascending=False)

    joblib.dump(modelo, model_path)
    joblib.dump(list(X.columns), columns_path)
    df.to_csv(os.path.join(ARTIFACT_DIR, "dataset_ml_ripley.csv"), index=False)
    importancia.to_csv(os.path.join(ARTIFACT_DIR, "importancia_variables.csv"), index=False)

    generar_graficos_ml(df, importancia, metricas)

    return {
        "modelo": modelo,
        "columnas": list(X.columns),
        "dataset": df,
        "metricas": metricas,
        "importancia": importancia,
        "total_anomalias": int((df['anomalia_dbscan'] == -1).sum()),
        "total_clusters": int(df['cluster_meanshift'].nunique())
    }


def generar_graficos_ml(df, importancia, metricas):
    conteo = df["riesgo_operativo"].value_counts()
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(conteo.index, conteo.values)
    ax.set_title("Distribución del riesgo operativo")
    ax.set_xlabel("Estado")
    ax.set_ylabel("Cantidad")
    fig.tight_layout()
    fig.savefig(os.path.join(BASE_STATIC_IMG, "ml_distribucion_riesgo.png"))
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.hist(df["cantidad_total"], bins=20)
    ax.set_title("Histograma de cantidad total")
    ax.set_xlabel("Cantidad total")
    ax.set_ylabel("Frecuencia")
    fig.tight_layout()
    fig.savefig(os.path.join(BASE_STATIC_IMG, "ml_hist_cantidad.png"))
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.boxplot(df["tiempo_reposicion_dias"], vert=False)
    ax.set_title("Boxplot del tiempo de reposición")
    ax.set_xlabel("Días")
    fig.tight_layout()
    fig.savefig(os.path.join(BASE_STATIC_IMG, "ml_boxplot_reposicion.png"))
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.scatter(df["stock_estimado"], df["demanda_semanal"], alpha=0.55)
    ax.set_title("Stock estimado vs demanda semanal")
    ax.set_xlabel("Stock estimado")
    ax.set_ylabel("Demanda semanal")
    fig.tight_layout()
    fig.savefig(os.path.join(BASE_STATIC_IMG, "ml_stock_demanda.png"))
    plt.close(fig)

    corr = df.select_dtypes(include=["number"]).corr()
    fig, ax = plt.subplots(figsize=(8, 6))
    im = ax.imshow(corr)
    fig.colorbar(im)
    ax.set_xticks(range(len(corr.columns)))
    ax.set_yticks(range(len(corr.columns)))
    ax.set_xticklabels(corr.columns, rotation=90)
    ax.set_yticklabels(corr.columns)
    ax.set_title("Matriz de correlación")
    fig.tight_layout()
    fig.savefig(os.path.join(BASE_STATIC_IMG, "ml_correlacion.png"))
    plt.close(fig)

    top = importancia.head(10).sort_values(by="Importancia")
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.barh(top["Variable"], top["Importancia"])
    ax.set_title("Variables más importantes")
    ax.set_xlabel("Importancia")
    fig.tight_layout()
    fig.savefig(os.path.join(BASE_STATIC_IMG, "ml_importancia.png"))
    plt.close(fig)

    matriz = metricas["matriz"]
    fig, ax = plt.subplots(figsize=(5, 4))
    im = ax.imshow(matriz)
    fig.colorbar(im)
    ax.set_xticks([0, 1])
    ax.set_yticks([0, 1])
    ax.set_xticklabels(["Normal", "Riesgo"])
    ax.set_yticklabels(["Normal", "Riesgo"])
    ax.set_xlabel("Predicción")
    ax.set_ylabel("Valor real")
    ax.set_title("Matriz de confusión")
    for i in range(matriz.shape[0]):
        for j in range(matriz.shape[1]):
            ax.text(j, i, matriz[i, j], ha="center", va="center")
    fig.tight_layout()
    fig.savefig(os.path.join(BASE_STATIC_IMG, "ml_matriz_confusion.png"))
    plt.close(fig)

    # Gráfico DBSCAN (Detección de Anomalías)
    fig, ax = plt.subplots(figsize=(7, 4))
    colores_dbscan = np.where(df['anomalia_dbscan'] == -1, 'red', 'blue')
    ax.scatter(df['cantidad_total'], df['tiempo_reposicion_dias'], c=colores_dbscan, alpha=0.6)
    ax.set_title("Detección de Anomalías Logísticas (DBSCAN)")
    ax.set_xlabel("Cantidad Total")
    ax.set_ylabel("Tiempo de Reposición (Días)")
    fig.tight_layout()
    fig.savefig(os.path.join(BASE_STATIC_IMG, "ml_dbscan_anomalias.png"))
    plt.close(fig)

    # Gráfico Mean-Shift (Agrupamiento)
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.scatter(df['cantidad_total'], df['demanda_semanal'], c=df['cluster_meanshift'], cmap='viridis', alpha=0.6)
    ax.set_title("Agrupación de Mercadería (Mean-Shift)")
    ax.set_xlabel("Cantidad Total")
    ax.set_ylabel("Demanda Semanal")
    fig.tight_layout()
    fig.savefig(os.path.join(BASE_STATIC_IMG, "ml_meanshift_clusters.png"))
    plt.close(fig)


def obtener_modelo_ml():
    return entrenar_modelo_ml()


def predecir(datos):
    obj = obtener_modelo_ml()
    modelo = obj["modelo"]
    columnas = obj["columnas"]

    df = pd.DataFrame([datos])
    df_codificado = pd.get_dummies(df, drop_first=True)
    df_codificado = df_codificado.reindex(columns=columnas, fill_value=0)

    pred = modelo.predict(df_codificado)[0]
    proba = modelo.predict_proba(df_codificado)[0]
    return {
        "clase": "Riesgo" if pred == 1 else "Normal",
        "prob_normal": float(proba[0]),
        "prob_riesgo": float(proba[1]),
    }


def predecir_riesgo_desde_reporte(reporte):
    if not reporte.detalles:
        return {"clase": "Normal", "prob_normal": 1.0, "prob_riesgo": 0.0}

    detalle_base = reporte.detalles[0]
    cantidad_total = sum(d.cantidad for d in reporte.detalles)
    numero_productos = len(reporte.detalles)
    tiene_incidencia = 1 if (reporte.incidencias and reporte.incidencias.strip()) else 0

    # Variables estimadas para la demostración académica del módulo inteligente.
    stock_estimado = max(5, 160 - cantidad_total)
    stock_minimo = 35
    demanda_semanal = min(160, cantidad_total * 3)
    unidades_transito = 25
    tiempo_reposicion_dias = 9 if tiene_incidencia else 5
    dias_sin_reposicion = 16 if cantidad_total < 40 else 27
    rotacion_producto = "Alta" if cantidad_total >= 24 else "Media"

    datos = {
        "categoria": detalle_base.categoria.nombre,
        "camion": reporte.camion.nombre,
        "cantidad_total": cantidad_total,
        "numero_productos": numero_productos,
        "stock_estimado": stock_estimado,
        "stock_minimo": stock_minimo,
        "demanda_semanal": demanda_semanal,
        "unidades_transito": unidades_transito,
        "tiempo_reposicion_dias": tiempo_reposicion_dias,
        "dias_sin_reposicion": dias_sin_reposicion,
        "tiene_incidencia": tiene_incidencia,
        "rotacion_producto": rotacion_producto,
    }
    return predecir(datos)