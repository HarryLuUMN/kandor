import * as d3 from 'https://cdn.jsdelivr.net/npm/d3@7/+esm';

function colorForType(type) {
  const palette = {
    faction: '#ef4444',
    location: '#3b82f6',
    artifact: '#a855f7',
    character: '#10b981',
    event: '#f59e0b',
    custom: '#94a3b8',
  };
  return palette[type] || '#c084fc';
}

function buildGraph(data, time) {
  const entities = data.entities || [];
  const relations = (data.relations || []).filter((relation) => {
    if (time == null) return true;
    const start = relation.start_time ?? 0;
    const end = relation.end_time;
    if (time < start) return false;
    if (end == null) return true;
    return time <= end;
  });

  const nodeMap = new Map();
  for (const entity of entities) {
    nodeMap.set(entity.id, {
      id: entity.id,
      label: entity.name || entity.id,
      type: entity.type || 'custom',
    });
  }
  for (const relation of relations) {
    if (!nodeMap.has(relation.subject)) {
      nodeMap.set(relation.subject, { id: relation.subject, label: relation.subject, type: 'custom' });
    }
    if (!nodeMap.has(relation.object)) {
      nodeMap.set(relation.object, { id: relation.object, label: relation.object, type: 'custom' });
    }
  }

  const nodes = Array.from(nodeMap.values());
  const links = relations.map((relation, index) => ({
    id: `${relation.subject}-${relation.predicate}-${relation.object}-${index}`,
    source: relation.subject,
    target: relation.object,
    predicate: relation.predicate,
  }));
  return { nodes, links };
}

function render({ model, el }) {
  el.innerHTML = `
    <style>
      .kg-shell { font-family: Inter, system-ui, sans-serif; color: #e5e7eb; }
      .kg-shell .kg-controls { display: flex; gap: 12px; align-items: center; margin-bottom: 12px; flex-wrap: wrap; }
      .kg-shell.kg-panel { background: #0f172a; border: 1px solid rgba(255,255,255,0.08); border-radius: 16px; padding: 12px; }
      .kg-shell .kg-meta { color: #94a3b8; font-size: 13px; }
      .kg-shell svg { width: 100%; height: 520px; display: block; }
      .kg-shell .kg-tooltip { color: #cbd5e1; font-size: 13px; margin-top: 8px; min-height: 20px; }
      .kg-shell .kg-badge { padding: 4px 8px; border-radius: 999px; background: rgba(255,255,255,0.06); }
      .kg-shell input[type='range'] { width: 220px; }
    </style>
    <div class="kg-shell kg-panel">
      <div class="kg-controls">
        <span class="kg-badge">Temporal KG Viewer</span>
        <label>Time <input id="time-slider" type="range" min="0" max="0" step="1" value="0" /></label>
        <span id="time-value" class="kg-meta"></span>
        <span id="stats" class="kg-meta"></span>
      </div>
      <svg></svg>
      <div id="tooltip" class="kg-tooltip"></div>
    </div>
  `;

  const svg = d3.select(el).select('svg');
  const tooltip = el.querySelector('#tooltip');
  const slider = el.querySelector('#time-slider');
  const timeValue = el.querySelector('#time-value');
  const stats = el.querySelector('#stats');

  function draw() {
    const data = model.get('data') || {};
    const minTime = model.get('min_time') ?? 0;
    const maxTime = model.get('max_time') ?? 0;
    let currentTime = model.get('time');
    if (currentTime == null) currentTime = maxTime;

    slider.min = minTime;
    slider.max = maxTime;
    slider.value = currentTime;
    timeValue.textContent = `t = ${currentTime}`;

    const graph = buildGraph(data, currentTime);
    stats.textContent = `${graph.nodes.length} nodes · ${graph.links.length} relations`;

    svg.selectAll('*').remove();
    const width = el.clientWidth - 24;
    const height = 520;
    svg.attr('viewBox', [0, 0, width, height]);

    const simulation = d3.forceSimulation(graph.nodes)
      .force('link', d3.forceLink(graph.links).id((d) => d.id).distance(95))
      .force('charge', d3.forceManyBody().strength(-260))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius(26));

    const link = svg.append('g')
      .attr('stroke', '#64748b')
      .attr('stroke-opacity', 0.7)
      .selectAll('line')
      .data(graph.links)
      .join('line')
      .attr('stroke-width', 1.4);

    const edgeLabels = svg.append('g')
      .selectAll('text')
      .data(graph.links)
      .join('text')
      .attr('fill', '#94a3b8')
      .attr('font-size', 11)
      .attr('text-anchor', 'middle')
      .text((d) => d.predicate);

    const node = svg.append('g')
      .selectAll('g')
      .data(graph.nodes)
      .join('g')
      .call(d3.drag()
        .on('start', (event, d) => {
          if (!event.active) simulation.alphaTarget(0.3).restart();
          d.fx = d.x;
          d.fy = d.y;
        })
        .on('drag', (event, d) => {
          d.fx = event.x;
          d.fy = event.y;
        })
        .on('end', (event, d) => {
          if (!event.active) simulation.alphaTarget(0);
          d.fx = null;
          d.fy = null;
        }));

    node.append('circle')
      .attr('r', 14)
      .attr('fill', (d) => colorForType(d.type))
      .attr('stroke', '#f8fafc')
      .attr('stroke-width', 1.2)
      .on('mouseenter', (_, d) => {
        tooltip.textContent = `${d.label} · ${d.type}`;
      })
      .on('mouseleave', () => {
        tooltip.textContent = '';
      });

    node.append('text')
      .attr('text-anchor', 'middle')
      .attr('dy', 28)
      .attr('fill', '#e2e8f0')
      .attr('font-size', 11)
      .text((d) => d.label);

    simulation.on('tick', () => {
      link
        .attr('x1', (d) => d.source.x)
        .attr('y1', (d) => d.source.y)
        .attr('x2', (d) => d.target.x)
        .attr('y2', (d) => d.target.y);
      edgeLabels
        .attr('x', (d) => (d.source.x + d.target.x) / 2)
        .attr('y', (d) => (d.source.y + d.target.y) / 2 - 6);
      node.attr('transform', (d) => `translate(${d.x},${d.y})`);
    });
  }

  slider.addEventListener('input', async (event) => {
    model.set('time', Number(event.target.value));
    model.save_changes();
    draw();
  });

  model.on('change:data', draw);
  model.on('change:time', draw);
  draw();
}

export default { render };
