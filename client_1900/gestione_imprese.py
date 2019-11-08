#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 27 18:34:22 2019

@author: Ilario Febi
"""

import sys

from PyQt5.QtWidgets import QMainWindow, QApplication, QTableWidgetItem, QWidget, QAction, QMessageBox, QDialogButtonBox
from PyQt5.QtCore import pyqtSignal as SIGNAL
from PyQt5.QtCore import QDate, QUrl
from PyQt5.QtGui import QDesktopServices
from main_w import Ui_MainWindow
from edita_impresa import Ui_Form
import requests
import copy
from dbMapper import dbMap, dbMap_main
import json
import os
from datetime import date, timedelta, datetime
from config import SITE, USER, DOCUPATH

#QApplication.setAttribute(Qt.AA_Use96Dpi)
#QApplication.setAttribute(Qt.AA_DisableHighDpiScaling)

#TODO: info sulla data ultimo download e ultima modifica
# Oppure USER in configurazione poi update su impresa quando la finestra di modifica e' aperta (user + data ora) 
# con tasto UNLOCK su modifica per eventuali bloccaggi

'''
def rGet(url):
    headers = {'accept': 'application/json', }
    response = requests.get(f'{SITE}/{url}', headers=headers)
    return response.json()
'''

def httpReq(url, params=None, data=None, method='post'):
    headers = {'Content-Type': 'application/json',}

    if params is not None:
        params = (params,)
    
    if method == 'post':
        resp = requests.post(f'{SITE}/{url}', headers=headers, params=params, data=json.dumps(data))
    elif method == 'get':
        resp = requests.get(f'{SITE}/{url}', headers=headers, params=params, data=json.dumps(data))
    try:
        rj = resp.json()
    except:
        print(resp.text)
    else:        
        return rj

def scrub(x, blank='---'):
    """
    Sostituisce i None del json con blank

    :param x:
    :return:
    """
    ret = copy.deepcopy(x)
    # Handle dictionaries. Scrub all values
    if isinstance(x, dict):
        for k,v in ret.items():
            ret[k] = scrub(v, blank)
    elif isinstance(x, list):
        for k, v in enumerate(ret):
            ret[k] = scrub(v, blank)
    # Handle None
    if x is None:
        ret = blank
    # Finished scrubbing
    return ret

class EditaImpresa(QWidget):
    def __init__(self, id_impresa):
        super().__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        
        # Seleziono il primo TAB (Generale) come quello di default
        self.ui.tabWidget.setCurrentIndex(0)
        
        self.id_impresa = id_impresa
        self.docupath = os.path.realpath('{}/{}'.format(DOCUPATH, id_impresa))
        
        self.populate()
        
        # Button box
        self.ui.bt_box.button(QDialogButtonBox.Save).clicked.connect(self.save)
        self.ui.bt_box.button(QDialogButtonBox.Reset).clicked.connect(self.populate)
        self.ui.bt_box.button(QDialogButtonBox.Close).clicked.connect(self.closeWin)
        self.ui.bt_box.button(QDialogButtonBox.Discard).clicked.connect(self.eliminaImpresa)
        
        # Add date
        self.ui.soa__add_date.clicked.connect(self.soaAddDate)
        self.ui.iso__add_date.clicked.connect(self.isoAddDate)
        
        self.ui.bt_browser_doc.clicked.connect(self.openDocuPath)
        #self.show()
        #url = QUrl('https://github.com/bioinformatist/Gao-s-SB#examples')
        
        self.date_format = '%d/%m/%Y'

    def closeWin(self):
        print('Close Win')
        self.close()

    def openDocuPath(self):
        if not os.path.isdir(self.docupath):
            os.mkdir(self.docupath)
            
        if sys.platform == 'linux':
            self.docupath = os.path.realpath('{}/{}'.format(self.docupath, self.id_impresa)) #? ???
            print(self.docupath)
            self.openFolder(self.docupath) #Linux   
        else:
            os.startfile(self.docupath) #Win
        
    def soaAddDate(self):
        t = self.ui.soa__note.toPlainText()
        today = date.today().strftime(self.date_format)
        self.ui.soa__note.setText('%s\n%s: ' % (t, today))
    
    def isoAddDate(self):
        t = self.ui.soa__note.toPlainText()
        today = date.today().strftime(self.date_format)
        self.ui.iso__note.setText('%s\n%s: ' % (t, today))
    
    def openFolder(self, path=None):
        #https://www.programcreek.com/python/example/93389/PyQt5.QtGui.QDesktopServices.openUrl
        dirPath = os.path.dirname(os.path.abspath(path))
        url = QUrl.fromLocalFile(dirPath)
        QDesktopServices.openUrl(url)
        #self.Dialog.close()

    def eliminaImpresa(self):
        resp = QMessageBox.warning(self, 'Attenzione', "Eliminare l'impresa %s?" % self.id_impresa, QMessageBox.Yes|QMessageBox.No)
        if resp == QMessageBox.Yes:
            print('si')
            
            #r = rGet('rmImpresa?id_impresa=%s' % self.id_impresa)
            r = httpReq('rmImpresa', params=('id_impresa', self.id_impresa), method='get')
            if r == int(self.id_impresa):
                self.closeWin()
            else:
                QMessageBox.warning(self, 'Errore', "Errore durante la l'eliminazione dell'impresa %s" % self.id_impresa)

    def DisplayTableFromDict(self, obj, data_tbl):
        # Mostra il contenuto di una tabella a partire da un dizionario
        table_w = obj['obj']
        col_order = obj['col_order']
        
        rowNo = 0
        
        
        if obj.get('dfix'):
            table_w.setRowCount(obj['dfix'])
            len_data_tbl = obj['dfix']
        else:
            len_data_tbl = len(data_tbl)
            table_w.setRowCount(len_data_tbl+1)
            
        if len_data_tbl == 0:
            return        
        for r in data_tbl:
            for k, v in r.items():
                colNo = col_order.index(k)
                oneColumn = QTableWidgetItem(str(v))
                table_w.setItem(rowNo, colNo, oneColumn)
                table_w.resizeColumnToContents(colNo)
            rowNo += 1
            

    def tableExtract(self, obj):
        table_w = obj['obj']
        col_order = obj['col_order']
        out = []
        
        for row in range(0, table_w.rowCount()):
            colNum = 0
            row_dict = {}
            for col in col_order:
                item = table_w.item(row,colNum)
                if item is not None:
                    if len(item.text()) > 0:
                        row_dict[col] = item.text()
                    #print(table_w.item(row,colNum).currentText())
                colNum += 1
            if len(row_dict) > 0 or obj.get('dfix'):
                out.append(row_dict)
        return json.dumps(out)
        
        
    def save(self):
        # Impresa
        update_imp = {}
        for k, obj in dbMap().QLE_imp_dict(self.ui).items():
            #obj.get
            update_imp[k] = obj.text()
            
        for k, obj in dbMap().QTW_imp_dict(self.ui).items():
            update_imp[k] = self.tableExtract(obj)
        #print(json.dumps(update_imp))
            
        # SOA
        update_soa = {}
        for k, obj in dbMap().QLE_soa_dict(self.ui).items(): # Line Edit
            update_soa[k] = obj.text()
            
        for k, obj in dbMap().QTB_soa_dict(self.ui).items():
            update_soa[k] = obj.toPlainText()
            
        for k, obj in dbMap().QTW_soa_dict(self.ui).items():
            update_soa[k] = self.tableExtract(obj)
            
        for k, obj in dbMap().QLEDate_soa_dict(self.ui).items():
            #for date_format in ['%d-%m-%Y', '%d/%m/%Y']:
            #https://stackoverflow.com/questions/7367204/python-date-validation#7367307
            if len(obj.text()) > 0:
                #date_format = '%d/%m/%Y'
                try:
                    d = datetime.strptime(obj.text(), self.date_format)
                except:
                    QMessageBox.warning(self, 'Errore', "Data %s malformata!!\nInserire la data nel formato\n gg-mm-aaaa" % obj.text())
                    return None
                update_soa[k] = d.strftime('%Y-%m-%d')
            else:
                update_soa[k] = ''
        
        # ISO
        update_iso = {}
        
        for k, obj in dbMap().QLE_iso_dict(self.ui).items(): # Line Edit
            update_iso[k] = obj.text()
        
        for k, obj in dbMap().QTB_iso_dict(self.ui).items(): # Text Browser
            update_iso[k] = obj.toPlainText()
            
        for k, obj in dbMap().QTW_iso_dict(self.ui).items(): # Table
            update_iso[k] = self.tableExtract(obj)
        #print(json.dumps(update_iso))
        
        out = dict(imp = update_imp,
                   soa = update_soa,
                   iso = update_iso)
        #print(json.dumps(out))
        res = httpReq('updateImpresa', params=('id_impresa', self.id_impresa), data=out, method='post')
        
        if res == 0:
            self.populate()
        else:
            QMessageBox.warning(self, 'Errore', "Errore durante l'aggiornamento dell'impresa %s" % self.id_impresa)

    
        
    def populate(self):
        # Impresa
        
        #r = rGet('viewAllDetail?id_impresa=%s' % self.id_impresa)
        #r = httpReq('viewAllDetail?id_impresa=%s' % self.id_impresa, method='get')
        
        r = httpReq('viewAllDetail', params=('id_impresa', self.id_impresa), method='get')
        if len(r) == 0:
            raise FileNotFoundError 
        r = scrub(r, blank='')[0]
        
        for k, obj in dbMap().QLE_imp_dict(self.ui).items(): # Line Edit
            v = r[k]
            obj.setText(str(v))
            
        for k, obj in dbMap().QTW_imp_dict(self.ui).items(): # Table

            try:
                self.DisplayTableFromDict(obj, json.loads(r[k]))
            except json.decoder.JSONDecodeError:
                print(k, r[k])
        # SOA
        for k, obj in dbMap().QLE_soa_dict(self.ui).items(): # Line Edit
            v = r[k]
            obj.setText(str(v))
        
        for k, obj in dbMap().QTB_soa_dict(self.ui).items(): # Text Browser
            v = r[k]
            obj.setText(str(v)) # TODO: trasformare in setHtml
        
        for k, obj in dbMap().QTW_soa_dict(self.ui).items(): # Table
            self.DisplayTableFromDict(obj, json.loads(r[k]))
        
        for k, obj in dbMap().QLEDate_soa_dict(self.ui).items(): # Date in formato line text
            if r[k] is None or len(r[k]) == 0:
                obj.setText(str(''))
            else:
                Y,M,D = r[k].split('-')
                v = '{}/{}/{}'.format(D,M,Y)
                obj.setText(str(v))
        '''        
        for k, obj in dbMap().QDE_soa_dict(self.ui).items(): # DateEdit
            #print(f"v: {r[k]}")
            #print(type(r[k]))
            if r[k] is None or len(r[k]) == 0:
                obj.setDate(QDate(2000,1,1))
                #obj.setEnabled(False)
                
            else:
                Y,M,D = r[k].split('-')
                obj.setDate(QDate(int(Y),int(M),int(D)))
        '''             
        
        # ISO
        for k, obj in dbMap().QLE_iso_dict(self.ui).items(): # Line Edit
            v = r[k]
            obj.setText(str(v))
        
        
        for k, obj in dbMap().QTB_iso_dict(self.ui).items(): # Text Browser
            #print(f"v: {r[k]}")
            #print(type(r[k]))
            v = r[k]
            obj.setText(str(v)) # TODO: trasformare in setHtml
        
        #print(dbMap().QTW_iso_dict(self.ui))
        for k, obj in dbMap().QTW_iso_dict(self.ui).items(): # Table
            #print(k)
            self.DisplayTableFromDict(obj, json.loads(r[k]))


        
class AppWindow(QMainWindow):
    def __init__(self):
        #SetUp Variables
        self.row2id = {}
        self.row2idSoa = {}
        self.row2idIso = {}
        
        self.today = date.today()
        self.yesterday = self.today - timedelta(1)
        
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Seleziono il primo TAB (SOA) come quello di default
        self.ui.tabWidget.setCurrentIndex(0)

        self.rowsSoa = scrub(httpReq('searchSoa', data={}, method='post'))
        self.rowsIso = scrub(httpReq('searchIso', data={}, method='post'))
        
        self.populate()
        self.updateStatic()

        self.showMaximized()
        self.ui.actionFull_Screen.triggered.connect(self.toggleFullScreen)

        self.ui.bt_iso_nuova_impresa.clicked.connect(self.newImpresa)
        self.ui.bt_soa_nuova_impresa.clicked.connect(self.newImpresa)
        #self.ui.bt_imp_mostra_tutto.clicked.connect(self.DisplayImprese)
        
        self.ui.bt_soa_stampa.clicked.connect(self.soaPrintPreview)
        self.ui.bt_iso_stampa.clicked.connect(self.isoPrintPreview)
        
        self.ui.bt_soa_cerca.clicked.connect(self.soaCerca)
        self.ui.bt_iso_cerca.clicked.connect(self.isoCerca)
        
        # Ricarica i dati dei combo box dopo il click su Resetta Filtro
        self.ui.bt_soa_resetta_filtro.released.connect(self.updateStatic)
        
        # ToolTips
        #self.ui.bt_iso_cerca.setToolTip('Cerca sta minchia')
        #self.ui.ln_iso_cf.setToolTip('chiave1:valore1, chiave2:valore2')

    def updateStatic(self):
        # Liste di stati, categorie, classifiche per i menu select
        #staticList = rGet('staticList')
        staticList = httpReq('staticList', method='get')
        
        # Update dei combo box
        self.updateCB(self.ui.cb_soa_stato, staticList['soa_stati'])
        #TODO: self.updateCB(self.ui.cb_iso_stato, staticList['iso_stati']) 
        self.updateCB(self.ui.cb_soa_categoria, staticList['categorie'])
        self.updateCB(self.ui.cb_soa_classifica, staticList['classifiche'])

        # Update delle date
        self.ui.data_soa_da.setDate(QDate(self.today.year,
                                          self.today.month, 
                                          self.today.day))
        self.ui.data_soa_a.setDate(QDate(self.yesterday.year,
                                         self.yesterday.month,
                                         self.yesterday.day))
    
    def updateCB(self, obj, dataList):
        c = 0
        for i in dataList:
            #print(i)
            obj.addItem(i[0])
            c += 1
        
    def soaCerca(self):
        search = {}
        
        id_impresa = self.ui.ln_soa_id.text()
        if len(id_impresa) > 0:
            search['idImpresa'] = int(id_impresa)
        
        impresa = self.ui.ln_soa_impresa.text()
        if len(impresa) > 0:
            search['ragione_sociale'] = impresa
        
        cf = self.ui.ln_soa_cf.text()
        if len(cf) > 0:
            search['cf'] = cf
            
        riferimenti = self.ui.ln_soa_riferimenti.text()
        if len(riferimenti) > 0:
            search['riferimenti'] = riferimenti
        
        comune = self.ui.ln_soa_comune.text()
        if len(comune) > 0:
            search['comune'] = comune

        prov = self.ui.ln_soa_prov.text()
        if len(prov) > 0:
            search['prov'] = prov

        stato = self.ui.cb_soa_stato.currentText()
        if len(stato) > 0:
            search['stato'] = stato

        categoria = self.ui.cb_soa_categoria.currentText()
        if len(categoria) > 0:
            search['categoria'] = categoria
            
        classifica = self.ui.cb_soa_classifica.currentText()
        if len(classifica) > 0:
            search['classifica'] = classifica
            
        data_soa_da = self.ui.data_soa_da.date().toPyDate()
        data_soa_a = self.ui.data_soa_a.date().toPyDate()
        if data_soa_a >= data_soa_da:
            search['da'] = str(data_soa_da)
            search['a'] = str(data_soa_a)
        elif data_soa_a == self.yesterday and data_soa_da == self.today:
            # Caso default per non inviare ricerche sulla data
            pass
        else:
            QMessageBox.warning(self, 'Attenzione', "Date non congruenti nella ricerca")

            
        #print(search)
        self.rowsSoa = scrub(httpReq('searchSoa', data=search, method='post'))
        if len(self.rowsSoa) == 0:
            QMessageBox.warning(self, 'Attenzione', "La ricerca non ha prodotto nessun risultato")
        elif len(self.rowsSoa) == 1:
            self.EI = EditaImpresa(self.rowsSoa[0]['id'])
            self.EI.show()
        else:
            self.populate()
        
    def isoCerca(self):
        search = {}
        
        id_impresa = self.ui.ln_iso_id.text()
        if len(id_impresa) > 0:
            search['idImpresa'] = int(id_impresa)
        
        impresa = self.ui.ln_iso_impresa.text()
        if len(impresa) > 0:
            search['ragione_sociale'] = impresa
        
        cf = self.ui.ln_iso_cf.text()
        if len(cf) > 0:
            search['cf'] = cf
            
        riferimenti = self.ui.ln_iso_riferimenti.text()
        if len(riferimenti) > 0:
            search['riferimenti'] = riferimenti
        
        prov = self.ui.ln_iso_prov.text()
        if len(prov) > 0:
            search['prov'] = prov

        stato = self.ui.cb_iso_stato.currentText()
        if len(stato) > 0:
            search['stato'] = stato

        
        self.rowsIso = httpReq('searchIso', data=search, method='post')
        if len(self.rowsIso) == 0:
            QMessageBox.warning(self, 'Attenzione', "La ricerca non ha prodotto nessun risultato")
        elif len(self.rowsIso) == 1:
            self.EI = EditaImpresa(self.rowsIso[0]['id'])
            self.EI.show()
        else:
            self.populate()

    def DisplayTableFromDict(self, obj, data_tbl):
        # Mostra il contenuto di una tabella a partire da un dizionario
        table_w = obj['obj']
        col_order = obj['col_order']
        
        rowNo = 0
        
        if obj.get('dfix'):
            table_w.setRowCount(obj['dfix'])
            len_data_tbl = obj['dfix']
        else:
            len_data_tbl = len(data_tbl)
            table_w.setRowCount(len_data_tbl+1)
            
        if len_data_tbl == 0:
            return        
        for r in data_tbl:
            for k, v in r.items():
                if k in col_order:
                    colNo = col_order.index(k)
                    oneColumn = QTableWidgetItem(str(v))
                    table_w.setItem(rowNo, colNo, oneColumn)
                    table_w.resizeColumnToContents(colNo)
            rowNo += 1
        
        # Sbianchetta l'ultima riga
        for colNo in range(table_w.columnCount()):
            table_w.setItem(rowNo, colNo, QTableWidgetItem(""))

    def reindex(self, rows, idx='id'):
        # Associa l'id della tabella con il numero di riga
        out = {}
        for i in range(len(rows)):
            out[i] = rows[i][idx]
        return out
        
    def populate(self):
        # Soa
        obj = dbMap_main().QTW_soa_dict(self.ui)
        self.DisplayTableFromDict(obj, self.rowsSoa)
        obj['obj'].cellDoubleClicked['int', 'int'].connect(self.callEditaImpresaFromSoa)
        self.row2idSoa = self.reindex(self.rowsSoa)

        # ISO
        obj = dbMap_main().QTW_iso_dict(self.ui)
        self.DisplayTableFromDict(obj, self.rowsIso)
        obj['obj'].cellDoubleClicked['int', 'int'].connect(self.callEditaImpresaFromIso)
        self.row2idIso = self.reindex(self.rowsIso)

    def callEditaImpresaFromSoa(self, x, y):
        self.row2id = self.row2idSoa
        self.callEditaImpresa(x, y)
        
    def callEditaImpresaFromIso(self, x, y):
        self.row2id = self.row2idIso
        self.callEditaImpresa(x, y)

    def newImpresa(self):
        #lastId = rGet('newImpresa')
        lastId = httpReq('newImpresa', method='get')
        
        #print(lastId)
        self.EI = EditaImpresa(lastId)
        self.EI.show()

    def callEditaImpresa(self, x, y):
        #print('si ',x, y, self.row2id[x])
        try:
            id_impresa = self.row2id[x]
            self.EI = EditaImpresa(id_impresa)
            self.EI.show()
        except KeyError:
            #raise
            QMessageBox.warning(self, 'Errore', 'id impresa non presente')
        except FileNotFoundError:
            QMessageBox.warning(self, 'Errore', 'id impresa non presente')
            
    def toggleFullScreen(self):
        #if self.isFullScreen():
        if self.isMaximized():
            print("Fullscreen mode: off")
            self.showNormal()
        else:
            print("Fullscreen mode: on")
            #self.showFullScreen()
            self.showMaximized()
        
    def isoPrintPreview(self):
        obj = dbMap_main().QTW_iso_pr_dict()
        data = self.rowsIso
        self.printPreview(obj, data)
    
    def soaPrintPreview(self):
        obj = dbMap_main().QTW_soa_pr_dict()
        data = self.rowsSoa
        self.printPreview(obj, data)
        
    def printPreview(self, obj, data):
        from PyQt5.QtPrintSupport import QPrinter, QPrintPreviewDialog
        from PyQt5.QtGui import QTextDocument, QTextCursor, QTextTableFormat, QTextFrameFormat#, QFont
        import time
        
        self.printer = QPrinter();
        self.printer.setPageSize(QPrinter.A4);
        self.printer.setOrientation(QPrinter.Landscape);
        self.printer.setFullPage(True);
        self.printer.setPageMargins(2,2,2,2,QPrinter.Millimeter);
        #self.printer.setFont(QFont("times",22))
        
        dialog = QPrintPreviewDialog(self.printer)
        #dialog.showFullScreen()
        
        
        document = QTextDocument()
        
        #document.setHtml("<html><head></head><body></body></html>")
        document.setHtml("")
        cursor = QTextCursor(document)
        
        # Titolo
        cursor.insertHtml("<h2 align=center>%s</h2>" % obj['title'])
        cursor.insertText("\n")
        # Data
        cursor.insertHtml("<h5 align=left>%s</h5>" % time.strftime("%d/%m/%Y"))
        cursor.insertText("\n")
        
        # Table
        tableFormat = QTextTableFormat()
        tableFormat.setCellPadding(2)
        tableFormat.setCellSpacing(3)
        #tableFormat.setBorderStyle(QTextFrameFormat.BorderStyle_Ridge)
        tableFormat.setBorder(0)
        
        cursor.insertTable(len(data) + 2, len(obj['col_name']), tableFormat)
        
        # Intestazioni
        for table_title in obj['col_name']:
            cursor.insertHtml('<font size="4" color="blue"><b>%s</b></font>' % table_title)
            cursor.movePosition(QTextCursor.NextCell)
        
        # Riga bianca
        for table_title in obj['col_name']:
            cursor.insertText(' ')
            cursor.movePosition(QTextCursor.NextCell)

        # Dati Tabella            
        for r in data:
            for k in obj['col_order']:
                v = r[k]
                if v is not None:
                    #cursor.insertText(str(v))
                    cursor.insertHtml('<font size="4">%s</font>' % v)
                    cursor.movePosition(QTextCursor.NextCell)
        
        dialog.paintRequested.connect(document.print_)
        dialog.setFixedSize(1500,1050)
        dialog.exec_()
        
        
if __name__=='__main__':
    
    # Handle Ctrl+C
    import signal
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    app = QApplication(sys.argv)
    #print(sys.argv)
    if len(sys.argv) == 1:
        w = AppWindow()
    else:
        w = EditaImpresa(sys.argv[1])
    w.show()
    sys.exit(app.exec_())

