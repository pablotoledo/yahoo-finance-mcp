# Tool Docstring Best Practices - MCP Python SDK

## 📚 Resumen de Recomendaciones Oficiales

Basado en:
- [MCP Specification - Tools](https://modelcontextprotocol.io/specification/2025-06-18/server/tools)
- [Python SDK Repository](https://github.com/modelcontextprotocol/python-sdk)

---

## ✅ Mejores Prácticas

### 1. **Description en el Decorador vs Docstring**

FastMCP ofrece 3 formas de especificar la descripción de un tool:

#### Opción A: Description en el decorador (RECOMENDADO para tools simples)
```python
@mcp.tool(description="Add two numbers together")
def sum(a: int, b: int) -> int:
    return a + b
```

#### Opción B: Docstring (cuando no hay description en decorador)
```python
@mcp.tool()
def sum(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b
```

#### Opción C: Ambos (el decorador tiene prioridad)
```python
@mcp.tool(description="Add two numbers together")
def sum(a: int, b: int) -> int:
    """Internal note: Uses standard Python addition operator."""
    return a + b
```

**📌 Recomendación**: 
- Para tools simples: usar `description` en el decorador
- Para tools complejos con múltiples párrafos: usar docstring
- NUNCA duplicar la misma información en ambos

---

### 2. **Documentación de Parámetros**

#### ❌ NO HACER (Args en docstring):
```python
@mcp.tool()
def get_weather(city: str, unit: str = "celsius") -> str:
    """
    Get weather for a city.
    
    Args:
        city: Name of the city
        unit: Temperature unit (celsius or fahrenheit)
    
    Returns:
        Weather information string
    """
    return f"Weather in {city}: 22°{unit[0].upper()}"
```

#### ✅ HACER (Field descriptions):
```python
from pydantic import Field

@mcp.tool()
def get_weather(
    city: str = Field(description="Name of the city to get weather for"),
    unit: str = Field(description="Temperature unit: 'celsius' or 'fahrenheit'", default="celsius")
) -> str:
    """Get current weather for a city."""
    return f"Weather in {city}: 22°{unit[0].upper()}"
```

**Por qué**: 
- `Field(description=...)` genera automáticamente el JSON Schema
- Los LLMs reciben estas descripciones en `inputSchema`
- Mantiene la documentación DRY (Don't Repeat Yourself)

---

### 3. **Estructura del Docstring**

#### Para tools simples (1 línea):
```python
@mcp.tool()
def echo(text: str) -> str:
    """Echo the input text."""
    return text
```

#### Para tools complejos:
```python
@mcp.tool()
async def book_table(
    date: str = Field(description="Date in YYYY-MM-DD format"),
    time: str = Field(description="Time in HH:MM format (24h)"),
    party_size: int = Field(description="Number of guests"),
    ctx: Context | None = None
) -> str:
    """
    Book a table at a restaurant with availability check.
    
    This tool checks date availability and may request alternative
    dates if the requested date is unavailable.
    """
    # Implementation...
```

**Formato recomendado**:
1. Primera línea: Acción concisa (verbo + objeto)
2. Líneas adicionales: Detalles de comportamiento especial
3. NO incluir: Args, Returns, Raises (se infieren de tipos y Field)

---

### 4. **Unicode y Emojis**

✅ Los emojis y Unicode son totalmente soportados:

```python
@mcp.tool(description="🌟 Get weather with emoji indicators")
def get_weather_emoji(
    city: str = Field(description="City name (supports Unicode: 北京, São Paulo)")
) -> str:
    """Returns weather with emoji indicators: ☀️ 🌧️ ⛈️ ❄️"""
    return f"Weather in {city}: ☀️ 22°C"
```

**Cuándo usar emojis**:
- ✅ En `description` para destacar visualmente el tool
- ✅ En outputs para mejor UX
- ❌ NO en `name` (debe ser snake_case válido)

---

### 5. **Title vs Name vs Description**

```python
@mcp.tool(
    name="get_stock_data",           # snake_case, único, usado por LLM
    title="Stock Data Retriever",    # Opcional, human-readable
    description="Get comprehensive stock information including price, volume, and metrics"
)
def get_stock_data(ticker: str) -> StockData:
    """Implementation..."""
```

**Diferencias**:
- `name`: Identificador técnico (usado en tool calls)
- `title`: Nombre para UI/inspección (opcional)
- `description`: Qué hace el tool (para LLM y humanos)

---

### 6. **Context Parameter**

El parámetro `Context` es **especial** y no debe documentarse:

```python
# ✅ CORRECTO
@mcp.tool()
async def long_task(
    task_name: str = Field(description="Name of the task to execute"),
    ctx: Context | None = None  # NO necesita Field()
) -> str:
    """Execute a long-running task with progress updates."""
    await ctx.info(f"Starting {task_name}")
    # ...
```

**Por qué**: 
- FastMCP lo detecta automáticamente por tipo
- No aparece en `inputSchema`
- Se inyecta automáticamente en runtime

---

### 7. **Structured Output**

Para tools con structured output, el docstring se enfoca en QUÉ devuelve, no en el schema:

```python
class WeatherData(BaseModel):
    """Weather information structure."""  # ← Este docstring es para el schema
    temperature: float = Field(description="Temperature in Celsius")
    humidity: float = Field(description="Humidity percentage")
    condition: str = Field(description="Weather condition")

@mcp.tool()
def get_weather(city: str) -> WeatherData:
    """Get weather for a city with structured data."""  # ← Este es para el tool
    return WeatherData(temperature=22.5, humidity=65, condition="Sunny")
```

**Separación de concerns**:
- Tool docstring: Qué hace la función
- Model docstring: Qué representa la estructura de datos
- Field descriptions: Qué significa cada campo

---

## 🎯 Checklist para Revisar Tools

Para cada `@mcp.tool()`:

- [ ] ¿El `name` es snake_case y descriptivo?
- [ ] ¿La `description` o docstring es concisa (1-2 líneas)?
- [ ] ¿Los parámetros usan `Field(description=...)` en lugar de docstring Args?
- [ ] ¿El parámetro `Context` NO tiene `Field()`?
- [ ] ¿El docstring NO duplica información del decorador?
- [ ] ¿Si hay structured output, los modelos Pydantic tienen docstrings?
- [ ] ¿Los Field descriptions son claros para un LLM?

---

## 📋 Ejemplos del Repositorio Oficial

### Simple Tool (fastmcp/echo.py)
```python
@mcp.tool()
def echo_tool(text: str) -> str:
    """Echo the input text"""
    return text
```

### Tool con Field Descriptions (fastmcp/parameter_descriptions.py)
```python
@mcp.tool()
def greet_user(
    name: str = Field(description="The name of the person to greet"),
    title: str = Field(description="Optional title like Mr/Ms/Dr", default=""),
    times: int = Field(description="Number of times to repeat the greeting", default=1),
) -> str:
    """Greet a user with optional title and repetition"""
    greeting = f"Hello {title + ' ' if title else ''}{name}!"
    return "\n".join([greeting] * times)
```

### Tool con Context (snippets/servers/tool_progress.py)
```python
@mcp.tool()
async def long_running_task(
    task_name: str, 
    ctx: Context[ServerSession, None], 
    steps: int = 5
) -> str:
    """Execute a task with progress updates."""
    await ctx.info(f"Starting: {task_name}")
    # ...
    return f"Task '{task_name}' completed"
```

### Unicode Tool (fastmcp/unicode_example.py)
```python
@mcp.tool(description="🌟 A tool that uses various Unicode characters: á é í ó ú ñ 漢字 🎉")
def hello_unicode(
    name: str = "世界", 
    greeting: str = "¡Hola"
) -> str:
    """
    A simple tool that demonstrates Unicode handling in:
    - Tool description (emojis, accents, CJK characters)
    - Parameter defaults (CJK characters)
    - Return values (Spanish punctuation, emojis)
    """
    return f"{greeting}, {name}! 👋"
```

---

## 🔧 Anti-Patterns a Evitar

### ❌ Docstring duplicado con description
```python
@mcp.tool(description="Add two numbers")
def sum(a: int, b: int) -> int:
    """Add two numbers."""  # ← Redundante!
    return a + b
```

### ❌ Args en docstring con Field descriptions
```python
@mcp.tool()
def get_weather(
    city: str = Field(description="City name")  # ← Ya documentado aquí
) -> str:
    """
    Get weather.
    
    Args:
        city: City name  # ← Redundante y no usado por MCP!
    """
    pass
```

### ❌ Context con Field()
```python
@mcp.tool()
async def task(
    name: str,
    ctx: Context = Field(description="...")  # ❌ NO! Context es especial
) -> str:
    pass
```

### ❌ Descripción vaga
```python
@mcp.tool()
def get_data(symbol: str) -> dict:
    """Get data."""  # ❌ Demasiado vago para LLM
    pass

# ✅ MEJOR:
@mcp.tool()
def get_stock_data(symbol: str) -> StockData:
    """Get comprehensive stock information including price, volume, and financial metrics."""
    pass
```

---

## 📖 Referencias

1. **MCP Specification**: https://modelcontextprotocol.io/specification/2025-06-18/server/tools
2. **Python SDK README**: https://github.com/modelcontextprotocol/python-sdk/blob/main/README.md#tools
3. **FastMCP Examples**: https://github.com/modelcontextprotocol/python-sdk/tree/main/examples/fastmcp
4. **Structured Output Guide**: https://github.com/modelcontextprotocol/python-sdk/blob/main/README.md#structured-output

---

**Fecha**: 2025-10-25  
**Versión SDK**: mcp 1.19.0 (FastMCP)  
**Autor**: Pablo Toledo
