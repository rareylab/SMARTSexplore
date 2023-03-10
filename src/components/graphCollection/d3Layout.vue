<template>
<div>
    <!-- {{ graph_data.dic.nodes[0] }} -->
    <!-- {{ nodes }} -->
</div>
</template>

<script>
/* eslint max-len: */
// import * as d3 from 'd3';

export default {
  data: function() {
    return {
      graphData: {dic: {nodes: [{'id': 1}, {'id': 2}], edges: [{'id': 1, 'source': 1, 'target': 2}, {'id': 2, 'source': 0, 'target': 0}]}},
    };
  },
  computed: {
    get_nodes() {
      return graphData[0];
    },
  },
  methods: {
    async fetchData() {
      // get the data from flask
      const gResponse = await fetch('http://localhost:5000/smarts/data');
      const gObject = await gResponse.json();
      this.graph_data = gObject;

      const edgeObj = gObject.dic.edges;
      const nodeObj = gObject.dic.nodes;

      const links = [];
      const edges = edgeObj;
      const nodes2 = nodeObj;

      const len = edges.length;
      // var len = 50;
      // Convert the data.
      for (let i = 0; i < len; i++) {
        links.push({
          source: 'node ' + String(edges[i]['source']),
          target: 'node ' + String(edges[i]['target']),
          type: 'licensing'});
      }
      // alert(JSON.stringify(nodes[0]['id']))
      const len2 = nodes.length;
      const nodes = {};
      for (let i = 0; i < len2; i++) {
        nodes.push({
          id: 'node ' + String(nodes2[i]['id']),
        });
      }
      // Compute the distinct nodes from the links.
      links.forEach(function(link) {
        link.source = nodes[link.source] || (nodes[link.source] = {name: link.source});
        link.target = nodes[link.target] || (nodes[link.target] = {name: link.target});
      });

      const width = 3000;
      const height = 2000;

      // create the simulation
      const force = d3.layout.force()
          .nodes(d3.values(nodes))
          .links(links)
          .size([width, height])
          .linkDistance(100)
          .gravity(0.009) // 0.1
          .charge(-60) // -60
          .on('tick', tick)
          .start();

      // create the svg and objects
      const svg = d3.select('body').append('svg')
          .attr('width', width)
          .attr('height', height);

      const link = svg.selectAll('.link')
          .data(force.links())
          .enter().append('line')
          .attr('class', 'link');

      const node = svg.selectAll('.node')
          .data(force.nodes())
          .enter().append('g')
          .attr('class', 'node')
          .on('mouseover', mouseover)
          .on('mouseout', mouseout)
          .call(force.drag);

      node.append('circle')
          .attr('r', 8);

      node.append('text')
          .attr('x', 12)
          .attr('dy', '.35em')
          .text(function(d) {
            return d.name;
          });

      const counter = 0;
      /**
       * Tick function of the simulation.
       */
      function tick() {
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
            .attr('transform', function(d) {
              return 'translate(' + d.x + ',' + d.y + ')';
            });
        counter =counter +1;
        console.log(counter);
      }

      /**
       * Mouse over function.
       * @param {event} event
       */
      function mouseover(event) {
        d3.select(event.subject).select('circle').transition()
            .duration(750)
            .attr('r', 16);
      }

      /**
       * Mouse out function.
       * @param {event} event
       */
      function mouseout(event) {
        d3.select(event.subject).select('circle').transition()
            .duration(750)
            .attr('r', 8);
      }
    },
  },
  beforeMount() {
    this.fetchData();
  },
};
</script>

<style>
/* Graph objects */

/* .hidden {
    display: none !important;
}


.node.transparent-border {
    stroke: rgba(0,0,0,0.15);
}
.node:hover {
    opacity: 1;
}
.node:not(:hover):not(.highlighted).muted {
    opacity: 0.1;
}
.node.highlighted {
    fill: magenta;
}
.node.node-fixed {
    stroke: #ee1eeb;
}

.composite-line:not(:hover):not(.highlighted).muted .edge.real {
    opacity: 0.1;
}
.composite-line.highlighted .edge.real {
    stroke: magenta;
}
.composite-line.highlighted:not(.equal) .edge.real {
    marker-end: url('#arrowhead-highlight');
}
#arrowhead-highlight path {
    fill: magenta;
}

.edge.hoverhelper {
    opacity: 0;
}
.composite-line:hover .edge.hoverhelper {
    opacity: 0.5;
}

.display-block {
    display: block;
} */

.node {
    stroke-width: 3;
    stroke: black;
}

</style>
