<template>
  <ArrowheadMarkers></ArrowheadMarkers>
</template>
<script>
/* eslint max-len: */
/* eslint linebreak-style: ['error', 'windows'] */
import {Graph} from '../graphComponents/graph.js';
import ArrowheadMarkers from '../graphComponents/ArrowheadMarkers.vue';

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
  components: {
    ArrowheadMarkers,
  },
  props: {
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
  },
  mounted() {
    this.$watch(() => [this.graph, this.activeEdges, this.activeNodes], (newVal) => {
      if (this.simulation) {
        this.simulation.stop();
      }
      let tickCounter = 0;
      this.graph.setPositionsFromCCs(this.edgeActiveFn, this.nodeActiveFn);
      const nodes2 = this.activeNodes;
      const links2 = this.activeEdges;

      const lenEdges = links2.length;
      const lenNodes = nodes2.length;

      const nodes = [];
      const links = [];

      for (let i = 0; i < lenEdges; i++) {
        links.push({
          source: 'node ' + String(links2[i]['source']['id']),
          target: 'node ' + String(links2[i]['target']['id']),
          id: 'link ' + i,
          myid: i,
          objid: links2[i]['id'],
          color: this.edgeColorFn(links2[i]),
          highlighted: false,
          type: links2[i]['type'],
          objtype: 'edge',
        });
      }
      for (let j = 0; j < 1; j++) {
        for (let i = 0; i < lenNodes; i++) {
          nodes.push({
            id: 'node ' + String(nodes2[i]['id']),
            objid: nodes2[i]['id'],
            myid: i+j*lenNodes,
            x: nodes2[i]['x'],
            y: nodes2[i]['y'],
            color: this.nodeColorFn(nodes2[i]),
            highlighted: false,
            incidentEdges: nodes2[i]['incidentEdges'],
            objtype: 'node',
          });
        }
      }

      // const nodes = graphData.nodes; // this.nodes2; // graphData.nodes;
      // const links = graphData.links; // this.links2; // graphData.links;
      if (nodes.length > 0) {
        const s = d3.select('#app').select('.smartsexplore-app').select('#d3svg');
        if (s) {
          s.remove();
        };

        let transform = d3.zoomIdentity;
        transform.k = 0.15;
        transform.x = 800;
        transform.y = 500;
        let highlightId= 0;
        let highlightObj= null;
        const nodeColorFn = this.nodeColorFn;
        const edgeColorFn = this.edgeColorFn;
        const width = document.body.clientWidth;
        const height = document.body.clientHeight;
        const zoom = d3.zoom()
            .scaleExtent([0.01, 2])
            .on('zoom', zoomed);

        const simulation = d3.forceSimulation(nodes)
            .velocityDecay(0.75)
            .force('charge', d3.forceManyBody().strength((node) => {
              return -30 * Math.log(1 + node.incidentEdges.length);
            }))
            .force('link', d3.forceLink(links)
                .id((edge) => edge.id)
                .distance((edge) => edge.type === 'equal' ? 75 : 150)
                .strength(1.5) // 1
                .iterations(15))// 3
            // .force('center', d3.forceCenter(width / 2, height / 2).strength(0))
            .force('collision', d3.forceCollide()
                .radius(50)) // 22.5
            .on('tick', () => {
              link
                  .attr('x1', (d) => d.source.x)
                  .attr('y1', (d) => d.source.y)
                  .attr('x2', (d) => d.target.x)
                  .attr('y2', (d) => d.target.y)
                  .attr('stroke', (d) => {
                    const l = this.graph.getEdgeById(d.objid);
                    return highlightObj == 'link' && highlightId == d.objid ? 'magenta': edgeColorFn(l);
                  });

              node
                  .attr('cx', (d) => d.x)
                  .attr('cy', (d) => d.y)
                  .attr('fill', (d) => {
                    const n = this.graph.getNodeById(d.objid);
                    return highlightObj == 'node' && highlightId == d.objid ? 'magenta': nodeColorFn(n);
                  });
              tickCounter += 1;
            });
        simulation.alpha(0.05).alphaDecay(0.01).restart();

        const svg = d3.select('#app').select('.smartsexplore-app').append('svg')// #app
            .attr('id', 'd3svg')
            .attr('width', width)
            .attr('height', height)
            .call(zoom);

        svg.append('defs')
            .selectAll('marker')
            .data(edgeColorFn.colors)
            .enter().append('marker')
            .attr('id', (d) => 'arrowhead-' + d.substring(1))
            .attr('refX', 14)
            .attr('refY', 0)
            .attr('viewBox', '0 -5 10 10')
            .attr('markerUnits', 'userSpaceOnUse')
            .attr('markerWidth', 30)
            .attr('markerHeight', 50)
            .attr('xoverflow', 'visible')
            .attr('orient', 'auto')
            .append('path')
            .attr('d', 'M 0,-5 L 10,0 L 0,5 z')
            .attr('fill', (d) => d);

        const link = svg.append('g')
            .attr('stroke-opacity', 1)
            .selectAll('line')
            .data(links)
            .enter().append('line')
            .attr('id', (d) => d.objid)
            .attr('stroke-width', 10)
            .attr('marker-end', (d) =>{
              // console.log(d.type);
              if (d.type === 'equal') {
                return '';
              } else {
                const l = this.graph.getEdgeById(d.objid);
                const colorId = edgeColorFn(l).substring(1);
                // console.log(colorId);
                return `url(#arrowhead-${colorId})`;
              }
            })
            .on('mouseover', edgeHover)
            .on('click', edgeClick);

        const node = svg.append('g')
            .attr('stroke', 'black')
            .attr('stroke-width', 5)
            .selectAll('circle')
            .data(nodes)
            .enter().append('circle')
            // .attr('r', 15)
            .attr('r', 20)
            .attr('id', (d) => d.objid)
            .call(d3.drag()
                .on('start', dragstarted)
                .on('drag', dragged)
                .on('end', dragended))
            .on('mouseover', (e) => nodeHover(e, simulation))
            .on('click', nodeClick);

        /**
         * drag start
         * @param {*} event
         */
        function dragstarted(event) {
          // event.subject.fx = event.x;
          // event.subject.fy = event.y;
        }
        /**
         * dragging
         * @param {*} event
         */
        function dragged(event) {
          // d3.select(this).attr('cx', event.subject.x = event.x).attr('cy', event.subject.y = event.y);
          event.subject.fx = event.x;
          event.subject.fy = event.y;
        }
        /**
         * drag end
         * @param {*} event
         */
        function dragended(event) {
          event.subject.fx = null;
          event.subject.fy = null;
        }
        node.attr('transform', transform);
        link.attr('transform', transform);

        /**
         * zoom function
         * @param {*} event
         */
        function zoomed(event) {
          transform = event.transform;
          transform.x = parseInt(transform.x);
          transform.y = parseInt(transform.y);
          node.attr('transform', transform);
          link.attr('transform', transform);
          // simulation.alpha(0.01).alphaDecay(0.01).restart();
        }
        /**
         * hover
         * @param {*} event
         * @param {*} simulation
         */
        function nodeHover(event, simulation) {
          highlightId = event.target.id;
          highlightObj = 'node';
          simulation.alpha(0.05).alphaDecay(0.01).restart();
          // this.$emit('nodeHover', {event: event, node: this.graph.getNodeById(event.target.id)});
        };
        /**
         * hover
         * @param {*} event
         */
        function edgeHover(event) {
          highlightId = event.target.id;
          highlightObj = 'link';
          // this.$emit('edgeHover', {event: event, edge: this.graph.getEdgeById(event.target.id)});
        };
        /**
         * click
         * @param {*} event
         */
        function nodeClick(event) {
          // this.$emit('nodeClick', {event: event, node: this.graph.getNodeById(event.target.id)});
        };
        /**
         * click
         * @param {*} event
         */
        function edgeClick(event) {
          // this.$emit('edgeClick', {event: event, edge: this.graph.getEdgeById(event.target.id)});
        };

        // measure the time of 100 simulation ticks
        // const start = new Date;
        // simulation.stop();
        // simulation.tick(100);
        // console.log(new Date() - start );
        // console.log('start', this.tickCounter);

        // measure the number of frames per second
        simulation.alpha(1).alphaDecay(0.01).restart();
        tickCounter = 0;
        const start = new Date;
        setTimeout(() => {
          const time = new Date() - start;
          console.log('tick', tickCounter);
          console.log('time', time);
        }, 5000);
        // setTimeout(() => {
        //   const time = new Date() - start;
        //   console.log('time', time);
        //   simulation.stop();
        // }, 2000);
      };
    }, {immediate: true});
  },
  beforeUnmount() {
    if (this.svg) {
      this.svg.remove();
    }
  },
};
</script>

