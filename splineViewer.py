from xml.dom import minidom
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QFileDialog
import sys
import numpy as np
import viewerGui


class splViewer(QtWidgets.QMainWindow, viewerGui.Ui_MainWindow):
    def __init__(self,parent=None):
        super(splViewer,self).__init__(parent)
        self.setupUi(self)

        self.statusBar().showMessage('Ready')
        self.actionRead_dfspl.triggered.connect(self.openFileNameDialog)


        self.model = QtGui.QStandardItemModel()
        self.model.resetInternalData()
        self.rootNode = self.model.invisibleRootItem()
        self.branch1 = QtGui.QStandardItem("Splines")         
         
        self.rootNode.appendRow([ self.branch1,None])
        


        self.treeView.setRootIsDecorated(True)
        self.treeView.setModel(self.model)
        self.treeView.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.treeView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        

        self.treeView.clicked.connect(self.clickTree)
        self.treeView.customContextMenuRequested.connect(self.openContextMenu)

        x = [0,1,2,3,4]
        y = [0,1,2,3,4]

        self.updatePlot(x,y)
       
        self.tableWidget.setColumnCount(2)
        self.tableWidget.setHorizontalHeaderLabels(['x', 'Fx'])
        self.tableWidget.horizontalHeader().setStretchLastSection(True) 
        self.tableWidget.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        
        self.updateTable(x,y)

        self.myMenu = QtWidgets.QMenu('Menu', self)
        self.myMenu.addAction(QtWidgets.QAction('DeleteMe',self))
        self.splineList = []


    def updatePlot(self,x,y):

        self.Mplwidget.canvas.ax1.clear()
        self.Mplwidget.canvas.ax1.plot(x,y)
        # Show the major grid lines with dark grey lines
        self.Mplwidget.canvas.ax1.grid(b=True, which='major', color='#666666', linestyle='-')

        # Show the minor grid lines with very faint and almost transparent grey lines
        self.Mplwidget.canvas.ax1.minorticks_on()
        self.Mplwidget.canvas.ax1.grid(b=True, which='minor', color='#999999', linestyle='-', alpha=0.2)
        self.Mplwidget.canvas.draw()
        
    def updateTable(self,x,y):
        while self.tableWidget.rowCount() > 0:
            self.tableWidget.removeRow(0)

        for i,j in zip(x,y):
            rowPos = self.tableWidget.rowCount()
            self.tableWidget.insertRow(rowPos)
            self.tableWidget.setItem(rowPos , 0, QtWidgets.QTableWidgetItem(str(i)))
            self.tableWidget.setItem(rowPos , 1, QtWidgets.QTableWidgetItem(str(j)))


    def openContextMenu(self):
        index = self.treeView.currentIndex()
        if (index.parent().data()):
            self.myMenu.exec_(QtGui.QCursor.pos())

            #myModel = index.model()
            #parent = index.parent()
            row = index.row()
            self.splineList.pop(row)
            self.updateMe()


    def clickTree(self):
        index = self.treeView.currentIndex()
        
        if (index.parent().data()):

            temp = self.splineList[index.row()].firstChild.nodeValue
            x,y = parseText2Array(temp)
                    

            self.updatePlot(x,y)
            self.updateTable(x,y)

            


    def updateMe(self):
        while self.branch1.rowCount() > 0:
            (self.branch1.removeRow(0))

        for i in self.splineList:
            myItem = QtGui.QStandardItem(i.getAttribute('name')) 
            self.branch1.appendRow([myItem])
            self.treeView.expandAll()


    def openFileNameDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","Spline XML Files (*.dfspl);;All Files (*)", options=options)
        if fileName:
            self.statusBar().showMessage("Try to open:  "+fileName)
            try:
                dom = minidom.parse(fileName)
                
                for i in dom.getElementsByTagName('Spline'):
                    self.splineList.append(i)
                    


                    
            except Exception as e:
                print(e)
                return False
        self.updateMe()
        return True

        


def parseText2Array(string):
    x=[];y=[]
    myList = string.split()
    for i in range(int(0.5*len(myList))):
        x.append(float(myList[i*2]))
        y.append(float(myList[i*2+1]))
    

    return x,y

def readXML():
    try:
        myFile = sys.argv[1]
        if not (os.path.isfile(myFile)):raise
    except Exception as e:
        print("Can't read input file ...")
        sys.exit()

    dom = minidom.parse(myFile)
    f = open('demo.xml','w')
    f.write(dom.toxml())
    f.close()
    pass


if __name__ == "__main__":

    app = QApplication(sys.argv)
    form = splViewer()
    form.show()
    app.exec_()