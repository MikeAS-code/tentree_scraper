# Tentree Product Scraper

## Descripción

Este proyecto consiste en completar un crawler para la extracción de productos de **Tentree**.

La base del crawler ya se encuentra implementada y está dividida en dos etapas principales:

* **Discovery:** obtiene las URLs de los productos disponibles en Tentree a partir de los sitemaps del sitio.
* **PDP (Product Detail Page):** recibe las URLs obtenidas durante el Discovery y procesa cada producto para extraer su información.

La tarea consiste principalmente en **completar la etapa PDP para extraer todos los campos requeridos**, normalizar la información y generar la estructura final definida en este documento.

No es necesario rehacer el crawler ni modificar su arquitectura general.

---

## Estructura del proyecto

El proyecto debe mantener la siguiente estructura:

```text
.
├── .gitignore
├── .env
├── .env.example
├── requirements.txt
├── config.py
└── main.py
```

### `main.py`

Contiene la lógica principal del crawler, incluyendo:

* Discovery.
* PDP.
* Parseo de productos.
* Parseo de variantes.
* Ejecución general del crawler.

### `config.py`

Contiene las configuraciones utilizadas por el crawler, por ejemplo:

* Base URL.
* Regex.
* Headers.
* Proxies.
* Timeout.
* Cantidad máxima de retries.
* Otras configuraciones necesarias.

### `.env`

Contiene variables privadas o credenciales necesarias para ejecutar el proyecto.

Este archivo no debe subirse al repositorio.

### `.env.example`

Debe contener las mismas variables requeridas por `.env`, pero sin valores privados.

### `.gitignore`

Debe excluir como mínimo:

* `.env`
* entornos virtuales;
* archivos generados por Python;
* archivos temporales del IDE/editor.

---

# Flujo general

El crawler debe mantener el siguiente flujo:

```text
Tentree Sitemap
      │
      ▼
   Discovery
      │
      ▼
Product Sitemaps
      │
      ▼
 Product URLs
      │
      ▼
     PDP
      │
      ▼
Product Information
      │
      ▼
Final Records
```

---

# Discovery

La etapa de **Discovery ya se encuentra implementada**.

Su objetivo es obtener todas las URLs de productos que posteriormente serán procesadas por el PDP.

El proceso parte del sitemap principal:

```text
https://www.tentree.com/sitemap.xml
```

Desde allí se identifican los sitemaps correspondientes a productos y posteriormente se extraen las URLs de productos.

Ejemplo de sitemap de productos:

```text
https://www.tentree.com/sitemap_products_1.xml?from=292293738519&to=7126736437434
```

Ejemplo de producto descubierto:

```text
https://www.tentree.com/products/mens-portal-t-shirt-blue-fog
```

El resultado del Discovery debe ser una colección de URLs únicas que serán enviadas a la etapa PDP.

---

# PDP

La etapa **PDP ya cuenta con su estructura base** y recibe los productos obtenidos durante el Discovery.

Actualmente se puede obtener información estructurada del producto mediante el endpoint:

```text
<product_url>.js
```

Por ejemplo:

```text
https://www.tentree.com/products/mens-portal-t-shirt-blue-fog.js
```

La tarea pendiente consiste en **terminar la extracción y normalización de los campos del producto**.

Si algún campo no se encuentra disponible en este endpoint, se deberá obtener desde otra fuente disponible en la página, API o información utilizada por el frontend.

---

# Campos requeridos

Cada producto debe contener los siguientes campos:

```text
url
id
title
description
vendor
price
image_main
images
rating_reviews
amount_reviews
amount_variants
variants
```

### Descripción general

| Campo             | Descripción                          |
| ----------------- | ------------------------------------ |
| `url`             | URL original del producto            |
| `id`              | ID del producto                      |
| `title`           | Nombre del producto                  |
| `description`     | Descripción del producto             |
| `vendor`          | Vendor o marca                       |
| `price`           | Precio del producto                  |
| `image_main`      | Imagen principal                     |
| `images`          | Array con las imágenes del producto  |
| `rating_reviews`  | Rating promedio                      |
| `amount_reviews`  | Cantidad total de reviews            |
| `amount_variants` | Cantidad de variantes                |
| `variants`        | Array con las variantes del producto |

Los valores deben normalizarse cuando sea necesario. Por ejemplo, si un precio se obtiene en centavos, debe convertirse al valor monetario correspondiente.

---

# Variantes

`variants` debe ser obligatoriamente un **array de diccionarios**.

Cada variante debe contener:

```text
id
title
sku
stock
price
image
barcode
option
value_option
```

La estructura general será:

```json
{
  "variants": [
    {
      "id": 123456789,
      "title": "White / XL",
      "sku": "PRODUCT-WHITE-XL",
      "stock": true,
      "price": 68.0,
      "image": "https://...",
      "barcode": "1234567890123",
      "option": "Color",
      "value_option": "White"
    }
  ]
}
```

---

# Options

Los campos:

```text
option
value_option
```

representan el tipo de opción y su valor respectivamente.

Por ejemplo:

```text
Color: White
```

debe representarse como:

```json
{
  "option": "Color",
  "value_option": "White"
}
```

Otro ejemplo:

```text
Size: XL
```

se representa como:

```json
{
  "option": "Size",
  "value_option": "XL"
}
```

Se debe relacionar correctamente la información de las opciones del producto con los valores correspondientes a cada variante.

Un producto puede tener diferentes tipos de opciones, por ejemplo:

```text
Color
Size
Material
Style
```

Por lo tanto, la implementación no debe asumir que siempre existirán únicamente `Color` o `Size`.

---

# Reviews

También deben obtenerse:

```text
rating_reviews
amount_reviews
```

Ejemplo:

```json
{
  "rating_reviews": 4.8,
  "amount_reviews": 213
}
```

Si estos campos no están disponibles en la respuesta `.js` del producto, deberán obtenerse desde la fuente utilizada por Tentree para mostrar las reviews.

No es necesario extraer el contenido completo de cada review. Solamente se requieren:

* rating promedio;
* cantidad total de reviews.

---

# Output esperado

Cada producto debe terminar generando un registro similar al siguiente:

```json
{
  "url": "https://www.tentree.com/products/mens-portal-t-shirt-blue-fog",
  "id": 7126736437434,
  "title": "Men's Portal T-Shirt",
  "description": "Product description",
  "vendor": "tentree",
  "price": 45.0,
  "image_main": "https://cdn.shopify.com/example-main.jpg",
  "images": [
    "https://cdn.shopify.com/example-main.jpg",
    "https://cdn.shopify.com/example-back.jpg",
    "https://cdn.shopify.com/example-detail.jpg"
  ],
  "rating_reviews": 4.8,
  "amount_reviews": 213,
  "amount_variants": 6,
  "variants": [
    {
      "id": 41234567890,
      "title": "Blue Fog / S",
      "sku": "TCM1234-BLF-S",
      "stock": true,
      "price": 45.0,
      "image": "https://cdn.shopify.com/example-blue-fog.jpg",
      "barcode": "661814000001",
      "option": "Color",
      "value_option": "Blue Fog"
    },
    {
      "id": 41234567891,
      "title": "Blue Fog / XL",
      "sku": "TCM1234-BLF-XL",
      "stock": true,
      "price": 45.0,
      "image": "https://cdn.shopify.com/example-blue-fog.jpg",
      "barcode": "661814000002",
      "option": "Size",
      "value_option": "XL"
    }
  ]
}
```

Los valores anteriores son únicamente ilustrativos. Los valores finales deben provenir de la información real de cada producto.

---

# Consideraciones generales

La implementación debe respetar la estructura y funcionamiento actual del crawler.

Se debe tener en cuenta:

* Utilizar el Discovery existente para obtener los productos.
* Completar principalmente la lógica del PDP.
* Extraer todos los campos definidos.
* Mantener `variants` como un array de diccionarios.
* Relacionar correctamente `option` con `value_option`.
* Normalizar precios y otros valores cuando corresponda.
* Evitar que campos opcionales faltantes detengan la ejecución.
* Mantener el sistema de retries existente.
* Mantener el uso de proxies y configuración centralizada.
* No almacenar credenciales directamente en el código.
* Evitar productos duplicados durante el Discovery.
* Procesar todos los productos descubiertos.
* Permitir que el crawler continúe si falla un producto individual.

---

# Tarea pendiente

La estructura principal del crawler y el proceso de Discovery/PDP ya están desarrollados.

La tarea consiste en:

> **Completar la extracción de los campos del PDP de Tentree y generar para cada producto un registro con la estructura definida en este README.**

En particular, se debe terminar la extracción de:

```text
url
id
title
description
vendor
price
image_main
images
rating_reviews
amount_reviews
amount_variants
variants
```

incluyendo dentro de cada variante:

```text
id
title
sku
stock
price
image
barcode
option
value_option
```

El objetivo final es que el crawler pueda ejecutar el flujo completo:

```text
Discovery → Product URLs → PDP → Parsed Products
```

y devolver los productos con todos los campos requeridos correctamente estructurados y guardados en un archivo JSON.
