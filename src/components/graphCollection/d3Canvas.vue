<template>
  <div v-if="a"></div>
</template>
<script>
/* eslint max-len: */
import {Graph} from '../graphComponents/graph.js';

import * as d3ScaleChromatic from 'd3-scale-chromatic';
import * as d3Interpolate from 'd3-interpolate';
import * as d3Scale from 'd3-scale';

import * as d3Or from 'd3';
import * as d3Reuse from 'd3-force-reuse';
import * as d3Sampled from 'd3-force-sampled';

const d3 = Object.assign({}, d3Or, d3Reuse, d3ScaleChromatic, d3Interpolate, d3Scale, d3Sampled);

const perObjectFn = {
  type: Function,
  validator: (fn) => fn.length == 1,
};

export default {
  props: {
    modus: {String},
    depth: {Number},
    displayMatches: {Boolean},
    steps: {Number},
    /** The Graph instance to render */
    graph: {type: Graph, required: true},
    /**
     * A function that returns a (CSS class) -> (boolean) mapping given a node.
     * Only if the boolean is true, the class will be added to the node.
     * No classes by default.
     */
    nodeClassFn: {...perObjectFn, default: (node) => {}},
    /** A function that returns a color given a node (white by default). */
    nodeColorFn: {...perObjectFn, default: (node) => 'white'},
    /**
     * A function that returns a (key)->(value) CSS style mapping given a node.
     * No styles by default
     */
    nodeStyleFn: {...perObjectFn, default: (node) => {}},
    /**
     * A function that determines if a node is active
     * (shown, included in the layout and force simulation, visited during DFS)
     */
    nodeActiveFn: {...perObjectFn, default: (node) => true},

    /**
     * A function that returns a (CSS class) -> (boolean) mapping given an edge.
     * Only if the boolean is true, the class will be added to the edge.
     * No classes by default.
     */
    edgeClassFn: {...perObjectFn, default: (node) => {}},
    /** A function that returns a color given a node (black by default). */
    edgeColorFn: {
      ...perObjectFn,
      default: (edge) => 'black',
      validator: (fn) => fn.length == 1 && fn.colors instanceof Array,
    },
    /**
     * A function that returns a (key)->(value) CSS style mapping given an edge.
     * No styles by default
     */
    edgeStyleFn: {...perObjectFn, default: (edge) => {}},
    /**
     * A function that determines if an edge is active
     * (shown, included in the layout and force simulation, traversed during DFS)
     */
    edgeActiveFn: {...perObjectFn, default: (edge) => true},
  },
  computed: {
    /**
     * The currently active edges (determined by the edgeActiveFn prop)
     * @return {edges}
     */
    activeEdges() {
      return _.filter(this.graph.edges, this.edgeActiveFn);
    },
    /**
     * The currently active nodes (determined by the nodeActiveFn prop)
     * @return {nodes}
     */
    activeNodes() {
      return _.filter(this.graph.nodes, this.nodeActiveFn);
    },
    /**
     * Merges external nodeClassFn behavior with component-internal behavior
     *  @return {class}
     */
    nodeClassFn_() {
      return (node) => {
        return {...this.nodeClassFn(node), 'node-fixed': node.__dragFixed};
      };
    },
  },
  data() {
    return {
      tick: false,
      zoomCounter: 0,
      a: false,
      transform: d3.zoomIdentity,
      width: document.body.clientWidth,
      height: document.body.clientHeight,
      radius: 20,
      currentNode: {highlighted: false},
      previousNode: {highlighted: false},
      currentEdge: {highlighted: false},
      previousEdge: {highlighted: false},
      tickCounter: 0,
      lastClick: new Date,
    };
  },
  methods: {
    /**
     * Create the Canvas to draw on.
     */
    createCanvas() {
      console.log('create canvas');
      const width = document.body.clientWidth;
      const height = document.body.clientHeight;
      d3.select('#app').select('.smartsexplore-app').append('canvas')
          .attr('id', 'd3canvas')
          .classed('mainCanvas', true)
          .attr('width', width)
          .attr('height', height);
      this.c = document.getElementById('d3canvas');
      this.ctx = this.c.getContext('2d');
    },
    /**
     * Convert the data in a suitable form
     * @return {gaphData}
     */
    updateGraphData() {
      console.log('init Graph');
      this.graph.setPositionsFromCCs(this.edgeActiveFn, this.nodectiveFn);
      const nodes2 = this.activeNodes;
      const links2 = this.activeEdges;

      const lenLinks = links2.length;
      const lenNodes = nodes2.length;

      const nodes = [];
      const links = [];

      for (let i = 0; i < lenLinks; i++) {
        links.push({
          source: 'node ' + String(links2[i]['source']['id']),
          target: 'node ' + String(links2[i]['target']['id']),
          sourceId: links2[i]['source']['id'],
          targetId: links2[i]['target']['id'],
          id: 'link ' + i,
          myid: i,
          objid: links2[i]['id'],
          color: this.edgeColorFn(links2[i]),
          type: links2[i]['type'],
          objtype: 'edge',
          muted: false,
          spsim: links2[i]['spsim'],
        });
        links2[i]['toLink'] = i;
      }
      for (let i = 0; i < lenNodes; i++) {
        nodes.push({
          id: 'node ' + String(nodes2[i]['id']),
          objid: nodes2[i]['id'],
          myid: i,
          x: nodes2[i]['x'],
          y: nodes2[i]['y'],
          color: this.nodeColorFn(nodes2[i]),
          incidentEdges: nodes2[i]['incidentEdges'],
          type: nodes2[i]['type'],
          objtype: 'node',
          muted: nodes2[i]['meta']['muted'],
          // meta: nodes2[i]['meta'],
        });
      }

      this.nodes = nodes;
      this.links = links;
      this.nodes2 = nodes2;
      this.links2 = links2;
      return {nodes, links};
    },
    /**
     * Bind the Graph data to a custom element.
     * @param {nodes} nodes
     * @param {links} links
     * @return {customData}
     */
    dataBind(nodes, links) {
      // eslint-disable-next-line require-jsdoc
      // const nodeColorFn = this.nodeColorFn();
      console.log('bind data');

      const detachedContainer = document.createElement('custom');
      const dataContainer = d3.select(detachedContainer);
      const nodeBinding = dataContainer.selectAll('custom.arc')
          .data(nodes, function(d) {
            return d;
          });

      const linkBinding = dataContainer.selectAll('custom.line')
          .data(links, function(d) {
            return d;
          });

      nodeBinding.enter()
          .append('custom')
          .classed('arc', true);

      linkBinding.enter()
          .append('custom')
          .classed('line', true);

      this.customNodes = dataContainer.selectAll('custom.arc');
      this.customLinks = dataContainer.selectAll('custom.line');
      const customNodes = dataContainer.selectAll('custom.arc');
      const customLinks = dataContainer.selectAll('custom.line');
      return {customNodes, customLinks};
    },
    /**
     * Draw this custom link-elements
     * @param {*} customLinks
     * @param {*} ctx
     */
    draw_links(customLinks, ctx) {
      const radius = this.radius;
      const nodes = this.nodes;
      const no = [];

      for (let i = 0; i < nodes.length; i++) {
        const node = nodes[i];
        const id = node.objid;
        no[id] = node;
      }
      ctx.lineWidth = 1;

      customLinks.each(function(d) {
        const scale = d3.scaleLinear();
        const sourceNode = no[d.sourceId];
        const targetNode = no[d.targetId];

        ctx.strokeStyle = d.highlighted ? 'magenta': d.color;
        ctx.fillStyle = d.highlighted ? 'magenta': d.color;
        const lineWidth = d.highlighted ? 10: Math.min(Math.max(2.5, 8 * scale(d.spsim)**2), 10);
        if (sourceNode) {
          ctx.globalAlpha = sourceNode.muted || targetNode.muted ? 0.1: 1;
          ctx.globalAlpha = d.highlighted ? 1: ctx.globalAlpha;
        }

        const tox = d.target.x;
        const toy = d.target.y;
        const fromx = d.source.x;
        const fromy = d.source.y;

        const width = lineWidth - (ctx.lineWidth -1);
        const lineLength = Math.sqrt((fromx-tox)**2+(fromy-toy)**2);
        const endLineFactor = (lineLength - 35) / lineLength;
        const endLinex = fromx + (tox-fromx)* endLineFactor;
        const endLiney = fromy + (toy-fromy)* endLineFactor;
        const prex = -1;
        const prey = 1;

        const v1y = tox - fromx;
        const v1x = toy - fromy;

        ctx.beginPath();

        const multi = width / 2 / Math.sqrt(v1x**2 + v1y**2);
        const startx = fromx + prex*multi*v1x;
        const starty = fromy + prey*multi*v1y;
        const endx = endLinex + prex*multi*v1x;
        const endy = endLiney + prey*multi*v1y;

        const mul = 0 / Math.sqrt(v1x**2 + v1y**2);
        const mul2 = width / Math.sqrt(v1x**2 + v1y**2);
        ctx.moveTo(startx - prex*mul*v1x, starty - prey*mul*v1y);
        ctx.lineTo(endx - prex*mul*v1x, endy - prey*mul*v1y);
        ctx.lineTo(endx - prex*mul2*v1x, endy - prey*mul2*v1y);
        ctx.lineTo(startx - prex*mul2*v1x, starty - prey*mul2*v1y);
        ctx.lineTo(startx - prex*mul*v1x, starty - prey*mul*v1y);
        ctx.fill();
        ctx.closePath();

        if (d.type=='subset') {
          const headlen = 25;
          const angle = Math.atan2(toy-fromy, tox-fromx);
          const tipx = tox - Math.cos(angle) * radius*(1.0);
          const tipy = toy - Math.sin(angle) * radius*(1.0);

          ctx.beginPath();
          const leftCornerx = tipx-(headlen)*Math.cos(angle-Math.PI/7);
          const leftCornery = tipy-(headlen)*Math.sin(angle-Math.PI/7);

          const rightCornerx = tipx-(headlen)*Math.cos(angle+Math.PI/7);
          const rightCornery = tipy-(headlen)*Math.sin(angle+Math.PI/7);
          ctx.moveTo(tipx, tipy);
          ctx.lineTo(leftCornerx, leftCornery);
          ctx.lineTo(rightCornerx, rightCornery);
          ctx.lineTo(tipx, tipy);
          ctx.fill();
          ctx.closePath();
        } else {
          ctx.beginPath();
          const startx = fromx + (tox-fromx)*(lineLength - 36) / lineLength + prex*multi*v1x;
          const starty = fromy + (toy-fromy)*(lineLength - 36) / lineLength + prey*multi*v1y;
          const endx = tox + prex*multi*v1x;
          const endy = toy + prey*multi*v1y;
          ctx.moveTo(startx - prex*mul*v1x, starty - prey*mul*v1y);
          ctx.lineTo(endx - prex*mul*v1x, endy - prey*mul*v1y);
          ctx.lineTo(endx - prex*mul2*v1x, endy - prey*mul2*v1y);
          ctx.lineTo(startx - prex*mul2*v1x, starty - prey*mul2*v1y);
          ctx.lineTo(startx - prex*mul*v1x, starty - prey*mul*v1y);
          ctx.fill();
          ctx.closePath();
        }
      });
    },
    /**
     * Draw the custom node-elements
     * @param {*} customNodes
     * @param {*} ctx
     */
    draw_nodes(customNodes, ctx) {
      const radius = this.radius;

      customNodes.each(function(d) {
        ctx.strokeStyle = d.active ? 'magenta': 'black';
        ctx.lineWidth = 6;
        ctx.fillStyle = d.highlighted ? 'magenta': d.color;
        ctx.globalAlpha = d.muted ? 0.1: 1;
        ctx.globalAlpha = d.highlighted ? 1: ctx.globalAlpha;

        ctx.beginPath();
        ctx.moveTo(d.x, d.y);
        ctx.arc(d.x, d.y, radius, 0, 2 * Math.PI);
        ctx.stroke();
        ctx.fill();
        // ctx.closePath();
      });
    },
    /**
     * The function is called whenever a simulationtick happens.
     * Update the object positions.
     */
    ticked() {
      this.tick = true;
      const width = document.body.clientWidth;
      const height = document.body.clientHeight;

      this.ctx.clearRect(0, 0, width, height);
      this.ctx.save();

      this.ctx.translate(this.transform.x, this.transform.y);
      this.ctx.scale(this.transform.k, this.transform.k);
      this.draw_links(this.customLinks, this.ctx);
      this.draw_nodes(this.customNodes, this.ctx);
      this.ctx.restore();

      this.tickCounter = this.tickCounter+1;
      this.tick = false;
    },
    /**
     * Initialize the simulation and start it.
     * @param {*} nodes
     * @param {*} links
     */
    initSimulation(nodes, links) {
      console.log('init simulation');
      if (this.simulation) {
        this.simulation.stop();
      }
      this.simulation = d3.forceSimulation(nodes)
          .force('charge', d3.forceManyBody()
              .strength((node) => {
                return -30 * Math.log(1 + node.incidentEdges.length);
              }))
          .force('link', d3.forceLink(links)
              .id((edge) => edge.id)
              .distance((edge) => edge.type === 'equal' ? 75 : 150)
              .strength(1)
              .iterations(3))
          .force('collision', d3.forceCollide()
              .radius(22.5))
          .on('tick', this.ticked);
    },
    /**
     * Update the transform
     * @param {*} event
     */
    zoom(event) {
      this.transform = event.transform;
      this.simulation.alphaDecay(0.1).restart();
    },
    /**
     * Bind the zoom function to the canvas.
     */
    initZoom() {
      console.log('init zoom');
      d3.select(this.ctx.canvas)
          .call(d3.zoom()
              .scaleExtent([0.1, 2])
              .on('zoom', this.zoom))
          .on('dblclick.zoom', null);
    },
    /**
     * Unbind the last dragged node.
     * @param {*} event
     */
    dragstarted(event) {
      event.subject.x = this.transform.invertX(event.x);
      event.subject.y = this.transform.invertY(event.y);
      event.subject.active = true;

      const id = event.subject.objid;

      const simNode = this.graph.getNodeById(id);

      const ccNodes = [];
      const ccEdges = [];

      const no = [];
      for (let i = 0; i < this.nodes.length; i++) {
        const node = this.nodes[i];
        const id = node.objid;
        no[id] = node;
      }

      const li = [];
      for (let i = 0; i < this.links.length; i++) {
        const link = this.links[i];
        const id = link.objid;
        li[id] = link;
      }

      this.graph.runDFS(
          simNode, 'all', Infinity,
          (node) => {
            const n = no[node.id];
            if (n) {
              ccNodes.push(n);
            }
          },
          (edge) => {
            const l = li[edge.id];
            if (l) {
              ccEdges.push(l);
            }
          },
          null,
          this.edgeActiveFn, null);

      this._prevSimNodes = this.simulation.nodes();
      this.simulation.nodes(ccNodes);
      this._prevSimEdges = this.simulation.force('link').links();
      this.simulation.force('link').links(ccEdges);
    },
    /**
     * Update the parameters while dragged.
     * @param {*} event
     */
    dragged(event) {
      event.subject.fx = this.transform.invertX(event.x);
      event.subject.fy = this.transform.invertY(event.y);
      this.simulation.alpha(0.075).alphaDecay(0.01).restart();
      // this.ticked();
    },
    /**
     * Fixate the position of the dragged object.
     * @param {*} event
     */
    dragended(event) {
      const currentClick = new Date;
      if (currentClick - this.lastClick < 500) {
        event.subject.fx = null;
        event.subject.fy = null;
        event.subject.active = false;
      } else {
        event.subject.fx = event.subject.x;
        event.subject.fy = event.subject.y;
      }
      if (this._prevSimNodes) {
        this.simulation.nodes(this._prevSimNodes);
        delete this._prevSimNodes;
      }
      if (this._prevSimEdges) {
        this.simulation.force('link').links(this._prevSimEdges);
        delete this._prevSimEdges;
      }
      this.simulation.alpha(0.075).alphaDecay(0.01).restart();
      this.lastClick = currentClick;
    },
    /**
     * Calculate the nearest Node.
     * @param {*} event
     * @return {subject}
     */
    dragsubject(event) {
      let subject = null;

      const x = this.transform.invertX(event.x);
      const y = this.transform.invertY(event.y);
      subject = this.simulation.find(x, y, this.radius+5);
      if (subject) {
        subject.x = this.transform.applyX(subject.x);
        subject.y = this.transform.applyY(subject.y);
      }
      return subject;
    },
    /**
     * Bind the drag function to the canvas.
     */
    initDrag() {
      // let transform = this.transform;
      // let simulation = this.simulation;
      d3.select(this.ctx.canvas)
          .call(d3.drag()
              .subject(this.dragsubject)
              .on('start', this.dragstarted)
              .on('drag', this.dragged)
              .on('end', this.dragended),
          );
    },
    /**
     * Calculate the nearest Object and emit it,
     * when the distance is under a threshold.
     * @param {*} event
     */
    mouseMove(event) {
      const x = this.transform.invertX(event.x);
      const y = this.transform.invertY(event.y);

      const node = this.simulation.find(x, y, this.radius);
      if (node) {
        this.previousNode = this.currentNode;
        this.currentNode = node;
        this.currentEdge.highlighted = false;
        this.previousNode.highlighted = false;

        this.currentNode.highlighted = true;
        if (!this.tick) {
          this.simulation.alphaDecay(0.1).restart();
        }
        this.$emit('nodeHover', {event: event, node: this.nodes2[node.myid]});
        if (event.altKey || event.shiftKey) {
          const maxDepth = this.depth;
          let dir = 'all';
          if (event.shiftKey && !event.altKey) dir = 'outgoing';
          else if (event.altKey && !event.shiftKey) dir = 'incoming';
          const dfsnode = this.graph.getNodeById(node.objid);
          // Mute all nodes, unmute only reached nodes
          _.each(this.nodes, (node) => {
            node.muted = true;
          });

          const no = [];
          for (let i = 0; i < this.nodes.length; i++) {
            const node = this.nodes[i];
            const id = node.objid;
            no[id] = node;
          }

          this.graph.runDFS(
              dfsnode, dir, maxDepth,
              (node) => {
                const nodeID = node.id;
                node.meta.muted = false;
                no[nodeID].muted = false;
              },
              null, null, this.edgeActiveFn, null,
          );
        }
      } else {
        const edge = this.findEdge(x, y, this.radius);
        if (edge) {
          this.previousEdge = this.currentEdge;
          this.currentEdge = edge;
          this.currentNode.highlighted = false;
          this.previousEdge.highlighted = false;
          this.currentEdge.highlighted = true;

          if (!this.tick) {
            this.simulation.alphaDecay(0.1).restart();
          }
          this.$emit('edgeHover', {event: event, edge: this.links2[edge.myid]});
        }
      }
    },
    /**
     * Bind the mousemove function to the canvas.
     */
    initMouseover() {
      d3.select(this.ctx.canvas)
          .on('mousemove', this.mouseMove);
    },
    /**
     * Calculate the nearest Edge and return it,
     * when the distance is under a threshold.
     * @param {*} x
     * @param {*} y
     * @param {*} radius
     * @return {edge}
     */
    findEdge(x, y, radius) {
      if (radius==null) radius = Infinity;
      else radius *= radius;
      const n = this.links.length;
      let closest = null;
      const setOfDistances = [];
      for (let i = 0; i < n; ++i) {
        const edge = this.links[i];
        const startX = edge.source.x;
        const startY = edge.source.y;
        const endX = edge.target.x;
        const endY = edge.target.y;
        const distances = [];
        const steps = 7;
        for (let j = 0; j < steps; ++j) { // 4
          const center1X = startX + j*1/steps*(endX - startX); // 0.25
          const center1Y = startY + j*1/steps*(endY - startY);
          const dx1 = x - center1X;
          const dy1 = y - center1Y;
          const d1 = dx1 * dx1 + dy1 * dy1;
          distances.push(d1);
        }
        const distance = Math.min(...distances);
        setOfDistances.push(distance);
      }
      for (let k = 0; k < setOfDistances.length; ++k) {
        const dist = setOfDistances[k];
        if (dist < radius) {
          closest = this.links[k], radius = dist;
        }
      }
      return closest;
    },
    /**
     * Calculate the nearest Object and emit it,
     * when the distance is under a threshold.
     * @param {*} event
     */
    mouseClick(event) {
      const x = this.transform.invertX(event.x);
      const y = this.transform.invertY(event.y);
      const node = this.simulation.find(x, y, this.radius*2);

      if (node) {
        this.previousNode = this.currentNode;
        this.currentNode = node;
        this.currentEdge.highlighted = false;
        this.previousNode.highlighted = false;

        this.currentNode.highlighted = true;
        this.$emit('nodeClick', {event: event, node: this.nodes2[node.myid]});
      } else {
        const edge = this.findEdge(x, y, this.radius*2);
        if (edge) {
          this.previousEdge = this.currentEdge;
          this.currentEdge = edge;
          this.currentNode.highlighted = false;
          this.previousEdge.highlighted = false;

          this.currentEdge.highlighted = true;
          this.$emit('edgeClick', {event: event, edge: this.links2[edge.myid]});
        } else {
          if (event.altKey || event.shiftKey) {
            _.each(this.nodes, (node) => {
              node.muted = false;
            });
            this.$emit('backgroundClick', event);
          }
        }
      }
      this.ticked();
    },
    /**
     * Bind the mouseclick function to the canvas.
     */
    initMouseclick() {
      console.log('init mouseclick');
      d3.select(this.ctx.canvas)
          .on('click', this.mouseClick);
    },
  },
  mounted() {
    this.createCanvas();
    this.count = 0;
    this.$watch(() => [this.graph, this.activeEdges], (newVal) => {
      if (this.simulation) {
        this.simulation.stop();
      }
      const graphData = this.updateGraphData();
      const nodes = graphData.nodes;
      const links = graphData.links;
      if (nodes.length >= 0) {
        this.transform.k = 0.15;
        this.transform.x = 800;
        this.transform.y = 500;
        this.dataBind(nodes, links);
        this.initSimulation(nodes, links);
        this.initMouseclick();
        this.initMouseover();
        this.initDrag();
        this.initZoom();

        this.tickCounter = 0;
        const start = new Date;
        this.simulation.alpha(2).alphaDecay(0.1).restart();
        // this.simulation.stop();
        // this.simulation.alpha(2).alphaDecay(0.15).restart();

        // measure the time of 100 simulation ticks
        // const n = 12;
        // this.simulation.tick(n);
        // console.log('time for', n, 'ticks: ', new Date() - start );

        // measure the number of frames per second
        setTimeout(() => {
          const time = new Date() - start;
          console.log('tick', this.tickCounter);
          console.log('time_counter', time);
        }, 1000);
        setTimeout(() => {
          const time = new Date() - start;
          console.log('time_stop', time);
          // this.simulation.stop();
        }, 3000);
      };
    }, {immediate: true});

    this.$watch(() => [this.displayMatches], (newVal) => {
      if (this.displayMatches) {
        for (let i = 0; i < this.nodes.length; i++) {
          this.nodes[i].meta = this.graph.getNodeById(this.nodes[i].objid).meta;
          this.nodes[i].muted = this.graph.getNodeById(this.nodes[i].objid).meta.matches.length == 0;
          this.nodes[i].color = this.nodeColorFn(this.nodes[i]);
        }
      } else {
        _.each(this.nodes, (node) => {
          node.color = this.nodeColorFn(this.graph.getNodeById(node.objid));
          node.muted = false;
        });
      }
      this.ticked();
    });

    this.$watch(() => [this.steps], (newVal) => {
      for (let i = 0; i < this.links.length; i++) {
        this.links[i].color = this.edgeColorFn(this.graph.getEdgeById(this.links[i].objid));
      }
      this.ticked();
    });
  },
  beforeUnmount() {
    if (this.c) {
      this.c.remove();
    }
  },
};
</script>

