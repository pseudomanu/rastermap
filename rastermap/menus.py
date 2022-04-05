from PyQt5.QtWidgets import QAction
import pyqtgraph as pg
import numpy as np
from . import io

# ------ MENU BAR -----------------
def mainmenu(parent): 
    loadMat =  QAction("&Load data", parent)
    loadMat.setShortcut("Ctrl+L")
    loadMat.triggered.connect(lambda: io.load_mat(parent, name=None))
    parent.addAction(loadMat)
    
    # load processed data
    loadProc = QAction("&Load processed data", parent)
    loadProc.setShortcut("Ctrl+P")
    loadProc.triggered.connect(lambda: io.load_proc(parent, name=None))
    parent.addAction(loadProc)
    
    # Save processed data
    saveProc = QAction("&Save processed data", parent)
    saveProc.setShortcut("Ctrl+S")
    saveProc.triggered.connect(lambda: io.save_proc(parent))
    parent.addAction(saveProc)

    # export figure
    exportFig = QAction("Export as image (svg)", parent)
    exportFig.triggered.connect(lambda: export_fig(parent))
    exportFig.setEnabled(True)
    parent.addAction(exportFig)

    # make mainmenu!
    main_menu = parent.menuBar()
    file_menu = main_menu.addMenu("&File")
    file_menu.addAction(loadMat)
    file_menu.addAction(loadProc)
    file_menu.addAction(saveProc)
    file_menu.addAction(exportFig)

def export_fig(parent):
    parent.win.scene().contextMenuItem = parent.p0
    parent.win.scene().showExportDialog()

