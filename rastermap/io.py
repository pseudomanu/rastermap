import os, glob
import numpy as np
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QPushButton, QLineEdit, QMessageBox, QFileDialog, QCheckBox, QDialog, QHBoxLayout, QVBoxLayout, QLabel, QWidget
import pyqtgraph as pg
from scipy.stats import zscore
import scipy.io as sio
from . import guiparts

def load_mat(parent, name=None): # Load data matrix (neurons x time)
    try:
        if name is None:
            name = QFileDialog.getOpenFileName(
                parent, "Open *.npy", filter="*.npy *.mat")
            parent.fname = name[0]
            parent.filebase = name[0]
            ext = parent.fname.split(".")[-1]
        else:
            parent.fname = name
            parent.filebase = name
        parent.update_status_bar("Loading "+ parent.fname)
        if ext == "mat":        #Note: can only load mat files containing one key assigned to data matrix
            X = sio.loadmat(parent.fname)
            for i, key in enumerate(X.keys()):
                if key not in ['__header__', '__version__', '__globals__']:
                    X = X[key]
        elif ext == "npy":
            X = np.load(parent.fname) # allow_pickle=True
        else:
            raise Exception("Invalid file type")
    except Exception as e:
            parent.update_status_bar('ERROR: this is not a *.npy array :( ')
            #parent.update_status_bar(e)
            X = None
    if X is not None and X.ndim > 1:
        parent.update_status_bar("Data loaded: "+ str(X.shape))
        iscell, file_iscell = parent.load_iscell()
        parent.file_iscell = None
        if iscell is not None:
            if iscell.size == X.shape[0]:
                X = X[iscell, :]
                parent.file_iscell = file_iscell
                parent.update_status_bar('using iscell.npy in folder')
        if len(X.shape) > 2:
            X = X.mean(axis=-1)
        parent.p0.clear()
        parent.sp = zscore(X, axis=1)
        del X
        parent.sp = np.maximum(-4, np.minimum(8, parent.sp)) + 4
        parent.sp /= 12
        parent.embedding = np.arange(0, parent.sp.shape[0]).astype(np.int64)[:,np.newaxis]
        parent.sorting = np.arange(0, parent.sp.shape[0]).astype(np.int64)
        
        parent.loaded = True
        parent.plot_activity()
        parent.show()
        parent.run_embedding_button.setEnabled(True)
        parent.upload_behav_button.setEnabled(True)
        parent.upload_run_button.setEnabled(True)

def get_rastermap_params(parent):
    if parent.custom_param_radiobutton.isChecked() and parent.loaded:
        dialog = QDialog()
        dialog.setWindowTitle("Set rastermap parameters")
        dialog.setFixedWidth(600)
        dialog.verticalLayout = QVBoxLayout(dialog)

        # Param options
        dialog.n_components_label = QLabel(dialog)
        dialog.n_components_label.setTextFormat(QtCore.Qt.RichText)
        dialog.n_components_label.setText("n_components:")
        dialog.n_components = QLineEdit()# QLabel(dialog)
        dialog.n_components.setText(str(1))
        dialog.n_components.setFixedWidth(45)
        dialog.n_components.setReadOnly(True)

        dialog.n_clusters_label = QLabel(dialog)
        dialog.n_clusters_label.setTextFormat(QtCore.Qt.RichText)
        dialog.n_clusters_label.setText("n_clusters:")
        dialog.n_clusters = QLineEdit()
        dialog.n_clusters.setText(str(50))
        dialog.n_clusters.setFixedWidth(45)

        dialog.n_neurons_label = QLabel(dialog)
        dialog.n_neurons_label.setTextFormat(QtCore.Qt.RichText)
        dialog.n_neurons_label.setText("n_neurons:")
        dialog.n_neurons = QLineEdit()
        dialog.n_neurons.setText(str(parent.sp.shape[0]))
        dialog.n_neurons.setFixedWidth(45)

        dialog.grid_upsample_label = QLabel(dialog)
        dialog.grid_upsample_label.setTextFormat(QtCore.Qt.RichText)
        dialog.grid_upsample_label.setText("grid_upsample:")
        dialog.grid_upsample = QLineEdit()
        dialog.grid_upsample.setText(str(10))
        dialog.grid_upsample.setFixedWidth(45)

        dialog.n_splits_label = QLabel(dialog)
        dialog.n_splits_label.setTextFormat(QtCore.Qt.RichText)
        dialog.n_splits_label.setText("n_splits:")
        dialog.n_splits = QLineEdit()
        dialog.n_splits.setText(str(4))
        dialog.n_splits.setFixedWidth(45)

        dialog.time_label = QLabel(dialog)
        dialog.time_label.setTextFormat(QtCore.Qt.RichText)
        dialog.time_label.setText("Time range:")
        dialog.slider = guiparts.TimeRangeSlider(parent)
        dialog.slider.setEnabled(False)
        dialog.time_checkbox = QCheckBox("Set time range")
        dialog.time_checkbox.setChecked(False)
        dialog.time_checkbox.toggled.connect(lambda: enable_time_range(dialog))

        dialog.ok_button = QPushButton('Ok')
        dialog.ok_button.setDefault(True)
        dialog.ok_button.clicked.connect(lambda: custom_set_params(parent, dialog))
        dialog.cancel_button = QPushButton('Cancel')
        dialog.cancel_button.clicked.connect(dialog.close)

        # Set layout of options
        dialog.widget = QWidget(dialog)
        dialog.horizontalLayout = QHBoxLayout(dialog.widget)
        dialog.horizontalLayout.setContentsMargins(-1, -1, -1, 0)
        dialog.horizontalLayout.setObjectName("horizontalLayout")
        dialog.horizontalLayout.addWidget(dialog.n_components_label)
        dialog.horizontalLayout.addWidget(dialog.n_components)
        dialog.horizontalLayout.addWidget(dialog.n_clusters_label)
        dialog.horizontalLayout.addWidget(dialog.n_clusters)

        dialog.widget2 = QWidget(dialog)
        dialog.horizontalLayout = QHBoxLayout(dialog.widget2)
        dialog.horizontalLayout.setContentsMargins(-1, -1, -1, 0)
        dialog.horizontalLayout.setObjectName("horizontalLayout")
        dialog.horizontalLayout.addWidget(dialog.n_neurons_label)
        dialog.horizontalLayout.addWidget(dialog.n_neurons)
        dialog.horizontalLayout.addWidget(dialog.n_splits_label)
        dialog.horizontalLayout.addWidget(dialog.n_splits)

        dialog.widget3 = QWidget(dialog)
        dialog.horizontalLayout = QHBoxLayout(dialog.widget3)
        dialog.horizontalLayout.setContentsMargins(-1, -1, -1, 0)
        dialog.horizontalLayout.setObjectName("horizontalLayout")
        dialog.horizontalLayout.addWidget(dialog.time_checkbox)
        dialog.horizontalLayout.addWidget(dialog.grid_upsample_label)
        dialog.horizontalLayout.addWidget(dialog.grid_upsample)

        dialog.widget4 = QWidget(dialog)
        dialog.horizontalLayout = QHBoxLayout(dialog.widget4)
        dialog.horizontalLayout.setContentsMargins(-1, -1, -1, 0)
        dialog.horizontalLayout.setObjectName("horizontalLayout")
        dialog.horizontalLayout.addWidget(dialog.time_label)
        dialog.horizontalLayout.addWidget(dialog.slider)

        dialog.widget5 = QWidget(dialog)
        dialog.horizontalLayout = QHBoxLayout(dialog.widget5)
        dialog.horizontalLayout.addWidget(dialog.cancel_button)
        dialog.horizontalLayout.addWidget(dialog.ok_button)

        # Add options to dialog box
        dialog.verticalLayout.addWidget(dialog.widget)
        dialog.verticalLayout.addWidget(dialog.widget2)
        dialog.verticalLayout.addWidget(dialog.widget3)
        dialog.verticalLayout.addWidget(dialog.widget4)
        dialog.verticalLayout.addWidget(dialog.widget5)

        dialog.adjustSize()
        dialog.exec_()

def enable_time_range(dialog):
    if dialog.time_checkbox.isChecked():
        dialog.slider.setEnabled(True)
    else:
        dialog.slider.setEnabled(False)

def set_rastermap_params(parent):
    if parent.default_param_radiobutton.isChecked():
        parent.n_clusters = 50
        parent.n_neurons = parent.sp.shape[0]
        if parent.n_neurons > 1000:
            parent.n_splits = min(4, parent.n_neurons//1000)
        else:
            parent.n_splits = 4
        parent.n_components = 1
        parent.grid_upsample = min(10, parent.n_neurons // (parent.n_splits * (parent.n_clusters+1)))
        parent.embed_time_range = -1

def custom_set_params(parent, dialogBox):
    try:
        parent.n_clusters = int(dialogBox.n_clusters.text())
        parent.n_neurons = int(dialogBox.n_neurons.text())
        parent.grid_upsample = int(dialogBox.grid_upsample.text())
        parent.n_splits = int(dialogBox.n_splits.text())
        parent.n_components = int(dialogBox.n_components.text())     
        if dialogBox.time_checkbox.isChecked():
            parent.embed_time_range = (dialogBox.slider.get_slider_values())
        else:
            parent.embed_time_range = -1
        parent.params_set = True
    except Exception as e:
        QMessageBox.about(parent, 'Error','Invalid input entered')
        #parent.update_status_bar(e)
        pass
    dialogBox.close()

def get_behav_data(parent):
    dialog = QDialog()
    dialog.setWindowTitle("Upload behaviour files")
    dialog.verticalLayout = QVBoxLayout(dialog)

    # Param options
    dialog.behav_data_label = QLabel(dialog)
    dialog.behav_data_label.setTextFormat(QtCore.Qt.RichText)
    dialog.behav_data_label.setText("Behavior matrix (*.npy, *.mat):")
    dialog.behav_data_button = QPushButton('Upload')
    dialog.behav_data_button.setFont(QtGui.QFont("Arial", 10, QtGui.QFont.Bold))
    dialog.behav_data_button.clicked.connect(lambda: load_behav_file(parent, dialog.behav_data_button))

    dialog.behav_comps_label = QLabel(dialog)
    dialog.behav_comps_label.setTextFormat(QtCore.Qt.RichText)
    dialog.behav_comps_label.setText("(Optional) Behavior labels file (*.npy):")
    dialog.behav_comps_button = QPushButton('Upload')
    dialog.behav_comps_button.setFont(QtGui.QFont("Arial", 10, QtGui.QFont.Bold))
    dialog.behav_comps_button.clicked.connect(lambda: load_behav_comps_file(parent, dialog.behav_comps_button))

    dialog.ok_button = QPushButton('Done')
    dialog.ok_button.setDefault(True)
    dialog.ok_button.clicked.connect(dialog.close)

    # Set layout of options
    dialog.widget = QWidget(dialog)
    dialog.horizontalLayout = QHBoxLayout(dialog.widget)
    dialog.horizontalLayout.setContentsMargins(-1, -1, -1, 0)
    dialog.horizontalLayout.setObjectName("horizontalLayout")
    dialog.horizontalLayout.addWidget(dialog.behav_data_label)
    dialog.horizontalLayout.addWidget(dialog.behav_data_button)

    dialog.widget1 = QWidget(dialog)
    dialog.horizontalLayout = QHBoxLayout(dialog.widget1)
    dialog.horizontalLayout.setContentsMargins(-1, -1, -1, 0)
    dialog.horizontalLayout.setObjectName("horizontalLayout")
    dialog.horizontalLayout.addWidget(dialog.behav_comps_label)
    dialog.horizontalLayout.addWidget(dialog.behav_comps_button)

    dialog.widget2 = QWidget(dialog)
    dialog.horizontalLayout = QHBoxLayout(dialog.widget2)
    dialog.horizontalLayout.addWidget(dialog.ok_button)

    # Add options to dialog box
    dialog.verticalLayout.addWidget(dialog.widget)
    dialog.verticalLayout.addWidget(dialog.widget1)
    dialog.verticalLayout.addWidget(dialog.widget2)

    dialog.adjustSize()
    dialog.exec_()

def load_behav_comps_file(parent, button):
    name = QFileDialog.getOpenFileName(
        parent, "Open *.npy", filter="*.npy"
    )
    name = name[0]
    parent.behav_labels_loaded = False
    try:
        if parent.behav_loaded:
            beh = np.load(name, allow_pickle=True) # Load file (behav_comps x time)
            if beh.ndim == 1 and beh.shape[0] == parent.behav_data.shape[0]:
                parent.behav_labels_loaded = True
                parent.behav_labels = beh
                parent.update_status_bar("Behav labels file loaded")
                button.setText("Uploaded!")
                parent.heatmap_checkBox.setEnabled(True)
            else:
                raise Exception("File contains incorrect dataset. Dimensions mismatch",
                            beh.shape, "not same as", parent.behav_data.shape[0])
        else:
            raise Exception("Please upload behav data (matrix) first")
    except Exception as e:
        print(e)
    add_behav_checkboxes(parent)

def add_behav_checkboxes(parent):
    # Add checkboxes for behav comps to display on heatmap and/or avg trace
    if parent.behav_labels_loaded:
        parent.behav_labels_selected = np.arange(0, len(parent.behav_labels)+1)
        if len(parent.behav_labels) > 5:
            prompt_behav_comps_ind(parent)
        clear_old_behav_checkboxes(parent)
        parent.heatmap_chkbxs.append(QCheckBox("All"))
        parent.heatmap_chkbxs[0].setStyleSheet("color: gray;")
        parent.heatmap_chkbxs[0].setChecked(True)
        parent.heatmap_chkbxs[0].toggled.connect(parent.behav_chkbx_toggled)
        parent.l0.addWidget(parent.heatmap_chkbxs[-1], 15, 12, 1, 2)
        for i, comp_ind in enumerate(parent.behav_labels_selected):
            parent.heatmap_chkbxs.append(QCheckBox(parent.behav_labels[comp_ind]))
            parent.heatmap_chkbxs[-1].setStyleSheet("color: gray;")
            parent.heatmap_chkbxs[-1].toggled.connect(parent.behav_chkbx_toggled)
            parent.heatmap_chkbxs[-1].setEnabled(False)
            parent.l0.addWidget(parent.heatmap_chkbxs[-1], 16+i, 12, 1, 2)
        parent.show_heatmap_ops()
        parent.update_scatter_ops_pos()
        parent.scatterplot_checkBox.setChecked(True)
    else:
        return

def clear_old_behav_checkboxes(parent):
    for k in range(len(parent.heatmap_chkbxs)):
        parent.l0.removeWidget(parent.heatmap_chkbxs[k])
    parent.heatmap_chkbxs = []

def prompt_behav_comps_ind(parent):
    dialog = QDialog()
    dialog.setWindowTitle("Select max 5")
    dialog.verticalLayout = QVBoxLayout(dialog)

    dialog.chkbxs = [] 
    for k in range(len(parent.behav_labels)):
        dialog.chkbxs.append(QCheckBox(parent.behav_labels[k]))
        dialog.chkbxs[k].setStyleSheet("color: black;")
        dialog.chkbxs[k].toggled.connect(lambda: restrict_behav_comps_selection(dialog, parent))

    dialog.ok_button = QPushButton('Done')
    dialog.ok_button.setDefault(True)
    dialog.ok_button.clicked.connect(lambda: get_behav_comps_ind(dialog, parent))

    # Add options to dialog box
    for k in range(len(dialog.chkbxs)):
        dialog.verticalLayout.addWidget(dialog.chkbxs[k])
    dialog.verticalLayout.addWidget(dialog.ok_button)
    
    dialog.adjustSize()
    dialog.exec_()

def get_behav_comps_ind(dialog, parent):
    parent.behav_labels_selected = []
    for k in range(len(parent.behav_labels)):
        if dialog.chkbxs[k].isChecked():
            parent.behav_labels_selected.append(k)
    dialog.close()

def restrict_behav_comps_selection(dialog, parent):
    chkbxs_count = 0
    for k in range(len(dialog.chkbxs)):
        if dialog.chkbxs[k].isChecked():
            chkbxs_count += 1
    if chkbxs_count > 5:
        for k in range(len(dialog.chkbxs)):
            dialog.chkbxs[k].setChecked(False)

def load_behav_file(parent, button):
    name = QFileDialog.getOpenFileName(
        parent, "Load behaviour data", filter="*.npy *.mat"
    )
    name = name[0]
    parent.behav_loaded = False
    try:  # Load file (behav_comps x time)
        ext = name.split(".")[-1]
        if ext == "mat":
            beh = sio.loadmat(name)
            load_behav_dict(parent, beh)
            del beh
        elif ext == "npy":
            beh = np.load(name, allow_pickle=True) 
            dict_item = False
            if beh.size == 1:
                beh = beh.item()
                dict_item = True
            if dict_item:
                load_behav_dict(parent, beh)
            else:  # load matrix w/o labels and set default labels
                if parent.embedded and parent.embed_time_range != -1:
                    beh = beh[:,parent.embed_time_range[0]:parent.embed_time_range[-1]]
                if beh.ndim == 2 and beh.shape[1] == parent.sp.shape[1]:
                    parent.behav_data = beh
                    clear_old_behav_checkboxes(parent)
                    parent.behav_loaded = True
                else:
                    raise Exception("File contains incorrect dataset. Dimensions mismatch",
                                beh.shape[1], "not same as", parent.sp.shape[1])
            del beh
    except Exception as e:
        print(e)
    if parent.behav_loaded:
        button.setText("Uploaded!")
        parent.behav_data = zscore(parent.behav_data, axis=1)
        parent.plot_behav_data()
        parent.heatmap_checkBox.setEnabled(True)
        parent.heatmap_checkBox.setChecked(True)
    else:
        return

def load_behav_dict(parent, beh):
    for i, key in enumerate(beh.keys()):
        if key not in ['__header__', '__version__', '__globals__']:
            if np.array(beh[key]).size == parent.sp.shape[1]:
                parent.behav_labels.append(key)
                parent.behav_labels_loaded = True
            else:
                parent.behav_binary_labels.append(key)
                parent.behav_binary_labels_loaded = True
    if parent.behav_labels_loaded:
        parent.behav_data = np.zeros((len(parent.behav_labels), parent.sp.shape[1]))
        for j, key in enumerate(parent.behav_labels):
            parent.behav_data[j] = beh[key]
        parent.behav_data = np.array(parent.behav_data)
        parent.behav_labels = np.array(parent.behav_labels)
        parent.behav_loaded = True
        add_behav_checkboxes(parent)
    if parent.behav_binary_labels_loaded:
        parent.behav_binary_data = np.zeros((len(parent.behav_binary_labels), parent.sp.shape[1]))
        parent.behav_bin_legend = pg.LegendItem(labelTextSize='12pt', horSpacing=30, colCount=len(parent.behav_binary_labels))
        for i, key in enumerate(parent.behav_binary_labels):
            dat = np.zeros(parent.sp.shape[1]) 
            dat[beh[key]] = 1                   # Convert to binary for stim/lick time
            parent.behav_binary_data[i] = dat
            parent.behav_bin_plot_list.append(pg.PlotDataItem(symbol=parent.symbol_list[i]))
            parent.behav_bin_legend.addItem(parent.behav_bin_plot_list[i], name=parent.behav_binary_labels[i])
            parent.behav_bin_legend.setPos(parent.run_trace_plot.x()+(20*i), parent.run_trace_plot.y())
            parent.behav_bin_legend.setParentItem(parent.p3)
            parent.p3.addItem(parent.behav_bin_plot_list[-1])
    if parent.behav_binary_data is not None:
        parent.plot_behav_binary_data()

def load_run_data(parent):
    name = QFileDialog.getOpenFileName(
        parent, "Open *.npy", filter="*.npy"
    )
    name = name[0]
    parent.run_loaded = False
    try:
        run = np.load(name)
        run = run.flatten()
        if parent.embedded and parent.embed_time_range != -1:
            run = run[parent.embed_time_range[0]:parent.embed_time_range[-1]]
        if run.size == parent.sp.shape[1]:
            parent.run_loaded = True
    except (ValueError, KeyError, OSError,
            RuntimeError, TypeError, NameError):
        parent.update_status_bar("ERROR: this is not a 1D array with length of data")
    if parent.run_loaded:
        parent.run_data = run
        parent.plot_run_trace()
        if parent.scatterplot_checkBox.isChecked():
            parent.scatterplot_checkBox.setChecked(True)
    else:
        return

def get_neuron_depth_data(parent):
    dialog = QDialog()
    dialog.setWindowTitle("Upload file")
    dialog.verticalLayout = QVBoxLayout(dialog)

    dialog.depth_label = QLabel(dialog)
    dialog.depth_label.setTextFormat(QtCore.Qt.RichText)
    dialog.depth_label.setText("Depth (Ephys):")
    dialog.depth_button = QPushButton('Upload')
    dialog.depth_button.setFont(QtGui.QFont("Arial", 10, QtGui.QFont.Bold))
    dialog.depth_button.clicked.connect(lambda: load_neuron_pos(parent, dialog.depth_button, depth=True))

    dialog.ok_button = QPushButton('Done')
    dialog.ok_button.setDefault(True)
    dialog.ok_button.clicked.connect(dialog.close)

    dialog.widget = QWidget(dialog)
    dialog.horizontalLayout = QHBoxLayout(dialog.widget)
    dialog.horizontalLayout.setContentsMargins(-1, -1, -1, 0)
    dialog.horizontalLayout.setObjectName("horizontalLayout")
    dialog.horizontalLayout.addWidget(dialog.depth_label)
    dialog.horizontalLayout.addWidget(dialog.depth_button)

    dialog.verticalLayout.addWidget(dialog.widget)
    dialog.verticalLayout.addWidget(dialog.ok_button)
    dialog.adjustSize()
    dialog.exec_()

def get_neuron_pos_data(parent):
    dialog = QDialog()
    dialog.setWindowTitle("Upload files")
    dialog.verticalLayout = QVBoxLayout(dialog)

    # Param options
    dialog.xpos_label = QLabel(dialog)
    dialog.xpos_label.setTextFormat(QtCore.Qt.RichText)
    dialog.xpos_label.setText("x position:")
    dialog.xpos_button = QPushButton('Upload')
    dialog.xpos_button.setFont(QtGui.QFont("Arial", 10, QtGui.QFont.Bold))
    dialog.xpos_button.clicked.connect(lambda: load_neuron_pos(parent, dialog.xpos_button, xpos=True))

    dialog.ypos_label = QLabel(dialog)
    dialog.ypos_label.setTextFormat(QtCore.Qt.RichText)
    dialog.ypos_label.setText("y position:")
    dialog.ypos_button = QPushButton('Upload')
    dialog.ypos_button.setFont(QtGui.QFont("Arial", 10, QtGui.QFont.Bold))
    dialog.ypos_button.clicked.connect(lambda: load_neuron_pos(parent, dialog.ypos_button, ypos=True))

    dialog.ok_button = QPushButton('Done')
    dialog.ok_button.setDefault(True)
    dialog.ok_button.clicked.connect(dialog.close)

    dialog.widget = QWidget(dialog)
    dialog.horizontalLayout = QHBoxLayout(dialog.widget)
    dialog.horizontalLayout.setContentsMargins(-1, -1, -1, 0)
    dialog.horizontalLayout.setObjectName("horizontalLayout")
    dialog.horizontalLayout.addWidget(dialog.xpos_label)
    dialog.horizontalLayout.addWidget(dialog.xpos_button)

    dialog.widget2 = QWidget(dialog)
    dialog.horizontalLayout = QHBoxLayout(dialog.widget2)
    dialog.horizontalLayout.setContentsMargins(-1, -1, -1, 0)
    dialog.horizontalLayout.setObjectName("horizontalLayout")
    dialog.horizontalLayout.addWidget(dialog.ypos_label)
    dialog.horizontalLayout.addWidget(dialog.ypos_button)

    # Add options to dialog box
    dialog.verticalLayout.addWidget(dialog.widget)
    dialog.verticalLayout.addWidget(dialog.widget2)
    dialog.verticalLayout.addWidget(dialog.ok_button)

    dialog.adjustSize()
    dialog.exec_()

def load_neuron_pos(parent, button, xpos=False, ypos=False, depth=False):
    try:
        file_name = QFileDialog.getOpenFileName(
                    parent, "Open *.npy", filter="*.npy")
        data = np.load(file_name[0])
        if xpos and data.size == parent.sp.shape[0]:
            parent.xpos_dat = data
            button.setText("Uploaded!")
            parent.update_status_bar("xpos data loaded")
        elif ypos and data.size == parent.sp.shape[0]: 
            parent.ypos_dat = data
            button.setText("Uploaded!")
            parent.update_status_bar("ypos data loaded")
        elif depth and data.size == parent.sp.shape[0]:
            parent.depth_dat = data
            button.setText("Uploaded!")
            parent.update_status_bar("depth data loaded")
        else:
            parent.update_status_bar("incorrect data uploaded")
            return
    except Exception as e:
        parent.update_status_bar('ERROR: this is not a *.npy array :( ')

def save_proc(parent): # Save embedding output
    try:
        if parent.embedded:
            if parent.save_path is None:
                folderName = QFileDialog.getExistingDirectory(parent,
                                    "Choose save folder")
                parent.save_path = folderName
                    
            else:
                raise Exception("Incorrect folder. Please select a folder")
            if parent.save_path:
                filename = parent.fname.split("/")[-1]
                filename, ext = os.path.splitext(filename)
                savename = os.path.join(parent.save_path, ("%s_rastermap_proc.npy"%filename))
                # Rastermap embedding parameters
                ops = {'n_components'       : parent.n_components, 
                        'n_clusters'        : parent.n_clusters,
                        'n_neurons'         : parent.n_neurons, 
                        'grid_upsample'     : parent.grid_upsample,
                        'n_splits'          : parent.n_splits,
                        'embed_time_range'  : parent.embed_time_range}
                proc = {'filename': parent.fname, 'save_path': parent.save_path,
                        'isort' : parent.sorting, 'embedding' : parent.embedding,
                        'U' : parent.U, 'ops' : ops}
                
                np.save(savename, proc, allow_pickle=True)
                parent.update_status_bar("File saved: "+ savename)
        else:
            raise Exception("Please run embedding to save output")
    except Exception as e:
        #parent.update_status_bar(e)
        return

def load_proc(parent, name=None):
    if name is None:
        name = QFileDialog.getOpenFileName(
            parent, "Open processed file", filter="*.npy"
            )
        parent.fname = name[0]
        name = parent.fname
    else:
        parent.fname = name
    try:
        proc = np.load(name, allow_pickle=True).item()
        parent.proc = proc
        X    = np.load(parent.proc['filename'])
        parent.filebase = parent.proc['filename']
        isort = parent.proc['isort']
        y     = parent.proc['embedding']
        u     = parent.proc['U'] 
        ops   = parent.proc['ops']
    except (ValueError, KeyError, OSError,
            RuntimeError, TypeError, NameError):
        parent.update_status_bar('ERROR: this is not a *.npy file :( ')
        X = None
    if X is not None:
        parent.filebase = parent.proc['filename']
        iscell, file_iscell = parent.load_iscell()

        parent.startROI = False
        parent.endROI = False
        parent.posROI = np.zeros((3,2))
        parent.prect = np.zeros((5,2))
        parent.ROIs = []
        parent.ROIorder = []
        parent.Rselected = []
        parent.Rcolors = []
        parent.p0.clear()

        parent.sp = zscore(X, axis=1)
        del X
        parent.sp = np.maximum(-4, np.minimum(8, parent.sp)) + 4
        parent.sp /= 12

        parent.embed_time_range = ops['embed_time_range']
        if parent.embed_time_range == -1:
            parent.sp = parent.sp
        else:
            parent.sp = parent.sp[:,parent.embed_time_range[0]:parent.embed_time_range[-1]]
        parent.embedding = y
        parent.sorting = isort
        parent.U = u
        parent.embedded = True

        ineur = 0
        parent.loaded = True
        parent.embedded = True
        parent.plot_activity()
        parent.ROI_position()
        parent.run_embedding_button.setEnabled(True)
        parent.upload_behav_button.setEnabled(True)
        parent.upload_run_button.setEnabled(True)
        parent.update_status_bar("Loaded: "+ parent.proc['filename'])
        parent.show()
