# 📋 Plan de Implementación Detallado - AI CV Generator

> **Objetivo**: Transformar el proyecto actual en una plataforma SaaS completa con todas las mejoras propuestas.
> **Duración estimada**: 6-8 meses (dependiendo del equipo)
> **Metodología**: Desarrollo incremental con releases cada 2-3 semanas

---

## 🎯 Estrategia General

### Principios de Desarrollo
1. **Incremental**: Cada feature debe ser independiente y desplegable
2. **Backward Compatible**: No romper funcionalidad existente
3. **Test-Driven**: Tests antes o durante desarrollo
4. **Documentation**: Documentar cada feature importante
5. **User Feedback**: Validar con usuarios reales antes de escalar

### Fases de Implementación

```
Fase 1: Fundación (Semanas 1-4)
Fase 2: UX Core (Semanas 5-8)
Fase 3: Features Avanzadas (Semanas 9-16)
Fase 4: Optimización (Semanas 17-20)
Fase 5: Escalabilidad (Semanas 21-24)
```

---

## 📅 FASE 1: FUNDACIÓN (Semanas 1-4)

### 🎯 Objetivo
Establecer base sólida: persistencia, configuración, y mejoras de UX básicas.

---

### **SPRINT 1.1: Persistencia de Preferencias** (Semana 1)
**Prioridad**: 🔴 CRÍTICA  
**Esfuerzo**: 2-3 días  
**Dependencias**: Ninguna

#### Objetivos
- Guardar configuración del usuario en localStorage
- Cargar configuración al iniciar
- Templates guardados (combinaciones de parámetros)

#### Tareas Técnicas Detalladas

##### 1.1.1: Crear servicio de persistencia
**Archivo**: `frontend/src/lib/storage.js`
```javascript
// Funcionalidades:
- saveConfig(config) → localStorage
- loadConfig() → config object
- saveTemplate(name, config) → templates array
- loadTemplates() → templates array
- deleteTemplate(id)
- exportConfig() → JSON download
- importConfig(json) → restore from JSON
```

**Implementación**:
- [ ] Crear `storage.js` con funciones de localStorage
- [ ] Manejar migración de versiones de config
- [ ] Validar estructura de datos al cargar
- [ ] Manejar errores de localStorage (quota exceeded)
- [ ] Añadir timestamps a templates

##### 1.1.2: Integrar con Zustand Store
**Archivo**: `frontend/src/stores/useGenerationStore.js`

**Cambios**:
- [ ] Modificar `setConfig` para guardar automáticamente
- [ ] Añadir `loadSavedConfig()` al mount
- [ ] Añadir `saveAsTemplate(name)` action
- [ ] Añadir `loadTemplate(id)` action
- [ ] Añadir `deleteTemplate(id)` action
- [ ] Añadir `exportConfig()` action
- [ ] Añadir `importConfig(json)` action

**Código específico**:
```javascript
// En useGenerationStore.js
setConfig: (key, value) => {
    set((state) => {
        const newConfig = { ...state.config, [key]: value };
        // Auto-save to localStorage
        storage.saveConfig(newConfig);
        return { config: newConfig };
    });
},

// Load on mount
useEffect(() => {
    const saved = storage.loadConfig();
    if (saved) {
        set({ config: { ...defaultConfig, ...saved } });
    }
}, []);
```

##### 1.1.3: UI para Templates
**Archivo**: `frontend/src/components/TemplateManager.jsx` (NUEVO)

**Componentes**:
- [ ] `TemplateManager.jsx` - Panel para gestionar templates
- [ ] `TemplateSelector.jsx` - Dropdown para seleccionar template
- [ ] `TemplateSaveModal.jsx` - Modal para guardar template actual

**UI Elements**:
- [ ] Botón "Save as Template" en ConfigPanel
- [ ] Dropdown "Load Template" en ConfigPanel
- [ ] Sección "My Templates" con lista
- [ ] Botones: Load, Delete, Rename, Export

**Diseño**:
```
┌─────────────────────────────┐
│ 📋 My Templates              │
├─────────────────────────────┤
│ [Save Current as Template]  │
│                             │
│ Templates:                  │
│ • Junior Dev Template       │
│   [Load] [Delete] [Export]  │
│ • Senior Manager Template   │
│   [Load] [Delete] [Export]  │
└─────────────────────────────┘
```

##### 1.1.4: Testing
- [ ] Test: Guardar y cargar configuración
- [ ] Test: Guardar múltiples templates
- [ ] Test: Eliminar template
- [ ] Test: Export/Import config
- [ ] Test: Migración de versiones antiguas
- [ ] Test: Manejo de localStorage lleno

**Archivo**: `frontend/src/lib/__tests__/storage.test.js`

##### 1.1.5: Documentación
- [ ] Documentar API de storage
- [ ] Añadir ejemplos de uso
- [ ] Documentar estructura de datos

**Archivo**: `frontend/src/lib/storage.md`

---

### **SPRINT 1.2: Búsqueda y Filtrado en FileExplorer** (Semana 1-2)
**Prioridad**: 🔴 CRÍTICA  
**Esfuerzo**: 3-4 días  
**Dependencias**: Ninguna

#### Objetivos
- Búsqueda en tiempo real por nombre, rol, ID
- Filtros por fecha, tamaño, estado
- Ordenamiento mejorado

#### Tareas Técnicas Detalladas

##### 1.2.1: Componente de Búsqueda
**Archivo**: `frontend/src/components/FileExplorer.jsx`

**Funcionalidades**:
- [ ] Input de búsqueda con debounce (300ms)
- [ ] Búsqueda en: filename, name, role, id
- [ ] Highlight de términos encontrados
- [ ] Clear button (X) cuando hay texto
- [ ] Contador de resultados: "5 of 20 files"

**Implementación**:
```javascript
// Estado
const [searchQuery, setSearchQuery] = useState('');

// Filtrado
const filteredFiles = useMemo(() => {
    if (!searchQuery) return sortedFiles;
    
    const query = searchQuery.toLowerCase();
    return sortedFiles.filter(file => {
        const meta = file.meta;
        return (
            meta.name.toLowerCase().includes(query) ||
            meta.role.toLowerCase().includes(query) ||
            meta.id.toLowerCase().includes(query) ||
            file.filename.toLowerCase().includes(query)
        );
    });
}, [sortedFiles, searchQuery]);
```

**UI**:
```
┌─────────────────────────────────────┐
│ [🔍 Search files...]          [X]   │
│ Showing 5 of 20 files               │
└─────────────────────────────────────┘
```

##### 1.2.2: Filtros Avanzados
**Archivo**: `frontend/src/components/FileExplorerFilters.jsx` (NUEVO)

**Filtros a implementar**:
- [ ] **Por Fecha**: 
  - Última hora, Últimas 24h, Última semana, Último mes, Personalizado
- [ ] **Por Tamaño**:
  - < 100 KB, 100-500 KB, > 500 KB
- [ ] **Por Estado**:
  - Completados, Con errores, En progreso
- [ ] **Por Rol/Categoría**:
  - Dropdown con roles únicos de los archivos

**Componente**:
```jsx
<FileExplorerFilters
    onFilterChange={(filters) => setActiveFilters(filters)}
    availableRoles={uniqueRoles}
/>
```

**UI**:
```
┌─────────────────────────────────────┐
│ Filters:                            │
│ [Date: Last week ▼]                 │
│ [Size: All ▼]                       │
│ [Role: Developer ▼]                 │
│ [Clear All Filters]                 │
└─────────────────────────────────────┘
```

##### 1.2.3: Lógica de Filtrado Combinado
**Archivo**: `frontend/src/components/FileExplorer.jsx`

**Implementación**:
```javascript
const [filters, setFilters] = useState({
    dateRange: null,
    sizeRange: null,
    role: null,
    status: null
});

const filteredAndSearched = useMemo(() => {
    let result = filesWithMeta;
    
    // Aplicar búsqueda
    if (searchQuery) {
        result = applySearch(result, searchQuery);
    }
    
    // Aplicar filtros
    if (filters.dateRange) {
        result = filterByDate(result, filters.dateRange);
    }
    if (filters.sizeRange) {
        result = filterBySize(result, filters.sizeRange);
    }
    if (filters.role) {
        result = filterByRole(result, filters.role);
    }
    
    return result;
}, [filesWithMeta, searchQuery, filters]);
```

##### 1.2.4: Ordenamiento Mejorado
**Archivo**: `frontend/src/components/FileExplorer.jsx`

**Mejoras**:
- [ ] Ordenamiento multi-columna (click en header)
- [ ] Indicador visual de columna activa
- [ ] Dirección de orden (asc/desc) visible
- [ ] Persistir ordenamiento en localStorage

**Implementación**:
```javascript
const [sortConfig, setSortConfig] = useState({
    primary: 'created_at',
    secondary: null,
    direction: 'desc'
});

const handleSort = (column) => {
    setSortConfig(prev => {
        if (prev.primary === column) {
            // Toggle direction
            return { ...prev, direction: prev.direction === 'asc' ? 'desc' : 'asc' };
        } else {
            // New primary column
            return { primary: column, secondary: prev.primary, direction: 'desc' };
        }
    });
};
```

##### 1.2.5: Testing
- [ ] Test: Búsqueda por nombre
- [ ] Test: Búsqueda por rol
- [ ] Test: Filtro por fecha
- [ ] Test: Filtro por tamaño
- [ ] Test: Combinación de filtros
- [ ] Test: Ordenamiento multi-columna

---

### **SPRINT 1.3: Modo Oscuro/Claro Persistente** (Semana 2)
**Prioridad**: 🟡 ALTA  
**Esfuerzo**: 1-2 días  
**Dependencias**: Ninguna

#### Objetivos
- Toggle de tema funcional
- Persistencia en localStorage
- Transición suave

#### Tareas Técnicas Detalladas

##### 1.3.1: Sistema de Temas
**Archivo**: `frontend/src/lib/theme.js` (NUEVO)

**Funcionalidades**:
- [ ] `getTheme()` → 'light' | 'dark' | 'system'
- [ ] `setTheme(theme)` → guarda y aplica
- [ ] `applyTheme(theme)` → aplica CSS variables
- [ ] `watchSystemTheme()` → detecta cambios del sistema

**Implementación**:
```javascript
export const themes = {
    light: {
        '--bg-primary': '#ffffff',
        '--bg-secondary': '#f5f5f5',
        // ... más variables
    },
    dark: {
        '--bg-primary': '#0a0a0a',
        '--bg-secondary': '#1a1a1a',
        // ... más variables
    }
};

export function applyTheme(theme) {
    const root = document.documentElement;
    const themeVars = themes[theme] || themes.light;
    
    Object.entries(themeVars).forEach(([key, value]) => {
        root.style.setProperty(key, value);
    });
    
    root.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
}
```

##### 1.3.2: Hook de Tema
**Archivo**: `frontend/src/hooks/useTheme.js` (NUEVO)

**Implementación**:
```javascript
export function useTheme() {
    const [theme, setThemeState] = useState(() => {
        return localStorage.getItem('theme') || 'dark';
    });
    
    useEffect(() => {
        applyTheme(theme);
    }, [theme]);
    
    const setTheme = (newTheme) => {
        setThemeState(newTheme);
        applyTheme(newTheme);
    };
    
    const toggleTheme = () => {
        setTheme(theme === 'dark' ? 'light' : 'dark');
    };
    
    return { theme, setTheme, toggleTheme };
}
```

##### 1.3.3: UI Component
**Archivo**: `frontend/src/components/ThemeToggle.jsx` (NUEVO)

**Ubicación**: En ConfigPanel header

**Implementación**:
```jsx
export default function ThemeToggle() {
    const { theme, toggleTheme } = useTheme();
    
    return (
        <Button
            variant="ghost"
            size="icon"
            onClick={toggleTheme}
            title={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
        >
            {theme === 'dark' ? <Sun /> : <Moon />}
        </Button>
    );
}
```

##### 1.3.4: CSS Variables
**Archivo**: `frontend/src/index.css`

**Cambios**:
- [ ] Definir variables CSS para ambos temas
- [ ] Añadir transición suave: `transition: background-color 0.3s ease`
- [ ] Asegurar contraste adecuado en ambos temas

##### 1.3.5: Testing
- [ ] Test: Toggle funciona
- [ ] Test: Persistencia funciona
- [ ] Test: Aplicación al recargar página

---

### **SPRINT 1.4: Mejoras de Error Handling** (Semana 2-3)
**Prioridad**: 🔴 CRÍTICA  
**Esfuerzo**: 2-3 días  
**Dependencias**: Ninguna

#### Objetivos
- Reintentos automáticos
- Queue de reintentos
- Notificaciones mejoradas

#### Tareas Técnicas Detalladas

##### 1.4.1: Sistema de Reintentos
**Archivo**: `frontend/src/lib/retry.js` (NUEVO)

**Funcionalidades**:
- [ ] `retryWithBackoff(fn, options)` → función con reintentos
- [ ] Exponential backoff configurable
- [ ] Max retries configurable
- [ ] Callback de progreso

**Implementación**:
```javascript
export async function retryWithBackoff(
    fn,
    {
        maxRetries = 3,
        initialDelay = 1000,
        maxDelay = 10000,
        backoffFactor = 2,
        onRetry = null
    } = {}
) {
    let lastError;
    
    for (let attempt = 0; attempt <= maxRetries; attempt++) {
        try {
            return await fn();
        } catch (error) {
            lastError = error;
            
            if (attempt < maxRetries) {
                const delay = Math.min(
                    initialDelay * Math.pow(backoffFactor, attempt),
                    maxDelay
                );
                
                if (onRetry) {
                    onRetry(attempt + 1, maxRetries, delay);
                }
                
                await new Promise(resolve => setTimeout(resolve, delay));
            }
        }
    }
    
    throw lastError;
}
```

##### 1.4.2: Error Boundary
**Archivo**: `frontend/src/components/ErrorBoundary.jsx` (NUEVO)

**Implementación**:
```jsx
export class ErrorBoundary extends React.Component {
    state = { hasError: false, error: null };
    
    static getDerivedStateFromError(error) {
        return { hasError: true, error };
    }
    
    componentDidCatch(error, errorInfo) {
        console.error('Error caught by boundary:', error, errorInfo);
        // Opcional: enviar a servicio de logging
    }
    
    render() {
        if (this.state.hasError) {
            return <ErrorFallback error={this.state.error} />;
        }
        return this.props.children;
    }
}
```

##### 1.4.3: Queue de Reintentos
**Archivo**: `frontend/src/stores/useRetryQueue.js` (NUEVO)

**Funcionalidades**:
- [ ] Cola de tareas fallidas
- [ ] Reintento automático en background
- [ ] UI para ver queue
- [ ] Botón "Retry All"

**Implementación**:
```javascript
const useRetryQueue = create((set, get) => ({
    failedTasks: [],
    
    addFailedTask: (task) => {
        set(state => ({
            failedTasks: [...state.failedTasks, {
                ...task,
                retryCount: 0,
                nextRetryAt: Date.now() + 5000
            }]
        }));
    },
    
    retryTask: async (taskId) => {
        // Lógica de reintento
    },
    
    retryAll: async () => {
        // Reintentar todos
    }
}));
```

##### 1.4.4: Notificaciones Mejoradas
**Archivo**: `frontend/src/lib/notifications.js` (NUEVO)

**Mejoras**:
- [ ] Notificaciones con acciones (Retry, Dismiss)
- [ ] Agrupación de notificaciones similares
- [ ] Sonido opcional
- [ ] Notificaciones del sistema (si está permitido)

**Implementación**:
```javascript
export function showErrorNotification(error, actions = []) {
    toast.error(error.message, {
        description: error.details,
        action: actions.map(action => ({
            label: action.label,
            onClick: action.onClick
        })),
        duration: 10000
    });
    
    // Sistema notification si está permitido
    if (Notification.permission === 'granted') {
        new Notification('Generation Failed', {
            body: error.message,
            icon: '/icon.png'
        });
    }
}
```

##### 1.4.5: Integración en API Calls
**Archivo**: `frontend/src/lib/api.js`

**Cambios**:
- [ ] Envolver todas las llamadas API con retry
- [ ] Manejar errores específicos (429, 500, etc.)
- [ ] Añadir timeout configurable

**Implementación**:
```javascript
// En api.js
api.interceptors.response.use(
    response => response,
    async error => {
        if (error.response?.status === 429) {
            // Rate limit - retry with backoff
            return retryWithBackoff(() => api.request(error.config));
        }
        return Promise.reject(error);
    }
);
```

---

### **SPRINT 1.5: Estadísticas Básicas** (Semana 3-4)
**Prioridad**: 🟡 MEDIA  
**Esfuerzo**: 2-3 días  
**Dependencias**: Persistencia (Sprint 1.1)

#### Objetivos
- Dashboard con métricas básicas
- Tiempo promedio por CV
- Tasa de éxito/fallo

#### Tareas Técnicas Detalladas

##### 1.5.1: Servicio de Estadísticas
**Archivo**: `frontend/src/lib/stats.js` (NUEVO)

**Funcionalidades**:
- [ ] `trackGeneration(task)` → guarda métricas
- [ ] `getStats()` → calcula estadísticas
- [ ] `getTimeSeries()` → datos para gráficos
- [ ] `exportStats()` → exportar como JSON

**Estructura de datos**:
```javascript
{
    totalGenerations: 150,
    successful: 142,
    failed: 8,
    averageTime: 45.3, // segundos
    totalTime: 6795, // segundos
    byRole: {
        'Software Developer': 45,
        'Product Manager': 32,
        // ...
    },
    byDate: [
        { date: '2026-01-15', count: 12 },
        // ...
    ]
}
```

##### 1.5.2: Componente Dashboard
**Archivo**: `frontend/src/components/StatsDashboard.jsx` (NUEVO)

**Métricas a mostrar**:
- [ ] Total de CVs generados
- [ ] Tasa de éxito (%)
- [ ] Tiempo promedio
- [ ] CVs por día (gráfico de línea)
- [ ] Distribución por rol (gráfico de barras)
- [ ] Tiempo por fase (gráfico de barras apiladas)

**Librería de gráficos**: `recharts` o `chart.js`

**UI**:
```
┌─────────────────────────────────────┐
│ 📊 Statistics Dashboard             │
├─────────────────────────────────────┤
│ Total: 150 CVs                      │
│ Success Rate: 94.7%                 │
│ Avg Time: 45.3s                      │
│                                     │
│ [Chart: CVs per day]                │
│ [Chart: By role]                    │
│ [Chart: Time by phase]              │
└─────────────────────────────────────┘
```

##### 1.5.3: Integración con Store
**Archivo**: `frontend/src/stores/useGenerationStore.js`

**Cambios**:
- [ ] Track cada task completada
- [ ] Track cada task fallida
- [ ] Calcular tiempo de generación
- [ ] Guardar en localStorage

**Implementación**:
```javascript
// En useGenerationStore
trackTaskComplete: (task, duration) => {
    stats.trackGeneration({
        taskId: task.id,
        role: task.role,
        status: 'success',
        duration,
        timestamp: Date.now()
    });
}
```

##### 1.5.4: Testing
- [ ] Test: Cálculo de estadísticas
- [ ] Test: Persistencia de métricas
- [ ] Test: Export de estadísticas

---

## 📅 FASE 2: UX CORE (Semanas 5-8)

### **SPRINT 2.1: Vista Previa Mejorada** (Semana 5)
**Prioridad**: 🔴 CRÍTICA  
**Esfuerzo**: 3-4 días  
**Dependencias**: Ninguna

#### Objetivos
- Preview del PDF sin descargar
- Zoom y pan
- Navegación entre páginas

#### Tareas Técnicas Detalladas

##### 2.1.1: PDF Viewer Component
**Archivo**: `frontend/src/components/PDFViewer.jsx` (NUEVO)

**Librería**: `react-pdf` o `pdfjs-dist`

**Funcionalidades**:
- [ ] Renderizar PDF en canvas
- [ ] Zoom in/out (50% - 200%)
- [ ] Pan (arrastrar)
- [ ] Navegación de páginas
- [ ] Rotación
- [ ] Download button
- [ ] Fullscreen mode

**Implementación**:
```jsx
import { Document, Page, pdfjs } from 'react-pdf';
import 'react-pdf/dist/esm/Page/AnnotationLayer.css';

pdfjs.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjs.version}/pdf.worker.min.js`;

export default function PDFViewer({ pdfUrl }) {
    const [numPages, setNumPages] = useState(null);
    const [pageNumber, setPageNumber] = useState(1);
    const [scale, setScale] = useState(1.0);
    
    // Implementación completa...
}
```

##### 2.1.2: Preview Modal Mejorado
**Archivo**: `frontend/src/components/PreviewModal.jsx`

**Mejoras**:
- [ ] Reemplazar iframe con PDFViewer
- [ ] Controles de zoom
- [ ] Controles de navegación
- [ ] Botón de fullscreen
- [ ] Keyboard shortcuts (← → para navegar)

##### 2.1.3: Thumbnail Preview
**Archivo**: `frontend/src/components/FileThumbnail.jsx` (NUEVO)

**Funcionalidades**:
- [ ] Generar thumbnail del PDF
- [ ] Mostrar en FileExplorer
- [ ] Hover para preview rápido
- [ ] Cache de thumbnails

**Backend**: Endpoint para generar thumbnails
**Archivo**: `backend/app/routers/generation.py`

```python
@router.get("/files/thumbnail/{filename}")
async def get_thumbnail(filename: str):
    # Generar thumbnail usando Pillow
    # Cache en memoria o disco
    # Retornar como imagen
```

##### 2.1.4: Testing
- [ ] Test: Renderizado de PDF
- [ ] Test: Zoom funciona
- [ ] Test: Navegación de páginas
- [ ] Test: Performance con PDFs grandes

---

### **SPRINT 2.2: Drag & Drop** (Semana 5-6)
**Prioridad**: 🟡 ALTA  
**Esfuerzo**: 2-3 días  
**Dependencias**: Ninguna

#### Objetivos
- Arrastrar PDFs para regenerar
- Arrastrar imágenes para avatares
- Feedback visual

#### Tareas Técnicas Detalladas

##### 2.2.1: DropZone Component
**Archivo**: `frontend/src/components/DropZone.jsx` (NUEVO)

**Funcionalidades**:
- [ ] Detectar drag over
- [ ] Validar tipo de archivo
- [ ] Preview del archivo
- [ ] Feedback visual (border, overlay)

**Implementación**:
```jsx
export default function DropZone({ onDrop, accept, children }) {
    const [isDragging, setIsDragging] = useState(false);
    
    const handleDragOver = (e) => {
        e.preventDefault();
        setIsDragging(true);
    };
    
    const handleDrop = (e) => {
        e.preventDefault();
        setIsDragging(false);
        
        const files = Array.from(e.dataTransfer.files);
        const validFiles = files.filter(f => accept.includes(f.type));
        
        if (validFiles.length > 0) {
            onDrop(validFiles);
        }
    };
    
    return (
        <div
            onDragOver={handleDragOver}
            onDragLeave={() => setIsDragging(false)}
            onDrop={handleDrop}
            className={isDragging ? 'drag-active' : ''}
        >
            {children}
        </div>
    );
}
```

##### 2.2.2: Regenerar desde PDF
**Archivo**: `backend/app/routers/generation.py`

**Nuevo Endpoint**:
```python
@router.post("/regenerate-from-pdf")
async def regenerate_from_pdf(file: UploadFile):
    # Extraer texto del PDF usando PyPDF2 o pdfplumber
    # Parsear estructura
    # Regenerar con mejoras
    # Retornar nuevo PDF
```

**Frontend**: `frontend/src/lib/api.js`
```javascript
export const regenerateFromPdf = async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post('/api/regenerate-from-pdf', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
    });
    
    return response.data;
};
```

##### 2.2.3: Avatar desde Imagen
**Archivo**: `backend/app/services/krea_service.py`

**Nuevo método**:
```python
async def generate_avatar_from_image(
    image_path: str,
    style: str = "professional"
) -> Tuple[str, str]:
    # Usar img2img de Krea
    # Aplicar estilo profesional
    # Retornar nueva imagen
```

**Frontend**: Integrar en ConfigPanel
- [ ] DropZone para imagen
- [ ] Preview de imagen subida
- [ ] Botón "Generate Avatar from Image"

##### 2.2.4: Testing
- [ ] Test: Drag & drop funciona
- [ ] Test: Validación de tipos
- [ ] Test: Regeneración desde PDF
- [ ] Test: Avatar desde imagen

---

### **SPRINT 2.3: Atajos de Teclado** (Semana 6)
**Prioridad**: 🟡 MEDIA  
**Esfuerzo**: 1-2 días  
**Dependencias**: Ninguna

#### Objetivos
- Atajos globales
- Atajos contextuales
- Help modal con atajos

#### Tareas Técnicas Detalladas

##### 2.3.1: Hook de Atajos
**Archivo**: `frontend/src/hooks/useKeyboardShortcuts.js` (NUEVO)

**Implementación**:
```javascript
export function useKeyboardShortcuts(shortcuts) {
    useEffect(() => {
        const handleKeyDown = (e) => {
            const key = `${e.ctrlKey || e.metaKey ? 'Ctrl+' : ''}${e.shiftKey ? 'Shift+' : ''}${e.key}`;
            
            const shortcut = shortcuts.find(s => s.key === key);
            if (shortcut && !shortcut.disabled) {
                e.preventDefault();
                shortcut.handler();
            }
        };
        
        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [shortcuts]);
}
```

##### 2.3.2: Atajos Globales
**Archivo**: `frontend/src/App.jsx`

**Atajos a implementar**:
- [ ] `Ctrl/Cmd + G` → Iniciar generación
- [ ] `Ctrl/Cmd + D` → Descargar ZIP
- [ ] `Ctrl/Cmd + F` → Focus en búsqueda
- [ ] `Ctrl/Cmd + K` → Abrir command palette
- [ ] `Esc` → Cerrar modales
- [ ] `?` → Mostrar ayuda de atajos

**Implementación**:
```javascript
useKeyboardShortcuts([
    { key: 'Ctrl+g', handler: () => startGeneration() },
    { key: 'Ctrl+d', handler: () => downloadZip() },
    { key: 'Ctrl+f', handler: () => searchInputRef.current?.focus() },
    { key: '?', handler: () => setShowHelp(true) },
]);
```

##### 2.3.3: Command Palette
**Archivo**: `frontend/src/components/CommandPalette.jsx` (NUEVO)

**Funcionalidades**:
- [ ] Búsqueda de comandos
- [ ] Ejecutar acciones
- [ ] Navegación con teclado
- [ ] Categorías de comandos

**UI**:
```
┌─────────────────────────────────────┐
│ Command Palette                     │
│ [🔍 Type a command...]              │
├─────────────────────────────────────┤
│ Generation                          │
│   ▶ Generate CVs                    │
│   ▶ Stop Generation                 │
│ Files                               │
│   ▶ Download All                    │
│   ▶ Clear All                       │
└─────────────────────────────────────┘
```

##### 2.3.4: Help Modal
**Archivo**: `frontend/src/components/KeyboardShortcutsHelp.jsx` (NUEVO)

**Mostrar**:
- [ ] Lista de todos los atajos
- [ ] Agrupados por categoría
- [ ] Visual de teclas

---

### **SPRINT 2.4: Batch Operations** (Semana 6-7)
**Prioridad**: 🟡 ALTA  
**Esfuerzo**: 2-3 días  
**Dependencias**: FileExplorer

#### Objetivos
- Selección múltiple
- Acciones masivas
- Modo selección

#### Tareas Técnicas Detalladas

##### 2.4.1: Modo Selección
**Archivo**: `frontend/src/components/FileExplorer.jsx`

**Funcionalidades**:
- [ ] Toggle "Select Mode"
- [ ] Checkboxes en cada fila
- [ ] Select All / Deselect All
- [ ] Contador de seleccionados
- [ ] Barra de acciones flotante

**Estado**:
```javascript
const [selectionMode, setSelectionMode] = useState(false);
const [selectedFiles, setSelectedFiles] = useState(new Set());
```

**UI**:
```
┌─────────────────────────────────────┐
│ [☐] File1.pdf    [☐] File2.pdf     │
│ [☑] File3.pdf    [☐] File4.pdf     │
│                                     │
│ 2 selected                          │
│ [Delete] [Download] [Clear]         │
└─────────────────────────────────────┘
```

##### 2.4.2: Acciones Masivas
**Archivo**: `frontend/src/components/FileExplorer.jsx`

**Acciones**:
- [ ] Delete múltiples
- [ ] Download múltiples (individual, no ZIP)
- [ ] Regenerate PDFs
- [ ] Export metadata

**Implementación**:
```javascript
const handleBulkDelete = async () => {
    if (confirm(`Delete ${selectedFiles.size} files?`)) {
        const promises = Array.from(selectedFiles).map(filename => 
            deleteFile(filename)
        );
        await Promise.all(promises);
        setSelectedFiles(new Set());
        loadFiles();
    }
};
```

##### 2.4.3: Barra de Acciones Flotante
**Archivo**: `frontend/src/components/BulkActionsBar.jsx` (NUEVO)

**UI**:
```
┌─────────────────────────────────────┐
│ 5 files selected                   │
│ [Delete] [Download] [Export] [×]   │
└─────────────────────────────────────┘
```

---

### **SPRINT 2.5: Notificaciones del Sistema** (Semana 7)
**Prioridad**: 🟡 MEDIA  
**Esfuerzo**: 1-2 días  
**Dependencias**: Ninguna

#### Objetivos
- Notificaciones del navegador
- Sonido opcional
- Badge con contador

#### Tareas Técnicas Detalladas

##### 2.5.1: Service de Notificaciones
**Archivo**: `frontend/src/lib/notifications.js`

**Funcionalidades**:
- [ ] Solicitar permiso
- [ ] Enviar notificación
- [ ] Manejar clicks
- [ ] Badge en favicon

**Implementación**:
```javascript
export async function requestNotificationPermission() {
    if ('Notification' in window) {
        const permission = await Notification.requestPermission();
        return permission === 'granted';
    }
    return false;
}

export function sendNotification(title, options = {}) {
    if (Notification.permission === 'granted') {
        const notification = new Notification(title, {
            icon: '/icon.png',
            badge: '/badge.png',
            ...options
        });
        
        notification.onclick = () => {
            window.focus();
            notification.close();
        };
    }
}
```

##### 2.5.2: Integración con Generación
**Archivo**: `frontend/src/stores/useGenerationStore.js`

**Cambios**:
- [ ] Notificar cuando batch completa
- [ ] Notificar cuando task falla
- [ ] Sonido opcional (configurable)

##### 2.5.3: Badge en Favicon
**Archivo**: `frontend/src/lib/favicon.js` (NUEVO)

**Funcionalidades**:
- [ ] Actualizar favicon con número
- [ ] Reset cuando se ve
- [ ] Canvas para dibujar número

---

### **SPRINT 2.6: Exportar/Importar Configuración** (Semana 7-8)
**Prioridad**: 🟡 MEDIA  
**Esfuerzo**: 1-2 días  
**Dependencias**: Persistencia (Sprint 1.1)

#### Objetivos
- Exportar config como JSON
- Importar config desde JSON
- Validación de datos

#### Tareas Técnicas Detalladas

##### 2.6.1: Funciones de Export/Import
**Archivo**: `frontend/src/lib/storage.js`

**Ya implementado en Sprint 1.1, pero mejorar**:
- [ ] Validación de schema
- [ ] Migración de versiones
- [ ] Preview antes de importar
- [ ] Backup automático antes de importar

##### 2.6.2: UI Components
**Archivo**: `frontend/src/components/ConfigImportExport.jsx` (NUEVO)

**Funcionalidades**:
- [ ] Botón "Export Config"
- [ ] Botón "Import Config"
- [ ] Drag & drop para importar
- [ ] Preview de datos a importar

---

## 📅 FASE 3: FEATURES AVANZADAS (Semanas 9-16)

### **SPRINT 3.1: Vista de Comparación** (Semana 9-10)
**Prioridad**: 🟢 BAJA  
**Esfuerzo**: 4-5 días  
**Dependencias**: PDF Viewer (Sprint 2.1)

#### Objetivos
- Comparar 2-3 CVs lado a lado
- Highlight de diferencias
- Exportar comparación

#### Tareas Técnicas Detalladas

##### 3.1.1: Comparador Component
**Archivo**: `frontend/src/components/CVComparator.jsx` (NUEVO)

**Funcionalidades**:
- [ ] Seleccionar 2-3 CVs para comparar
- [ ] Vista side-by-side
- [ ] Sincronización de scroll
- [ ] Highlight de diferencias (usando diff algorithm)
- [ ] Exportar como PDF comparativo

**UI**:
```
┌─────────────────────────────────────┐
│ Compare CVs                         │
│ [Select CV 1 ▼] [Select CV 2 ▼]     │
├─────────────────────────────────────┤
│ CV 1          │ CV 2                │
│ [PDF Viewer]  │ [PDF Viewer]        │
│               │                      │
│ [Sync Scroll] [Export Comparison]   │
└─────────────────────────────────────┘
```

##### 3.1.2: Diff Algorithm
**Archivo**: `frontend/src/lib/diff.js` (NUEVO)

**Librería**: `diff` npm package

**Funcionalidades**:
- [ ] Extraer texto de ambos PDFs
- [ ] Comparar sección por sección
- [ ] Generar highlights
- [ ] Mostrar diferencias en UI

---

### **SPRINT 3.2: Editor de CV Inline** (Semana 10-12)
**Prioridad**: 🟢 BAJA  
**Esfuerzo**: 5-7 días  
**Dependencias**: Ninguna

#### Objetivos
- Editar campos directamente
- Regenerar solo secciones
- Guardar versiones

#### Tareas Técnicas Detalladas

##### 3.2.1: Editor Component
**Archivo**: `frontend/src/components/CVEditor.jsx` (NUEVO)

**Funcionalidades**:
- [ ] Cargar CV data (JSON)
- [ ] Editor de campos (name, email, experience, etc.)
- [ ] Validación en tiempo real
- [ ] Preview en tiempo real
- [ ] Guardar cambios
- [ ] Regenerar secciones específicas

**UI**:
```
┌─────────────────────────────────────┐
│ Edit CV: John Doe                   │
├─────────────────────────────────────┤
│ Name: [John Doe____________]        │
│ Email: [john@example.com___]        │
│                                     │
│ Experience:                         │
│ [Add Experience]                    │
│ • Senior Dev at Tech Corp           │
│   [Edit] [Delete]                   │
│                                     │
│ [Save] [Regenerate Section] [Cancel]│
└─────────────────────────────────────┘
```

##### 3.2.2: Backend para Regeneración Parcial
**Archivo**: `backend/app/routers/generation.py`

**Nuevo Endpoint**:
```python
@router.post("/regenerate-section")
async def regenerate_section(
    cv_data: dict,
    section: str,  # "experience", "skills", etc.
    context: dict
):
    # Regenerar solo una sección específica
    # Mantener el resto del CV igual
    # Retornar CV actualizado
```

##### 3.2.3: Versionado
**Archivo**: `frontend/src/lib/versioning.js` (NUEVO)

**Funcionalidades**:
- [ ] Guardar versiones del CV
- [ ] Historial de cambios
- [ ] Revertir a versión anterior
- [ ] Comparar versiones

---

### **SPRINT 3.3: Filtros Avanzados en DownloadZipPanel** (Semana 12-13)
**Prioridad**: 🟡 MEDIA  
**Esfuerzo**: 2-3 días  
**Dependencias**: Búsqueda (Sprint 1.2)

#### Objetivos
- Filtros por fecha, rol, tamaño
- Búsqueda dentro del panel
- Filtros combinados

#### Tareas Técnicas Detalladas

##### 3.3.1: Componente de Filtros
**Archivo**: `frontend/src/components/DownloadZipPanel.jsx`

**Mejoras**:
- [ ] Añadir sección de filtros
- [ ] Date range picker
- [ ] Size range slider
- [ ] Role multi-select
- [ ] Search input
- [ ] Clear filters button

**UI**:
```
┌─────────────────────────────────────┐
│ Download CVs as ZIP                 │
├─────────────────────────────────────┤
│ Filters:                            │
│ [Date: Last week ▼]                 │
│ [Size: 100-500 KB ▼]               │
│ [Role: Developer ▼]                 │
│ [🔍 Search...]                      │
│ [Clear Filters]                     │
├─────────────────────────────────────┤
│ Files (filtered: 5 of 20)          │
│ ...                                 │
└─────────────────────────────────────┘
```

---

### **SPRINT 3.4: Preview Mejorado sin Descargar** (Semana 13-14)
**Prioridad**: 🟡 ALTA  
**Esfuerzo**: 2-3 días  
**Dependencias**: PDF Viewer (Sprint 2.1)

#### Objetivos
- Preview hover en FileExplorer
- Preview rápido
- Thumbnails

#### Tareas Técnicas Detalladas

##### 3.4.1: Hover Preview
**Archivo**: `frontend/src/components/FileExplorer.jsx`

**Funcionalidades**:
- [ ] Tooltip con preview al hover
- [ ] Delay de 500ms antes de mostrar
- [ ] Preview pequeño (200x300px)
- [ ] Click para abrir modal completo

##### 3.4.2: Thumbnail Generation
**Backend**: `backend/app/routers/generation.py`

**Endpoint**:
```python
@router.get("/files/thumbnail/{filename}")
async def get_thumbnail(filename: str, size: int = 200):
    # Generar thumbnail del PDF
    # Retornar como imagen PNG
```

**Frontend**: Cache de thumbnails
- [ ] Cache en memoria
- [ ] Lazy loading
- [ ] Placeholder mientras carga

---

## 📅 FASE 4: OPTIMIZACIÓN (Semanas 17-20)

### **SPRINT 4.1: Caché de Resultados** (Semana 17-18)
**Prioridad**: 🟡 ALTA  
**Esfuerzo**: 3-4 días  
**Dependencias**: Backend

#### Objetivos
- Cachear respuestas de LLM similares
- Reutilizar avatares
- Reducir costos

#### Tareas Técnicas Detalladas

##### 4.1.1: Sistema de Caché
**Archivo**: `backend/app/core/cache.py` (NUEVO)

**Funcionalidades**:
- [ ] Cache en memoria (Redis opcional)
- [ ] Hash de prompts para matching
- [ ] TTL configurable
- [ ] Invalidación inteligente

**Implementación**:
```python
import hashlib
import json
from functools import lru_cache

class ResponseCache:
    def __init__(self, ttl=3600):
        self.cache = {}
        self.ttl = ttl
    
    def get_key(self, prompt, model):
        data = json.dumps({'prompt': prompt, 'model': model}, sort_keys=True)
        return hashlib.md5(data.encode()).hexdigest()
    
    def get(self, prompt, model):
        key = self.get_key(prompt, model)
        entry = self.cache.get(key)
        if entry and time.time() - entry['timestamp'] < self.ttl:
            return entry['response']
        return None
    
    def set(self, prompt, model, response):
        key = self.get_key(prompt, model)
        self.cache[key] = {
            'response': response,
            'timestamp': time.time()
        }
```

##### 4.1.2: Integración en LLM Service
**Archivo**: `backend/app/services/llm_service.py`

**Cambios**:
- [ ] Verificar cache antes de llamar API
- [ ] Guardar respuesta en cache
- [ ] Log de cache hits/misses

##### 4.1.3: Cache de Avatares
**Archivo**: `backend/app/services/krea_service.py`

**Funcionalidades**:
- [ ] Cachear avatares por parámetros
- [ ] Reutilizar si parámetros similares
- [ ] Variación aleatoria mínima

---

### **SPRINT 4.2: Rate Limiting y Throttling** (Semana 18-19)
**Prioridad**: 🔴 CRÍTICA  
**Esfuerzo**: 2-3 días  
**Dependencias**: Backend

#### Objetivos
- Límites por usuario/IP
- Queue management
- Priorización

#### Tareas Técnicas Detalladas

##### 4.2.1: Rate Limiter
**Archivo**: `backend/app/core/rate_limiter.py` (NUEVO)

**Librería**: `slowapi` o implementación custom

**Implementación**:
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/generate")
@limiter.limit("10/minute")
async def start_generation(...):
    # ...
```

##### 4.2.2: Queue Management
**Archivo**: `backend/app/core/task_manager.py`

**Mejoras**:
- [ ] Prioridad de tareas
- [ ] Límite de tareas concurrentes
- [ ] Queue de espera
- [ ] Estimación de tiempo

---

### **SPRINT 4.3: Logging Estructurado** (Semana 19-20)
**Prioridad**: 🟡 MEDIA  
**Esfuerzo**: 2-3 días  
**Dependencias**: Backend

#### Objetivos
- Logs centralizados
- Trazabilidad
- Alertas

#### Tareas Técnicas Detalladas

##### 4.3.1: Sistema de Logging
**Archivo**: `backend/app/core/logging_config.py` (NUEVO)

**Librería**: `structlog` o `loguru`

**Implementación**:
```python
import structlog

logger = structlog.get_logger()

# Uso
logger.info("generation_started", 
    batch_id=batch_id, 
    qty=qty,
    user_id=user_id
)
```

##### 4.3.2: Integración
- [ ] Log todas las operaciones importantes
- [ ] Request ID tracking
- [ ] Performance metrics
- [ ] Error tracking

---

## 📅 FASE 5: ESCALABILIDAD (Semanas 21-24)

### **SPRINT 5.1: Webhooks** (Semana 21-22)
**Prioridad**: 🟢 BAJA  
**Esfuerzo**: 3-4 días  
**Dependencias**: Backend

#### Objetivos
- Notificaciones cuando termina
- Integración externa
- Callbacks

#### Tareas Técnicas Detalladas

##### 5.1.1: Webhook Service
**Archivo**: `backend/app/services/webhook_service.py` (NUEVO)

**Funcionalidades**:
- [ ] Registrar webhooks
- [ ] Enviar eventos
- [ ] Retry en caso de fallo
- [ ] Signature verification

---

### **SPRINT 5.2: API Pública Documentada** (Semana 22-23)
**Prioridad**: 🟢 BAJA  
**Esfuerzo**: 3-4 días  
**Dependencias**: Backend

#### Objetivos
- OpenAPI/Swagger docs
- SDK
- Rate limits claros

#### Tareas Técnicas Detalladas

##### 5.2.1: OpenAPI Docs
**Archivo**: `backend/app/main.py`

**FastAPI ya genera docs automáticamente, pero mejorar**:
- [ ] Añadir ejemplos
- [ ] Documentar errores
- [ ] Añadir schemas detallados
- [ ] Customizar UI

##### 5.2.2: SDK
**Archivo**: `sdk/python/` (NUEVO)

**Crear SDK en Python**:
- [ ] Cliente wrapper
- [ ] Métodos type-safe
- [ ] Documentación
- [ ] Ejemplos

---

## 📊 RESUMEN DE PRIORIZACIÓN

### 🔴 CRÍTICO (Implementar primero)
1. ✅ Persistencia de Preferencias (Sprint 1.1)
2. ✅ Búsqueda y Filtrado (Sprint 1.2)
3. ✅ Mejoras de Error Handling (Sprint 1.4)
4. ✅ Vista Previa Mejorada (Sprint 2.1)
5. ✅ Rate Limiting (Sprint 4.2)

### 🟡 ALTA (Implementar después)
6. Modo Oscuro/Claro (Sprint 1.3)
7. Drag & Drop (Sprint 2.2)
8. Batch Operations (Sprint 2.4)
9. Caché de Resultados (Sprint 4.1)
10. Estadísticas Básicas (Sprint 1.5)

### 🟢 MEDIA/BAJA (Nice to have)
11. Atajos de Teclado (Sprint 2.3)
12. Notificaciones del Sistema (Sprint 2.5)
13. Vista de Comparación (Sprint 3.1)
14. Editor de CV (Sprint 3.2)
15. Webhooks (Sprint 5.1)

---

## 🧪 ESTRATEGIA DE TESTING

### Por Feature
- [ ] Unit tests para lógica de negocio
- [ ] Integration tests para APIs
- [ ] E2E tests para flujos críticos
- [ ] Performance tests para operaciones pesadas

### Herramientas
- **Frontend**: Vitest + Testing Library
- **Backend**: Pytest + pytest-asyncio
- **E2E**: Playwright

---

## 📝 DOCUMENTACIÓN REQUERIDA

### Por Feature
- [ ] README actualizado
- [ ] API documentation
- [ ] User guide (opcional)
- [ ] Changelog

---

## 🚀 PLAN DE DEPLOYMENT

### Releases Incrementales
- **v1.1.0**: Fase 1 completa (Semanas 1-4)
- **v1.2.0**: Fase 2 completa (Semanas 5-8)
- **v1.3.0**: Fase 3 completa (Semanas 9-16)
- **v1.4.0**: Fase 4 completa (Semanas 17-20)
- **v2.0.0**: Fase 5 completa (Semanas 21-24)

### Estrategia
- Feature flags para features nuevas
- Rollback plan para cada release
- Monitoring post-deployment

---

## ⚠️ RIESGOS Y MITIGACIÓN

### Riesgos Identificados
1. **Performance**: Caché y optimizaciones
2. **Costos API**: Rate limiting y caché
3. **Complejidad**: Desarrollo incremental
4. **Testing**: Cobertura desde el inicio

---

¿Quieres que empiece a implementar alguna feature específica o prefieres que detalle más algún sprint en particular?

