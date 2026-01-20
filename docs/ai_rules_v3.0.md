<!-- /docs/ai_rules_v3.0.md -->

# AI RULES — v3.0

**Reglas oficiales y obligatorias para la IA en el proyecto DemeArizOil**

Este documento define **cómo debe trabajar la IA** en este proyecto.
No describe arquitectura ni negocio: **describe el contrato operativo entre tú y la IA**.

Su objetivo es **eliminar invenciones, simplificaciones implícitas y desviaciones**.

---

## 0. Principio rector

> **La IA no es autónoma en este proyecto.**
> La IA **ejecuta instrucciones bajo contrato**, no interpreta intenciones.

Si algo no está:

* documentado
* autorizado
* o explícitamente pedido

👉 **la IA debe parar y preguntar**.

---

## 1. Documentos fuente obligatorios

La IA **debe cumplir estrictamente**:

1. `architecture_v3.0.md`
2. `ai_rules_v3.0.md`

Cuando exista conflicto:

* **architecture_v3.0.md tiene prioridad técnica**
* **ai_rules_v3.0.md tiene prioridad operativa**

La IA **no puede**:

* contradecirlos
* reinterpretarlos
* “mejorarlos” sin permiso

---

## 2. Modos de trabajo (OBLIGATORIOS)

La IA **solo puede trabajar** si uno de estos modos está activo.
Si el usuario no lo indica explícitamente → **la IA debe parar y pedirlo**.

---

### 🔒 MODO 1 — DOCUMENTACIÓN COMO LEY

**Uso**
Revisión, alineación o verificación de documentos existentes.

**Reglas absolutas**

1. ❌ No crear nada nuevo.
2. ❌ No eliminar nada existente.
3. ❌ No renombrar nada.
4. ❌ No simplificar nada.
5. ✅ Solo:

   * detectar incoherencias
   * señalar contradicciones
   * proponer **correcciones documentales**, no de código
6. Si algo no está documentado → **se marca como hueco**, no se inventa.

**Frase de activación obligatoria**

> “Modo documentación como ley. No inventes nada.”

---

### 🧩 MODO 2 — ADAPTAR A MODELOS EXISTENTES

**Uso**
Cuando los models ya existen y hay que alinear documentación o lógica auxiliar.

**Reglas**

1. Los **models actuales mandan**.
2. ❌ No crear campos nuevos.
3. ❌ No cambiar reglas de negocio.
4. ❌ No introducir nuevas entidades.
5. ✅ Solo se puede modificar:

   * documentación
   * helpers (utils)
6. Si una regla no puede cumplirse con los models actuales → **se señala el conflicto**.

**Frase de activación**

> “Modo adaptar a modelos existentes. No inventes campos ni reglas.”

---

### 🛠️ MODO 3 — CAMBIO CONTROLADO

**Uso**
Cuando **sí** se quiere cambiar comportamiento, estructura o reglas.

**Reglas**

1. **Todo cambio debe enumerarse**.
2. Cada cambio debe indicar:

   * documento afectado
   * punto exacto
   * motivo
3. ❌ Nada implícito.
4. ❌ Nada automático.
5. La IA **no puede aplicar cambios no enumerados**.

**Frase de activación**

> “Modo cambio controlado. Enumera cada modificación.”

---

## 3. Regla crítica de parada

Si la IA detecta **cualquiera** de los siguientes casos:

* Falta de contexto
* Ambigüedad semántica
* Posible invención
* Conflicto entre documentos
* Inconsistencia con `architecture_v3.0.md`

👉 **DEBE PARAR Y PREGUNTAR**.
Continuar sería una violación del contrato.

---

## 4. Prohibiciones absolutas

La IA **NO PUEDE**:

1. Inventar modelos, campos o relaciones.
2. Simplificar capas (“esto se puede quitar”).
3. Fusionar services, controllers o routers.
4. Persistir movimientos.
5. Introducir repositorios, schemas o migraciones.
6. Reordenar carpetas por criterio propio.
7. Cambiar naming rules.
8. Proponer alternativas tecnológicas.
9. Ejecutar lógica de negocio fuera de services.
10. “Arreglar” arquitectura sin modo activo.

---

## 5. Arquitectura (recordatorio obligatorio)

La IA debe respetar siempre:

* Entidades / Aggregates / Documentos → persistentes
* Movimientos → **NO persistentes**
* CRUD obligatorio para Entidades, Aggregates y Documentos
* Stack obligatorio:

  * model
  * service
  * controller
  * router
* Plantillas:

  * Base + Extensión obligatorias
  * Especial solo cuando aplica

Cualquier desviación → **parar**.

---

## 6. Generación de archivos (FORMATO OBLIGATORIO)

Siempre que la IA entregue:

- un documento
- un archivo de código
- una especificación técnica

Debe **envolver el contenido completo** con comentarios que indiquen
**ruta completa y nombre del archivo**, **adaptados al lenguaje del archivo**.

### Formato general

La primera y la última línea **deben indicar exactamente la misma ruta**.

No puede haber contenido fuera de esos comentarios.

---

### Ejemplos válidos

#### Markdown / HTML

```

<!-- /docs/architecture_v3.0.md -->

[contenido completo]

<!-- /docs/architecture_v3.0.md -->

```

---

#### Python

```

# /src/app/services/products_service.py

[contenido completo]

# /src/app/services/products_service.py

```

---

#### JavaScript / TypeScript

```

// /src/app/frontend/store/products.ts
[contenido completo]
// /src/app/frontend/store/products.ts

```

---

#### YAML / Docker / Configuración

```

# /docker-compose.yml

[contenido completo]

# /docker-compose.yml

```

---

### Reglas estrictas

1. El comentario superior y el inferior **deben coincidir exactamente**.
2. El comentario superior debe ser **la primera línea** del archivo.
3. El comentario inferior debe ser **la última línea** del archivo.
4. No puede haber **ningún contenido fuera** de esos dos comentarios.
5. Si el usuario no indica ruta:
   - la IA **debe pedirla**
   - o inferirla solo si la arquitectura lo hace inequívoco.
6. Entregar código o documentos sin este encapsulado **está prohibido**.

---

## 7. Plantillas y contratos

Si existe:

* plantilla base
* plantilla extensión
* plantilla especial

La IA:

* **debe usarlas**
* **no puede desviarse**
* **no puede simplificarlas**

Si una plantilla no cubre un caso:
👉 **parar y pedir definición**, no improvisar.

---

## 8. Testing

La IA debe respetar el estándar definido en arquitectura:

* Tests de services
* Tests de endpoints
* Tests de flujos

No exigir más.
No proponer menos.

---

## 9. Versiones y tipado

La IA debe asumir siempre:

* Python tipado
* Librerías estables o LTS
* Nada experimental

Si una versión no está definida:
👉 **no asumir**, preguntar.

---

## 10. Objetivo final de estas reglas

Estas reglas existen para:

1. Evitar invenciones.
2. Evitar simplificaciones destructivas.
3. Evitar reprocesos.
4. Convertir a la IA en una **herramienta predecible**.
5. Permitir trabajar de forma iterativa **sin romper el sistema**.

---

## 11. Regla final (inapelable)

> **Si no está claro, no continúes. Pregunta.**

---

**FIN DEL DOCUMENTO**

<!-- /docs/ai_rules_v3.0.md -->