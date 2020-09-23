import networkx as nx
from networkx.drawing.nx_agraph import write_dot
import pygraphviz
import dot2tex
import copy
import os

default_graph_list = []

def snapshot(G,graph_list=default_graph_list):
    """
    takes a given graph G and appends it to graph_list.
    If no graph_list is given, it is appended to a global list
    """
    H = copy.deepcopy(G)
    graph_list.append(H)

def setNodesToCircleShape(G):
    for node in G.nodes():
        G.nodes[node]['shape'] = "ellipse"

def setLenAsLabel(G):
    for edge in G.edges():
        try:
            G.edges[edge]['label'] = G.edges[edge]['len']
        except:
            raise Exception("no len given")

def compile(dir, graph_list=default_graph_list, tikzedgelabels = True, lenAsLabel=True, scale_total = 1, scale_edge_lengths = 1, texmode = "math", **kwargs):
    """
    creates a new directory if dir doesn't exist
    takes graphs in graph_list and writes their dot code and tikz code to files in dir
    if graph_list isn't explicitly set, it takes default_graph_list
    label_with_weight: add edge weight as label
    --------------------------------------------------------------------------
    options:
    see https://dot2tex.readthedocs.io/en/latest/usage_guide.html

    edge attributes:
        - 'len': length of edge
        - 'label': tikz edge label
        - 'weight': specifies how much the edge is weighted in the optimization process
    """
    parentpath = os.getcwd()
    try:
        os.chdir(dir)
    except:
        os.mkdir(dir)
        os.chdir(dir)
    os.system("rm -f graph*.tex")
    os.system("rm -f graph*.dot")
    for index, graph in enumerate(graph_list):
        filename = 'graph' + str(index) + '.dot'
        filenametikz = 'graph' + str(index) + '.tex' 
        
        if lenAsLabel:
            setLenAsLabel(graph)
        #factor 0.5 turned out to look nice on beamer presentations
        for edge in graph.edges:
            graph.edges[edge]['len'] = 0.5 * scale_edge_lengths * graph.edges[edge]['len']
        setNodesToCircleShape(graph)
        write_dot(graph, filename)
        with open(filename, "r") as f:
            lines = f.readlines()
            graphoptions = "      graph   ["
            for arg in kwargs:
                if arg in ["overlap", "splines", "sep", "orientation"]:
                    graphoptions += arg + "=" + kwargs[arg] + ", "
                else:
                    raise  Exception(f"Unknown keywordargument {arg}.")
            graphoptions = graphoptions[:-2]
            graphoptions += "];\n"
            lines.insert(1, graphoptions)
        with open (filename, "w") as f:
            f.writelines(lines)
        with open(filename, "r") as f:
            dotgraph = f.read()
        with open(filenametikz, "w") as f:
            if texmode not in ["math", "verbatim", "raw"]:
                raise Exception(f"texmode was set to {texmode}, but can only be set to 'math', 'verbatim' or 'raw'.")
            options = {'format':"tikz", 'texmode':texmode, 'output':filenametikz, 'graphstyle':"scale=" + str(scale_total) + ", auto, every node/.style={transform shape}", 'tikzedgelabels':tikzedgelabels, 'prog':"neato", 'figonly':True, 'force':True}
            f.write(dot2tex.dot2tex(dotgraph, **options))
        
    os.chdir(parentpath)

def beamer_slide(directory, title=None, path=None, caption_list=[]):
    caption_iterator = iter(caption_list)
    content = os.listdir(directory)
    texfiles = []
    index = 0
    next_helper = True
    while next_helper:
        nextfile = f"graph{index}.tex"
        if nextfile in content:
            texfiles.append(nextfile)
            index += 1
        else:
            next_helper = False
    slidelines = [r"\begin{frame}"]
    if title:
        slidelines.append(r"\frametitle{" + title + r"}")
    for i, texfile in enumerate(texfiles):
        filerawname = texfile.split(".")[0]
        filenamewithdir = os.path.join(directory, filerawname)
        try:
            current_caption = next(caption_iterator)
            line = r"\only<" + str(i+1) + r">{\begin{figure} \input{" + filenamewithdir + r".tex} \caption{" + current_caption + r"} \end{figure}}"
        except: 
            line = r"\only<" + str(i+1) + r">{\begin{figure} \input{" + filenamewithdir + r".tex} \end{figure}}"
        slidelines.append(line)
    slidelines.append(r"\end{frame}")
    slidecode = ""
    for line in slidelines:
        slidecode += line + "\n"
    if path:
        with open(path, "w") as f:
            f.write(slidecode)
    return slidecode

def latex_document(directory, title=None, path=None, caption_list=[]):
    caption_iterator = iter(caption_list)
    content = os.listdir(directory)
    texfiles = []
    index = 0
    next_helper = True
    while next_helper:
        nextfile = f"graph{index}.tex"
        if nextfile in content:
            texfiles.append(nextfile)
            index += 1
        else:
            next_helper = False
    latex_doc_lines = [r"\documentclass{article}", r"\usepackage{tikz}", r"\usetikzlibrary{decorations,arrows,shapes}", r"\usepackage{amsmath}", r"\usepackage{float}","\n", r"\begin{document}", "\n"]
    if title:
        latex_doc_lines.append(r"\section{" + title + r"}")
    for i, texfile in enumerate(texfiles):
        filerawname = texfile.split(".")[0]
        filenamewithdir = os.path.join(directory, filerawname)
        try:
            current_caption = next(caption_iterator)
            line = r"\begin{figure}[H] \input{" + filenamewithdir + r".tex} \caption{" + current_caption + r"} \end{figure}"
        except: 
            line = r"\begin{figure}[H] \input{" + filenamewithdir + r".tex} \end{figure}"
        latex_doc_lines.append(line)
    latex_doc_lines.append("\n")
    latex_doc_lines.append(r"\end{document}")
    latex_doc_code = ""
    for line in latex_doc_lines:
        latex_doc_code += line + "\n"
    if path:
        with open(path, "w") as f:
            f.write(latex_doc_code)
    return latex_doc_code
