export default function ResultPanel({ result, onReset }) {
    const { excalidraw, metadata } = result;

    const handleDownload = () => {
        const blob = new Blob([JSON.stringify(excalidraw, null, 2)], {
            type: 'application/json',
        });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'flowchart.excalidraw';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    };

    const handleOpenExcalidraw = () => {
        // Excalidraw can import files via the web UI
        // We'll open excalidraw.com and user can drag-drop the file
        window.open('https://excalidraw.com', '_blank');
    };

    return (
        <div className="result-container">
            <div className="result-card">
                <div className="result-header">
                    <span className="result-icon">✅</span>
                    <div>
                        <h3 className="result-title">Conversion Complete!</h3>
                        <p className="result-subtitle">
                            Your flowchart is ready as an Excalidraw file
                        </p>
                    </div>
                </div>

                <div className="result-stats">
                    <div className="stat-badge">
                        <span className="stat-value">{metadata.nodes_count}</span> shapes detected
                    </div>
                    <div className="stat-badge">
                        <span className="stat-value">{metadata.arrows_count}</span> connections found
                    </div>
                </div>

                <div className="result-actions">
                    <button className="btn-download" onClick={handleDownload}>
                        ⬇️ Download .excalidraw
                    </button>
                    <button className="btn-open-excalidraw" onClick={handleOpenExcalidraw}>
                        🖊️ Open Excalidraw
                    </button>
                    <button className="btn-new" onClick={onReset}>
                        🔄 Convert Another
                    </button>
                </div>
            </div>
        </div>
    );
}
