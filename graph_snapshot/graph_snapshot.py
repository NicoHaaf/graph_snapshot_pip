"""
graph_snapshot
==================
"""
import networkx as nx
from networkx.drawing.nx_agraph import write_dot
import pygraphviz
import dot2tex
import copy
import os

default_graph_list = []

def snapshot(G,graph_list=default_graph_list):
    """
    Takes a given graph G and appends it to graph_list.
    If no graph_list is given, it is appended to a global list.

    Parameters
    -----------
    G
        The graph to be appended to graph_list.

    graph_list
        The list where graphs are saved.

    """
    H = copy.deepcopy(G)
    graph_list.append(H)

def setNodesToCircleShape(G):
    """
    set node shape to circle

    Parameters
    -----------
    G
        the graph whose nodes we talk about

    """
    for node in G.nodes():
        G.nodes[node]['shape'] = "circle"

def setLenAsLabel(G):
    """
    set len attribute of edges as label

    Parameters
    -----------
    G
        the graph whose nodes we talk about

    """
    for edge in G.edges():
        try:
            G.edges[edge]['label'] = G.edges[edge]['len']
        except:
            raise Exception("no len given")

def compile(dir, graph_list=default_graph_list, tikzedgelabels = True, lenAsLabel = False, scale_total = 1, scale_edge_lengths = 1, texmode = "math", **kwargs):
    """
    Creates graph<i>.dot files containing the dot code for the graph in the snapshot with index <i> and graph<i>.tex files containing the tikz code for the graph in the snapshot with index <i>. The .dot files are only there because the dot code is created anyway and it can be useful for debugging to see the dot code.

    Parameters
    -----------
    dir
        Directory where all output files are placed. If it doesn't exist, it is created.
        If it already exists, all further graph<i>.dot or graph<i>.tex files in it are deleted.

    graph_list
        The list of snapshots to be processed and converted into tikz code. Default is to use `default_graph_list` which is also default for the snapshot function. If in snapshot a `graph_list` is specified, this list must be specified in compile aswell. For detailed instruction how to use this, look at the tutorial in the documentation.
    
    tikzedgelabels
        Defaults to True, meaning that the tikz edge label placement algorithm is used to position the labels.
        If set to False, the graphviz algorithm is used instead. Just try out what gives better performance for your graph.

    lenAsLabel
        Defaults to False. If set to True, the 'len' attribute of the graph edges will be used as label in the final tikz graph.
        Warning: This will override any 'label' attribute given to the graph edge.
    
    scale_total
        Default is 1, resulting in no scaling at all. If the tikz output size is inappropriate in your document, you can use this factor to scale the whole tikzpicture.
    
    scale_edge_lengths
        Default is 1, resulting in no scaling at all. If the ratio of edge length to node size is not appropriate, you can use this factor to scale the edge lengths only. This will result in a differently sized picture, however you can scale the total size of the picture with `scale_total`.
    
    texmode
        Defaults to 'math', meaning that the text in your node/edge labels will be processed as latex math.
        You can alternatively set it to 'verbatim' or 'raw', resulting in the corresponding processing.

    **kwargs
        The keywords and arguments are taken from http://www.graphviz.org/doc/info/attrs.html
        and have exactly the same meaning.
        However, only `overlap`,  `sep`, `splines` and `orientation` have shown an effect in this function, so other keywords are not permitted.
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
            graphoptions = "      graph   [  "
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
    """
    Returns a .tex file that can be included as a frame in a beamer presentation.

    Parameters
    ------------
    directory
        Directory where 'graph<i>.tex' files are located.
        graphn.tex is included in the frame, if all files graphi.tex with 0 < i < n are in `directory`.
    
    title
        The frametitle of the returned frame.
    
    path
        The name of the .tex file that is to be modified.

    caption_list
        The i-th caption gets assigned to the i-th snapshot.
        If there are too many captions they are simply ignored.
        If there are not enough captions, the last snapshots get no caption.
        
    """
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
    """
    Returns a compilable .tex file with all snapshots as figures.

    Parameters
    ------------
    directory
        Directory where 'graph<i>.tex' files are located.
        graphn.tex is included in the frame, if all files graphi.tex with 0 < i < n are in `directory`.
    
    title
        The title of the document.

    path
        The name of the .tex file that is to be modified.
    
    caption_list
        The i-th caption gets assigned to the i-th snapshot.
        If there are too many captions they are simply ignored.
        If there are not enough captions, the last snapshots get no caption.

    """
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
    for texfile in texfiles:
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

def standalone(directory):
    """
    Returns a compilable .tex file for each image generated containing the image

    Parameters 
    ------------
    directory
        Directory where 'graph<i>.tex' files are located.
        graphn.tex is included in the frame, if all files graphi.tex with 0 < i < n are in `directory`.

    """
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
    #latex_doc_lines = [r"\documentclass{standalone}", r"\usepackage{tikz}", r"\usetikzlibrary{decorations,arrows,shapes}", "\n", r"\begin{document}"]
    os.chdir(directory)
    for texfile in texfiles:
        filerawname = texfile.split(".")[0]
        latex_document = r"""\documentclass{standalone}
\usepackage{tikz}
\usetikzlibrary{decorations,arrows,shapes}
\begin{document}
\input{""" + filerawname + r""".tex}
\end{document}"""
        with open(filerawname + "stda.tex", "w+") as f:
            f.write(latex_document)
        
        os.system(f"pdflatex {filerawname}stda.tex")