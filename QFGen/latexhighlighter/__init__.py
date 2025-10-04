#from tex_highlighter import PdfViewer,LatexText,LaTeXCompiler,LaTeXModifier

try:
    from question_abstractor import ExoAbstractor
    from color_manager import ColorManager
except ImportError:
    from .color_manager import ColorManager
    #from .question_abstractor import ExoAbstractor