graph_snapshot is a tool to visualize graph algorithms based on `networkx <https://networkx.github.io/>`_, `pygraphviz <https://pygraphviz.github.io/>`_ and `dot2tex <https://dot2tex.readthedocs.io/en/latest/#>`_. 

Say you have a python script that runs Kruskal's algorithm on a networkx graph and you want to show how the algorithm works in your paper.

The only thing you have to do is to import graph_snapshot, create 'snapshots' of your graph at important moments during the algorithm and you'll get a directory of .tex files containing the tikz code for your graphs that are just waiting for you to include them into your Latex paper.

If you want to give a talk presenting your algorithm, graph_snapshot makes things even easier for you by providing the `beamer_slide` function that will create one beamer slide with the images of your algorithm as overlays, so that you just need to input this slide in order to be able to 'click through the algorithm' in your talk.