/**
 * TruVex AI - Interactive Source Relationship Graph
 * Visual flow: USER URL -> PLATFORM -> ARTICLE -> CLAIMS -> SOURCES -> VERDICT
 */

function renderSourceGraph(graphData, containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;
    container.innerHTML = "";

    if (!graphData || !graphData.nodes || graphData.nodes.length === 0) {
        container.innerHTML = `
            <div style="display:flex;height:100%;align-items:center;justify-content:center;color:#64748b;font-size:0.875rem;">
                No relationship nodes available for direct text without verified claims.
            </div>
        `;
        return;
    }

    const width = container.clientWidth || 900;
    const height = 420;

    // Create SVG with responsive viewBox
    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute("viewBox", `0 0 ${width} ${height}`);
    svg.setAttribute("class", "graph-svg");

    // Defs for arrowheads & filters
    const defs = document.createElementNS("http://www.w3.org/2000/svg", "defs");
    defs.innerHTML = `
        <marker id="arrow-neutral" viewBox="0 0 10 10" refX="22" refY="5" markerWidth="6" markerHeight="6" orient="auto">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#b91c1c" />
        </marker>
        <marker id="arrow-supports" viewBox="0 0 10 10" refX="22" refY="5" markerWidth="6" markerHeight="6" orient="auto">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#10b981" />
        </marker>
        <marker id="arrow-contradicts" viewBox="0 0 10 10" refX="22" refY="5" markerWidth="6" markerHeight="6" orient="auto">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#ef4444" />
        </marker>
        <filter id="glow-emerald" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="3" result="blur" />
            <feComposite in="SourceGraphic" in2="blur" operator="over" />
        </filter>
    `;
    svg.appendChild(defs);

    const g = document.createElementNS("http://www.w3.org/2000/svg", "g");
    svg.appendChild(g);

    // Layout hierarchy into horizontal columns (X coordinate based on category)
    const columns = {
        "url": width * 0.08,
        "platform": width * 0.22,
        "content": width * 0.38,
        "claim": width * 0.58,
        "source": width * 0.78,
        "verdict": width * 0.92
    };

    // Group nodes by category to distribute vertically (Y coordinate)
    const nodesByCategory = {};
    graphData.nodes.forEach(node => {
        if (!nodesByCategory[node.category]) {
            nodesByCategory[node.category] = [];
        }
        nodesByCategory[node.category].push(node);
    });

    const nodePositions = {};
    Object.keys(nodesByCategory).forEach(cat => {
        const list = nodesByCategory[cat];
        const colX = columns[cat] || width * 0.5;
        const count = list.length;
        list.forEach((node, i) => {
            const spacing = height / (count + 1);
            const colY = spacing * (i + 1);
            nodePositions[node.id] = { x: colX, y: colY, data: node };
        });
    });

    // Draw Edges
    const edgesGroup = document.createElementNS("http://www.w3.org/2000/svg", "g");
    graphData.edges.forEach(edge => {
        const src = nodePositions[edge.source];
        const tgt = nodePositions[edge.target];
        if (!src || !tgt) return;

        const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
        const dx = (tgt.x - src.x) * 0.5;
        const d = `M ${src.x} ${src.y} C ${src.x + dx} ${src.y}, ${tgt.x - dx} ${tgt.y}, ${tgt.x} ${tgt.y}`;
        
        path.setAttribute("d", d);
        path.setAttribute("fill", "none");
        
        let strokeColor = "rgba(239, 68, 68, 0.3)";
        let markerId = "arrow-neutral";
        let strokeDash = "none";

        if (edge.relation === "supports") {
            strokeColor = "#10b981";
            markerId = "arrow-supports";
        } else if (edge.relation === "contradicts") {
            strokeColor = "#ef4444";
            markerId = "arrow-contradicts";
            strokeDash = "4,3";
        }

        path.setAttribute("stroke", strokeColor);
        path.setAttribute("stroke-width", "1.75");
        path.setAttribute("stroke-dasharray", strokeDash);
        path.setAttribute("marker-end", `url(#${markerId})`);
        path.setAttribute("opacity", "0.75");
        
        // Edge label (hoverable)
        const title = document.createElementNS("http://www.w3.org/2000/svg", "title");
        title.textContent = `${edge.label} (${edge.relation})`;
        path.appendChild(title);

        edgesGroup.appendChild(path);
    });
    g.appendChild(edgesGroup);

    // Draw Nodes
    const nodesGroup = document.createElementNS("http://www.w3.org/2000/svg", "g");
    Object.keys(nodePositions).forEach(id => {
        const pos = nodePositions[id];
        const node = pos.data;

        const nodeG = document.createElementNS("http://www.w3.org/2000/svg", "g");
        nodeG.setAttribute("transform", `translate(${pos.x}, ${pos.y})`);
        nodeG.style.cursor = "pointer";

        // Node circle color based on status or category
        let fillColor = "#140306";
        let strokeColor = "#dc2626";
        let radius = 18;

        if (node.status === "true") {
            fillColor = "rgba(16, 185, 129, 0.25)";
            strokeColor = "#10b981";
        } else if (node.status === "false") {
            fillColor = "rgba(239, 68, 68, 0.3)";
            strokeColor = "#ef4444";
        } else if (node.status === "misleading") {
            fillColor = "rgba(245, 158, 11, 0.25)";
            strokeColor = "#f59e0b";
        } else if (node.category === "verdict") {
            radius = 24;
            strokeColor = "#ff1e42";
            fillColor = "rgba(220, 38, 38, 0.35)";
        } else if (node.category === "claim") {
            radius = 20;
            strokeColor = "#ff4d6d";
            fillColor = "rgba(255, 77, 109, 0.15)";
        }

        const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
        circle.setAttribute("r", radius);
        circle.setAttribute("fill", fillColor);
        circle.setAttribute("stroke", strokeColor);
        circle.setAttribute("stroke-width", "2.5");

        // Icon or initials inside circle
        const iconText = document.createElementNS("http://www.w3.org/2000/svg", "text");
        iconText.setAttribute("text-anchor", "middle");
        iconText.setAttribute("dy", "4");
        iconText.setAttribute("fill", "#ffffff");
        iconText.setAttribute("font-size", "10");
        iconText.setAttribute("font-weight", "bold");
        
        let iconChar = "•";
        if (node.category === "url") iconChar = "URL";
        else if (node.category === "platform") iconChar = "PLT";
        else if (node.category === "content") iconChar = "DOC";
        else if (node.category === "claim") iconChar = "CLM";
        else if (node.category === "source") iconChar = "SRC";
        else if (node.category === "verdict") iconChar = "VRD";
        iconText.textContent = iconChar;

        // Label below node
        const label = document.createElementNS("http://www.w3.org/2000/svg", "text");
        label.setAttribute("text-anchor", "middle");
        label.setAttribute("dy", radius + 14);
        label.setAttribute("fill", "#cbd5e1");
        label.setAttribute("font-size", "9.5");
        label.setAttribute("font-family", "inherit");
        
        // Truncate label for clean visual presentation
        const cleanLabel = (node.label || "").length > 20 ? (node.label || "").substring(0, 18) + "…" : node.label;
        label.textContent = cleanLabel;

        // Tooltip
        const title = document.createElementNS("http://www.w3.org/2000/svg", "title");
        title.textContent = `${node.label}\nCategory: ${node.category}\nStatus: ${node.status || 'N/A'}`;
        nodeG.appendChild(title);

        nodeG.appendChild(circle);
        nodeG.appendChild(iconText);
        nodeG.appendChild(label);
        nodesGroup.appendChild(nodeG);
    });
    g.appendChild(nodesGroup);

    container.appendChild(svg);
}
