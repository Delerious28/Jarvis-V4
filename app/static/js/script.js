// Error Boundary Component to catch errors in child components
class ErrorBoundary extends React.Component {
    constructor(props) {
        super(props);
        this.state = { hasError: false, error: null };
    }

    static getDerivedStateFromError(error) {
        return { hasError: true, error: error };
    }

    componentDidCatch(error, errorInfo) {
        console.error("Uncaught error:", error, errorInfo);
    }

    render() {
        if (this.state.hasError) {
            return (
                <div className="card" style={{ gridColumn: '1 / -1', backgroundColor: '#401a1a', borderColor: 'red' }}>
                    <h2><i className="icon">⚠️</i> Application Error</h2>
                    <p>Jarvis has encountered a critical error. Please check the developer console for details.</p>
                    <pre style={{ whiteSpace: 'pre-wrap', backgroundColor: '#10101a', padding: '1rem', borderRadius: '8px' }}>
                        {this.state.error && this.state.error.toString()}
                    </pre>
                </div>
            );
        }
        return this.props.children;
    }
}

// Modal Component for configuring lights
const LightConfigModal = ({ allLights, visibleLights, onClose, onSave }) => {
    const [selectedLights, setSelectedLights] = React.useState(new Set(visibleLights));

    const handleCheckboxChange = (lightName) => {
        setSelectedLights(prev => {
            const next = new Set(prev);
            if (next.has(lightName)) {
                next.delete(lightName);
            } else {
                next.add(lightName);
            }
            return next;
        });
    };

    const handleSave = () => onSave(Array.from(selectedLights));

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal-content" onClick={e => e.stopPropagation()}>
                <div className="modal-header">
                    <h3>Configure Visible Lights</h3>
                    <button className="modal-close-button" onClick={onClose}>&times;</button>
                </div>
                <div className="modal-body">
                    {allLights.map(light => (
                        <div key={light} className="modal-light-item">
                            <input
                                type="checkbox"
                                id={`light-checkbox-${light}`}
                                checked={selectedLights.has(light)}
                                onChange={() => handleCheckboxChange(light)}
                            />
                            <label htmlFor={`light-checkbox-${light}`}>{light}</label>
                        </div>
                    ))}
                </div>
                <div className="modal-footer">
                    <button className="action-button" onClick={handleSave}>Save Configuration</button>
                </div>
            </div>
        </div>
    );
};

// Main Application Component
const App = () => {
    const [command, setCommand] = React.useState('');
    const [response, setResponse] = React.useState('Welcome to your Jarvis V4 Interface.');
    const [systemStatus, setSystemStatus] = React.useState({ cpu: 'Loading...', ram: 'Loading...', temp: 'Loading...', weather: 'Loading...' });
    const [lightsData, setLightsData] = React.useState({ all: [], visible: [] });
    const [todoList, setTodoList] = React.useState([]);
    const [isModalOpen, setIsModalOpen] = React.useState(false);
    const [loading, setLoading] = React.useState({ status: true, lights: true, todo: true });
    
    const playTextAsSpeech = (text) => {
        if (!text || text.trim() === '') return;
        const audioUrl = `/api/tts?text=${encodeURIComponent(text)}`;
        const audio = new Audio(audioUrl);
        audio.play().catch(e => {
            console.error("Audio playback failed:", e);
            setResponse(prev => `${prev}\n(Could not play audio due to browser policy)`);
        });
    };

    const api = {
        post: async (endpoint, body) => {
            const res = await fetch(endpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body),
            });
            if (!res.ok) throw new Error(`API Error: ${res.status}`);
            return res.json();
        },
        get: async (endpoint) => {
            const res = await fetch(endpoint);
            if (!res.ok) throw new Error(`API Error: ${res.status}`);
            return res.json();
        },
    };

    const sendCommand = async (cmd) => {
        setResponse(`Executing: "${cmd}"...`);
        try {
            const data = await api.post('/api/command', { command: cmd });
            const responseText = data.response_text || `Command "${cmd}" executed successfully.`;
            setResponse(responseText);
            if (data.speak_response) {
                playTextAsSpeech(responseText);
            }
            if (cmd.includes('to-do')) {
                fetchTodoList();
            }
        } catch (error) {
            console.error('Error sending command:', error);
            setResponse(`Error executing command. See console for details.`);
        }
    };

    const fetchTodoList = async () => {
        setLoading(prev => ({ ...prev, todo: true }));
        try {
            const tasks = await api.get('/api/todo');
            setTodoList(tasks);
        } catch (error) {
            console.error('Failed to fetch to-do list:', error);
        } finally {
            setLoading(prev => ({ ...prev, todo: false }));
        }
    };

    const clearTodoList = async () => {
        try {
            await api.post('/api/todo/clear');
            setTodoList([]);
            setResponse("To-do list has been cleared.");
            playTextAsSpeech("To-do list has been cleared.");
        } catch (error) {
            console.error('Failed to clear to-do list:', error);
            setResponse("Error clearing the to-do list.");
        }
    };

    const fetchAllData = React.useCallback(async () => {
        setLoading({ status: true, lights: true, todo: true });
        try {
            const [statusData, lightsInfo, todoData] = await Promise.all([
                api.get('/api/status'),
                api.get('/api/lights'),
                api.get('/api/todo'),
            ]);
            setSystemStatus(statusData);
            if (lightsInfo.error) {
                setResponse(`Hue Lights Error: ${lightsInfo.error}`);
            } else {
                setLightsData({ all: lightsInfo.all_lights || [], visible: lightsInfo.visible_lights || [] });
            }
            setTodoList(todoData);
        } catch (error) {
            console.error('Failed to fetch initial data:', error);
            setResponse('Connection to backend failed. Is the server running?');
        } finally {
            setLoading({ status: false, lights: false, todo: false });
        }
    }, []);

    const saveLightConfiguration = async (newVisibleLights) => {
        try {
            await api.post('/api/lights/config', { visible_lights: newVisibleLights });
            setLightsData(prev => ({ ...prev, visible: newVisibleLights }));
            setIsModalOpen(false);
            setResponse('Light configuration saved.');
        } catch (error) {
            console.error('Error saving light config:', error);
            setResponse('Failed to save light configuration.');
        }
    };

    React.useEffect(() => {
        fetchAllData();
        const intervalId = setInterval(() => api.get('/api/status').then(setSystemStatus).catch(console.error), 10000);
        return () => clearInterval(intervalId);
    }, [fetchAllData]);

    const handleCommandSubmit = (e) => {
        e.preventDefault();
        if (!command.trim()) return;
        sendCommand(command);
        setCommand('');
    };

    return (
        <React.Fragment>
            <div className="card command-center">
                <h2>Command Center</h2>
                <form onSubmit={handleCommandSubmit}>
                    <input
                        type="text"
                        className="command-input"
                        value={command}
                        onChange={(e) => setCommand(e.target.value)}
                        placeholder="Ask Jarvis anything..."
                    />
                </form>
                <div className="response-area">{response}</div>
            </div>

            <div className="card status-dashboard">
                <h2>System Status</h2>
                <div className="status-grid">
                    {Object.entries(systemStatus).map(([key, value]) => (
                        <div className="status-item" key={key}>
                            <strong>{key.toUpperCase()}:</strong> {loading.status ? 'Loading...' : value}
                        </div>
                    ))}
                </div>
            </div>

            <div className="card quick-actions">
                <h2>Quick Actions</h2>
                <div className="quick-actions-grid">
                    <button className="action-button" onClick={() => sendCommand('give me my daily briefing')}>Daily Briefing</button>
                    <button className="action-button" onClick={() => sendCommand('start movie mode')}>Movie Mode</button>
                    <button className="action-button" onClick={() => sendCommand('start work mode')}>Work Mode</button>
                    <button className="action-button" onClick={() => sendCommand('start code mode')}>Code Mode</button>
                    <button className="action-button" onClick={() => sendCommand('turn on my pc')}>Wake PC</button>
                </div>
            </div>

            <div className="card lights-control">
                <h2>
                    <span>Lights Control</span>
                    <button className="config-button" onClick={() => setIsModalOpen(true)}>Configure</button>
                </h2>
                <div className="lights-control-list">
                    {loading.lights ? <p>Loading lights...</p> :
                     lightsData.visible.length > 0 ? lightsData.visible.map(light => (
                        <div className="light-item" key={light}>
                            <span>{light}</span>
                            <div>
                                <button onClick={() => sendCommand(`turn on ${light}`)}>On</button>
                                <button onClick={() => sendCommand(`turn off ${light}`)}>Off</button>
                            </div>
                        </div>
                    )) : <p>No visible lights. Click 'Configure' to add them.</p>}
                </div>
            </div>

            <div className="card todo-list-card">
                <h2>
                    <span>To-Do List</span>
                    <button className="config-button" onClick={clearTodoList}>Clear All</button>
                </h2>
                <div className="lights-control-list">
                    {loading.todo ? <p>Loading tasks...</p> :
                     todoList.length > 0 ? todoList.map((task, index) => (
                        <div className="light-item" key={index}>
                            <span>{task}</span>
                        </div>
                     )) : <p>No tasks. Add one via the command center!</p>
                    }
                </div>
            </div>
            
            <div className="card network-diagnostics">
                <h2>Network Diagnostics</h2>
                <div className="quick-actions-grid">
                    <button className="action-button" onClick={() => sendCommand('ping google.com')}>Ping Google</button>
                    <button className="action-button" onClick={() => sendCommand('run a speed test')}>Run Speed Test</button>
                </div>
            </div>

            {/* New Media Controls Card */}
            <div className="card media-controls">
                <h2>Media Controls</h2>
                <div className="quick-actions-grid">
                    <button className="action-button" onClick={() => sendCommand('previous track')}>Prev</button>
                    <button className="action-button" onClick={() => sendCommand('play pause media')}>Play/Pause</button>
                    <button className="action-button" onClick={() => sendCommand('next track')}>Next</button>
                    <button className="action-button" onClick={() => sendCommand('volume down')}>Vol -</button>
                    <button className="action-button" onClick={() => sendCommand('volume up')}>Vol +</button>
                    <button className="action-button" onClick={() => sendCommand('mute')}>Mute</button>
                </div>
            </div>

            {isModalOpen && (
                <LightConfigModal
                    allLights={lightsData.all}
                    visibleLights={lightsData.visible}
                    onClose={() => setIsModalOpen(false)}
                    onSave={saveLightConfiguration}
                />
            )}
        </React.Fragment>
    );
};

ReactDOM.render(
    <ErrorBoundary>
        <App />
    </ErrorBoundary>,
    document.getElementById('root')
);
