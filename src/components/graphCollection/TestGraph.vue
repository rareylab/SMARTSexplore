<template>
    <div></div>
</template>

<script>
/* eslint max-len: */
import {Graph} from '../graphComponents/graph';
import * as reuse from 'd3-force-reuse';

export default {
  name: 'TestGraph',
  props: {
    graph: Graph,
  },
  methods: {
    createGraph() {
      console.log(this.graph);
      const edges = this.graph.edges;
      const nodes2 = this.graph.nodes;

      const nodes = [];
      const links = [];

      nodes2.forEach((node) => {
        nodes.push({
          id: 'node ' + String(node.id),
          x: node.id,
          y: node.id,
          vx: 0,
          vy: 0,
        });
      });

      edges.forEach((edge) => {
        links.push({
          source: 'node ' + edge.source.id,
          target: 'node ' + edge.target.id,
          id: edge.id,
          type: 'licensing',
        });
      });

      const width = 1280*2;
      const height = 640*2;

      const simulation = d3.forceSimulation(nodes)
          .force('link', d3.forceLink().strength(2).id(function(d) {
            return d.id;
          }))
          .force('charge', reuse.forceManyBodyReuse().strength(-3))
          .force('center', d3.forceCenter(width / 2, height / 2).strength(0.03))
          .force('collide', d3.forceCollide(3))
          .on('tick', ticked);

      const svg = d3.select('body').append('svg')
          .attr('width', width)
          .attr('height', height);

      const link = svg.append('g')
          .attr('class', 'links')
          .selectAll('line')
          .data(links)
          .enter().append('line')
          .attr('stroke-width', 2)
          .attr('stroke', 'black');

      const node = svg.append('g')
          .attr('class', 'nodes')
          .selectAll('circle')
          .data(nodes)
          .enter().append('circle')
          .attr('r', 5)
          .attr('fill', function(d) {
            return 'green';
          })
          .call(d3.drag()
              .on('start', dragstarted)
              .on('drag', dragged)
              .on('end', dragended));

      node.append('title')
          .text(function(d) {
            return d.id;
          });

      simulation.force('link')
          .links(links);

      /**
       * Tick function of the simulation
       */
      function ticked() {
        link
            .attr('x1', function(d) {
              return d.source.x;
            })
            .attr('y1', function(d) {
              return d.source.y;
            })
            .attr('x2', function(d) {
              return d.target.x;
            })
            .attr('y2', function(d) {
              return d.target.y;
            });

        node
            .attr('cx', function(d) {
              return d.x;
            })
            .attr('cy', function(d) {
              return d.y;
            });
      }

      /**
       * When drag starts.
       * @param {*} d
       */
      function dragstarted(d) {
        if (!d3.event.active) simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
      }

      /**
       * When dragged.
       * @param {*} d
       */
      function dragged(d) {
        d.fx = d3.event.x;
        d.fy = d3.event.y;
      }

      /**
       * When drag ends.
       * @param {*} d
       */
      function dragended(d) {
        if (!d3.event.active) simulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
      }
    },
  },
  beforeMount() {
    this.createGraph();
  },
};
</script>
