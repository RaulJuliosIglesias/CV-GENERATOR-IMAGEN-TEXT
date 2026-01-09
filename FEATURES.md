# 🎯 Feature Documentation

> **Comprehensive guide to all features and capabilities of the AI CV Generator**

---

## 📑 Table of Contents

1. [Core Features](#core-features)
2. [File Management](#file-management)
3. [CV Comparison](#cv-comparison)
4. [Batch Operations](#batch-operations)
5. [Statistics & Analytics](#statistics--analytics)
6. [Configuration & Templates](#configuration--templates)
7. [User Interface](#user-interface)

---

## 🎯 Core Features

### CV Generation

The system generates professional CVs through a multi-phase orchestration process:

1. **Profile Generation**: Creates realistic professional profiles using LLM
2. **Content Creation**: Generates work history, skills, and achievements
3. **Avatar Generation**: Creates photorealistic headshots using Krea AI
4. **HTML Rendering**: Assembles CV using Jinja2 templates
5. **PDF Export**: Converts HTML to PDF using Playwright

**Key Capabilities**:
- ✅ Multi-model AI orchestration (OpenRouter + Krea)
- ✅ Parametric career engine (prevents unrealistic career paths)
- ✅ Anti-bias imaging engine (diverse, modern avatars)
- ✅ Batch generation support
- ✅ Real-time progress tracking

---

## 📁 File Management

### File Explorer

The File Explorer provides comprehensive file management capabilities:

#### **Search & Filter**
- **Full-text Search**: Search by name, role, or ID
- **Role Filtering**: Filter files by professional role
- **Real-time Results**: Instant filtering as you type

#### **File Display**
- **Metadata Extraction**: Automatically parses filename to extract:
  - Unique ID
  - Person name
  - Professional role
- **Formatted Display**: Clean, readable file information
- **Pagination**: Handles large file lists efficiently (50 per page)

#### **File Actions**
- **Click-to-Open**: Click anywhere on file to open preview
- **Download PDF**: Direct download of generated PDF
- **Delete File**: Remove files from system
- **Preview Modal**: Full-screen preview with zoom and navigation

#### **Resizable Panel**
- **Drag Handle**: Visual resize handle between tools and file explorer
- **Height Persistence**: Remembers preferred height across sessions
- **Smooth Resizing**: Real-time height adjustment
- **Min/Max Limits**: Prevents extreme sizes (150px - 800px)

### File Organization
```
Files are organized by:
- Creation date (newest first)
- Name (alphabetical)
- Role (category)
- ID (unique identifier)
```

---

## 🔍 CV Comparison

### Overview

Compare up to 4 CVs side-by-side in a dedicated comparison view.

### Features

#### **File Selection**
- **Search Functionality**: 
  - Search by name, role, or ID
  - Real-time filtering
  - Highlights matching files
  
- **Complete File Access**:
  - All files available (not limited to first 10)
  - Scrollable list with all CVs
  - Metadata display for each file

- **Bulk Selection**:
  - "Select All" button (respects 4-file limit)
  - "Deselect All" button
  - Individual file selection with checkboxes

#### **Visual Selection**
- **Rich File Cards**: 
  - Name, role, and ID displayed
  - Color-coded badges for roles
  - Selection state clearly indicated
  
- **Selected Files Display**:
  - Shows all selected files at top
  - Easy removal with X button
  - Visual distinction from unselected files

#### **Comparison View**
- **Side-by-Side Display**:
  - 2 files: 2-column grid
  - 3 files: 3-column grid
  - 4 files: 2x2 grid
  
- **Interactive Preview**:
  - Full HTML rendering in iframe
  - Pretty-print option
  - Download and preview buttons per file
  
- **Navigation**:
  - Easy file switching
  - Close button to exit comparison

### Usage Workflow

1. **Open Comparison Panel**: Click to expand "Compare CVs" section
2. **Search Files**: Use search bar to find specific CVs
3. **Select Files**: Click checkboxes or use "Select All"
4. **Open Comparison**: Click "Open Comparison View" (requires 2+ files)
5. **Compare**: View CVs side-by-side with full HTML rendering

---

## 📦 Batch Operations

### Overview

Perform bulk operations on multiple files simultaneously.

### Available Operations

#### **Batch Delete**
- Select multiple files
- Delete all selected files at once
- Confirmation dialog for safety

#### **Batch Download**
- Select multiple files
- Download all as individual PDFs
- Progress tracking during download

### Selection Interface
- **Select All**: Toggle to select/deselect all files
- **Individual Selection**: Checkboxes for each file
- **Selection Counter**: Shows number of selected files

---

## 📊 Statistics & Analytics

### Statistics Panel

The Statistics Panel provides insights into CV generation activity.

#### **Key Metrics**
- **Total Generations**: Total number of CVs generated
- **Success Rate**: Percentage of successful generations
- **Average Time**: Average generation time per CV
- **Failed Generations**: Count of failed attempts

#### **Role Analytics**
- **Top Roles**: Most frequently generated roles
- **Role Distribution**: Breakdown by professional category
- **Trend Analysis**: Generation patterns over time

#### **Features**
- **Collapsible Panel**: Save space when not needed
- **Auto-refresh**: Updates every 5 seconds
- **Persistent State**: Remembers expanded/collapsed state

---

## ⚙️ Configuration & Templates

### Configuration Panel

Configure generation parameters:

#### **Basic Settings**
- **Role Selection**: Choose from 982+ professional roles
- **Gender**: Select gender representation
- **Ethnicity**: Choose ethnic representation
- **Origin**: Select geographic origin
- **Expertise Level**: Set experience level

#### **AI Model Selection**
- **LLM Models**: Choose from available language models
  - Google Gemini 2.0 (Free)
  - GPT-4 Turbo
  - Claude 3 Opus
  - And more...
  
- **Image Models**: Select image generation model
  - Flux-1-Dev (Best Quality)
  - Imagen-4
  - Seedream

#### **Advanced Options**
- **Batch Size**: Number of CVs to generate
- **Template Selection**: Choose CV template
- **Output Format**: HTML, PDF, or both

### Template Management

#### **Save Templates**
- Save current configuration as template
- Add name and description
- Quick access to saved configurations

#### **Template Features**
- **Load Template**: Apply saved configuration instantly
- **Delete Template**: Remove unused templates
- **Export/Import**: Share configurations via JSON

#### **Template Organization**
- List view of all saved templates
- Search and filter templates
- Collapsible panel for space efficiency

---

## 🎨 User Interface

### Layout Structure

```
┌─────────────────────────────────────────┐
│  Sidebar (Config Panel)  │  Main Area  │
│                          │
│  - Configuration          │  Progress   │
│  - Model Selection        │  Tracker    │
│  - Template Manager       ├─────────────┤
│                           │  Tools      │
│                           │  Panel [▼] │
│                           ├═════════════┤
│                           │  File       │
│                           │  Explorer   │
│                           │  (Resizable)│
└─────────────────────────────────────────┘
```

### Tools Panel

Unified panel containing:
- **Statistics**: Generation metrics
- **CV Comparison**: Side-by-side comparison
- **Batch Operations**: Bulk file operations
- **Download ZIP**: Multi-file download

**Features**:
- Collapsible to save space
- State persistence
- Clean, organized layout

### Responsive Design

- **Adaptive Layout**: Adjusts to screen size
- **Collapsible Panels**: Maximize workspace
- **Resizable Components**: Customize layout
- **Touch-Friendly**: Works on tablets

### Accessibility

- **Keyboard Navigation**: Full keyboard support
- **Screen Reader Support**: ARIA labels
- **High Contrast**: Readable in all themes
- **Focus Indicators**: Clear focus states

---

## 🔧 Advanced Features

### Error Handling

- **Graceful Degradation**: App continues working with partial data
- **User-Friendly Messages**: Clear error descriptions
- **Error Boundaries**: Prevents app crashes
- **Retry Mechanisms**: Automatic retry for transient errors

### Performance

- **Optimized API Calls**: Reduced timeouts and fallbacks
- **Efficient State Management**: Prevents unnecessary re-renders
- **Lazy Loading**: Components load on demand
- **Caching**: Response caching for faster access

### Persistence

- **LocalStorage Integration**: 
  - Panel states
  - File explorer height
  - User preferences
  - Templates and configurations

---

## 📱 Keyboard Shortcuts

| Shortcut | Action |
|:---------|:-------|
| `Ctrl/Cmd + G` | Start generation |
| `Ctrl/Cmd + S` | Stop generation |
| `Ctrl/Cmd + K` | Clear queue |
| `F5` | Refresh file list |

---

## 🎯 Best Practices

### File Management
- Use search to quickly find specific CVs
- Use filters to narrow down by role
- Keep file explorer height comfortable for viewing

### Comparison
- Use comparison tool to review multiple CVs
- Search before selecting to find specific files
- Use "Select All" for quick bulk selection

### Configuration
- Save frequently used configurations as templates
- Export configurations for backup
- Use batch operations for efficiency

---

## 📚 Additional Resources

- [README.md](./README.md) - Project overview
- [CHANGELOG.md](./CHANGELOG.md) - Version history
- [QUICKSTART.md](./QUICKSTART.md) - Setup guide
- [ROADMAP.md](./ROADMAP.md) - Future plans

---

**Last Updated**: January 2025  
**Version**: 2.0.0
