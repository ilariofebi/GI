#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 11 17:43:59 2019

@author: ilario
"""

import sqlite3
import json
import traceback

WHERE_BASE = ' WHERE 1=1 '

def db_conn(as_dict = False):
    conn = sqlite3.connect('GestioneImpreseNG.db')
    
    def dict_factory(cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    if as_dict:
        conn.row_factory = dict_factory
    c = conn.cursor()
    return conn, c
#%%

def db_select(sql, params=None, limit=100, as_dict = False):
    if limit is not None:
        sql = f'{sql} LIMIT {limit}'
        
    try:
        conn, c = db_conn(as_dict)
        if params is None:
            c.execute(sql)
        else:
            c.execute(sql, params)
    except:
        tb = traceback.format_exc()
        print(f'ERROR:\n {tb}\n sql: {sql};\n params: {params}')
        conn.rollback()
        return False
    else:
        ret = c.fetchall()
    finally:
        conn.close()
        
    return ret

#%%
def viewAllDetail(id_impresa):
    sql = '''
    SELECT *
    FROM imprese I 
        JOIN soa S ON I.id = S.idImpresa
        JOIN iso I ON I.id = I.idImpresa
    WHERE id = ?
    '''
    return db_select(sql, (id_impresa,), as_dict=True)
#%%


def viewIso(wc=None, params=None):
    sql = 'SELECT * FROM view_main_iso'
    
    if wc != WHERE_BASE:
        sql += wc
    else: sql += '''
        WHERE (scadenzaAnnuale_9001 is not null 
               OR scadenzaAnnuale_14001 is not null 
               OR scadenzaAnnuale_18001 is not null)
        ORDER BY scadenzaAnnuale_9001, scadenzaAnnuale_14001, scadenzaAnnuale_18001
        '''

    print(sql, params)
    return db_select(sql, params, as_dict = True)

def viewSoa(wc=None, params=None, cat_class_search=False):
    if cat_class_search == True:
        sql = 'SELECT * FROM view_main_soa_cat_class_search'
    else:
        sql = 'SELECT * FROM view_main_soa'
        
    if wc != WHERE_BASE:
        sql += wc
    else:
        sql += ''' WHERE stato like 'Attestato Ideal %' or stato like 'Contratto Ideal %' '''

    print(sql, params)
    return db_select(sql, params, as_dict = True)


#%%

def staticList():
    #sql='select Indice, IDCategoria from Categorie order by Indice'
    sql='select IDCategoria from Categorie order by Indice'
    categorie = db_select(sql)
    
    #sql='select Classifica, IDLivelloImporto from Classifiche order by classifica'
    sql='select IDLivelloImporto from Classifiche order by classifica'
    classifiche = db_select(sql)
    
    sql='select stato from SOA group by stato order by stato'
    soa_stati = db_select(sql)
    
    #TODO: la tabella ISO non ha stato, ma nel motore di ricerca c'e'... che faccio?
    #sql='select stato from ISO group by stato order by stato'
    #iso_stati = db_select(sql)
    iso_stati = []
    
    return dict(categorie = categorie, 
                classifiche = classifiche,
                soa_stati = soa_stati,
                iso_stati = iso_stati,
                )

def buildUpdate(tbl, pk, data):
    sql = 'UPDATE %s SET '% tbl
    values = []
    for k, v in data.items():
        if k != pk[0]:
            sql += '%s = ?,' % k
            values.append(v)
    sql = sql[:-1]
    sql += ' WHERE %s = %s' % (pk[0], pk[1])
    return sql, values

def buildWhereCondSoa(item):
    wc = WHERE_BASE # where cond
    wcp = []
    if item.ragione_sociale is not None:
        wc += "AND ragioneSociale LIKE ? "
        wcp.append(f'%{item.ragione_sociale}%')
        
    if item.riferimenti is not None:
        wc += "AND riferimenti LIKE ? "
        wcp.append(f'%{item.riferimenti}%') 
    
    if item.cf is not None:
        wc += "AND UPPER(codFisc) LIKE UPPER(?) "
        wcp.append(f'%{item.cf}%')
    if item.idImpresa is not None:
        wc += "AND id = ? "
        wcp.append(item.idImpresa)
    if item.comune is not None:
        wc += "AND (UPPER(l_comune) = UPPER(?) OR UPPER(o_comune) = UPPER(?)) "
        wcp.append(item.comune)
        wcp.append(item.comune)
    if item.prov is not None:
        wc += "AND (UPPER(l_prov) = UPPER(?) OR UPPER(o_prov) = UPPER(?)) "
        wcp.append(item.prov)
        wcp.append(item.prov)
    
    if item.stato is not None:
        wc += "AND stato = ? "
        wcp.append(item.stato)
        
    # select C.value from SOA, json_each(SOA.categorie) C order by idImpresa;
    if item.categoria is not None:
        wc += "AND categoria = ? "
        wcp.append(item.categoria)
    if item.classifica is not None:
        wc += "AND classifica = ? "
        wcp.append(item.classifica)


    if item.da is not None:
        wc += "AND scadenza BETWEEN ? and ? "
        wcp.append(item.da)
        wcp.append(item.a)
        
    #print(wc, wcp)
    return wc, wcp

def buildWhereCondIso(item):
    wc = ' WHERE 1=1 ' # where cond
    wcp = []
    if item.ragione_sociale is not None:
        wc += "AND ragioneSociale LIKE ? "
        wcp.append(f'%{item.ragione_sociale}%')
        
    if item.riferimenti is not None:
        wc += "AND riferimenti LIKE ? "
        wcp.append(f'%{item.riferimenti}%') 
    
    if item.cf is not None:
        wc += "AND UPPER(codFisc) LIKE UPPER(?) "
        wcp.append(f'%{item.cf}%')
    if item.idImpresa is not None:
        wc += "AND id = ? "
        wcp.append(item.idImpresa)
    
    return wc, wcp
        
#Execute
def db_edit(sql, params = None):
    try:
        conn, c = db_conn()
        if params is None:
            c.execute(sql)
        else:
            c.execute(sql, params)
    except:
        tb = traceback.format_exc()
        print(f'ERROR:\n {tb}\n sql: {sql};\n params: {params}')
        conn.rollback()
        return -1
    else:
        conn.commit()
    finally:
        conn.close()
    
    return c.lastrowid
    
#%%

def newImpresa():
    sql = "INSERT INTO Imprese (ragioneSociale) VALUES ('Nuova Impresa')"
    lastId = db_edit(sql)
    sql = "INSERT INTO SOA (idImpresa) VALUES (?)"
    db_edit(sql, (lastId,))
    sql = "INSERT INTO ISO (idImpresa) VALUES (?)"
    db_edit(sql, (lastId,))
    return lastId

#Test
#print(new_impresa())
#%%
    
def rmImpresa(id_impresa):
    sql = "DELETE FROM SOA where idImpresa = ?"
    db_edit(sql, (id_impresa,))
    sql = "DELETE FROM ISO where idImpresa = ?"
    db_edit(sql, (id_impresa,))
    sql = "DELETE FROM Imprese WHERE id = ?"
    db_edit(sql, (id_impresa,))
    return id_impresa

def updateImpresa(id_impresa, imp, soa, iso):
    #print(id_impresa)
    sql, params = buildUpdate('Imprese', ('id', id_impresa), imp)
    db_edit(sql, params)
    
    sql, params = buildUpdate('SOA', ('idImpresa', id_impresa), soa)
    db_edit(sql, params)
    
    sql, params = buildUpdate('ISO', ('idImpresa', id_impresa), iso)
    db_edit(sql, params)

    return 0
    
def searchSoa(search_params):
    wc, wcp = buildWhereCondSoa(search_params)
    
    if search_params.categoria is not None or search_params.classifica:
        # Se si cerca qualcosa in categoria o classifica, e' necessario usare una query diversa
        return viewSoa(wc = wc, params = wcp, cat_class_search=True)
    return viewSoa(wc = wc, params = wcp)

def searchIso(search_params):
    wc, wcp = buildWhereCondIso(search_params)
    return viewIso(wc = wc, params = wcp)
    
    
    
if __name__ == "__main__":
    pass