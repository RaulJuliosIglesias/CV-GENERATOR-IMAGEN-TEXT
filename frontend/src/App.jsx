import ConfigPanel from './components/ConfigPanel';
import ProgressTracker from './components/ProgressTracker';
import FileExplorer from './components/FileExplorer';

function App() {
    return (
        <div className="flex h-screen overflow-hidden bg-background">
            {/* Sidebar - Config Panel */}
            <ConfigPanel />

            {/* Main Content */}
            <main className="flex-1 flex flex-col overflow-hidden">
                {/* Progress Tracker */}
                <ProgressTracker />

                {/* File Explorer */}
                <FileExplorer />
            </main>
        </div>
    );
}

export default App;
