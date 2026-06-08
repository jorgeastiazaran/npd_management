# NPD Management (Gestión de Desarrollo de Nuevos Productos)

Una aplicación integral y robusta para **ERPNext** diseñada específicamente para orquestar y controlar todo el ciclo de vida de **Desarrollo de Nuevos Productos (NPD)** en industrias de alimentos, bebidas y manufactura.

## 📖 Descripción Detallada

La aplicación **NPD Management** extiende las capacidades de ERPNext proporcionando flujos de trabajo dedicados para transformar una simple idea en un producto comercialmente viable y listo para su lanzamiento. 

El sistema gestiona de manera centralizada la viabilidad técnica y financiera, las iteraciones de formulación, las cotizaciones de insumos, las inspecciones de calidad, y las pruebas piloto, asegurando que todos los departamentos (I+D, Finanzas, Calidad, Compras y Producción) estén alineados bajo una misma fuente de verdad.

### Características Principales:
- **Gestión de Ideas (NPD Idea):** Recolección, evaluación preliminar y aprobación de nuevas ideas de productos.
- **Formulación e Iteraciones (NPD Formula):** Control de versiones y recetas para el departamento de I+D, incluyendo el manejo de perfiles nutricionales y alérgenos de cada ingrediente.
- **Rollup Nutricional Automático:** Cálculo dinámico del perfil nutricional de una fórmula a partir de los valores de sus ingredientes.
- **Pruebas de Calidad (NPD Quality Inspection):** Registro detallado de catas, análisis organolépticos y pruebas de vida de anaquel.
- **Gestión de Proveedores (NPD Sourcing):** Control de cotizaciones, hojas técnicas y estatus de los ingredientes clave de manera independiente al módulo nativo de compras, ideal para la fase de prototipado.
- **Pruebas Piloto y Escalamiento (NPD Trial):** Planificación, ejecución y documentación fotográfica/financiera de lotes piloto y corridas industriales.
- **Validaciones Regulatorias (NPD Compliance):** Rastreo de normativas, certificaciones (ej. Orgánico, Kosher) y validación de etiquetado.

## 💻 Requisitos del Sistema

- **Framework Frappe:** Versión 13.
- **ERPNext:** Versión 13.
- **Python:** 3.7 o superior.
- **Node.js:** 14+ (para assets).
- **Redis & MariaDB:** Estándares del ecosistema Frappe.

## ⚙️ Instrucciones de Instalación

Para instalar `npd_management` en tu servidor o entorno local, sigue estos pasos desde la consola de tu usuario `frappe`:

### 1. Obtener la aplicación
Descarga la aplicación a tu entorno de bench:
```bash
bench get-app https://github.com/jorgeastiazaran/npd_management.git
```

### 2. Instalar en tu Sitio
Asegúrate de saber el nombre del sitio de ERPNext donde deseas instalar el módulo (por ejemplo, `misitio.localhost`) e instálalo:
```bash
bench --site misitio.localhost install-app npd_management
```

### 3. Ejecutar Migraciones (Requerido)
Para asegurar que todos los Custom Fields, DocTypes personalizados y lógicas internas se inyecten correctamente en la base de datos:
```bash
bench --site misitio.localhost migrate
```

### 4. Limpiar Caché y Reiniciar
```bash
bench --site misitio.localhost clear-cache
bench restart
# Si usas docker-compose: docker-compose restart erpnext
```

## 🚀 Uso Rápido

1. Inicia sesión en ERPNext con permisos de Administrador o con un rol de "NPD Manager".
2. Busca la sección o Workspace de **NPD Management** en el menú lateral.
3. Comienza creando un nuevo registro en **NPD Idea** para evaluar una oportunidad de mercado.
4. Una vez aprobada, conviértela en un **NPD Project** para rastrear todo el ciclo de formulación y pruebas.

## 🛠 Soporte y Contribución
Para reportar fallos, problemas o solicitar nuevas características, por favor abre un _Issue_ en el repositorio de GitHub de este proyecto.
