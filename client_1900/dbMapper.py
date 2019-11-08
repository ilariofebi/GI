#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 16 22:12:49 2019

@author: ilario
"""

class dbMap:
    def QLE_imp_dict(self, obj):
        """
        Mappatura dei campi della tabella impresa con gli elementi QtLineEdit 
        """
        return dict(
            id = obj.cod_impresa, 
            ragioneSociale = obj.imp__ragione_sociale,
            codFisc = obj.imp__codice_fiscale,
            l_indirizzo = obj.imp__indirizzo_legale,
            l_prov = obj.imp__provincia_legale,
            l_comune = obj.imp__comune_legale, 
            o_indirizzo = obj.imp__indirizzo_op,
            o_prov = obj.imp__provincia_op,
            o_comune = obj.imp__comune_op,         
            sdi = obj.imp__sdi,
            #referenteAziendale = obj.imp__referente_az,
            tel = obj.imp__tel,
            fax = obj.imp__fax,       
            pec = obj.imp__pec, 
            webSite = obj.imp__website,
            email = obj.imp__email, 
            email2 = obj.imp__email2,
        )

    def QTW_imp_dict(self, obj):
        return dict(contatti = {'obj': obj.imp__contatti, 'col_order': ['referente','ruolo','cell','email','altro']})
        
    def QLE_soa_dict(self, obj):
        """
        Mappatura dei campi della tabella impresa con gli elementi QtLineEdit 
        """
        return dict(
            tipo = obj.soa__tipo,
            stato = obj.soa__stato,
            ente = obj.soa__ente,
            istruttore = obj.soa__istruttore,
            riferimenti = obj.soa__riferimenti,
            )
    
    def QTW_soa_dict(self, obj):
        return dict(
            categorie = {'obj': obj.soa__categorie, 'col_order': ['categoria','classifica']},
            contratti = {'obj': obj.soa__contratti, 'col_order': ['dataFirmaContratto','dataInvioContratto','tipoOperazione','prezzo','rate','finePagamento','percNostra','percDaDare','percDareA']}
            )

    def QTB_soa_dict(self, obj):
        return(dict(soa_note = obj.soa__note))
    
    def QLEDate_soa_dict(self, obj):
        return dict(
            scadQualita = obj.soa__scad_qualita,
            scadenza = obj.soa__scadenza
                )
        
    def QTW_iso_dict(self, obj):
        return dict(              
            dati = {'obj': obj.iso__tabel, 'col_order': ['certificazione', 'data', 'stato', 'tipo', 'ente', 'consulenza', 'consulenzaIva', 'incassoConsulente', 'fatturatoConsulenza', 'incassoEnte', 'provvEnte']},
            costiIso9001 = {'obj': obj.iso__costi9001, 'col_order': ['consulenza', 'ente', 'scadenza', 'consulente'], 'dfix': 3},
            costiIso14001 = {'obj': obj.iso__costi14001, 'col_order': ['consulenza', 'ente','scadenza', 'consulente'], 'dfix': 3},
            costiIso18001 = {'obj': obj.iso__costi18001, 'col_order': ['consulenza', 'ente','scadenza', 'consulente'], 'dfix': 3},
            )

    def QTB_iso_dict(self, obj):
        return(dict(iso_note = obj.iso__note))
    
    def QLE_iso_dict(self, obj):
        return dict(
        ente9001 = obj.iso__ente_9001,
        ente14001 = obj.iso__ente_14001, 
        ente18001 = obj.iso__ente_18001 
        )


class dbMap_main:
    def QTW_soa_dict(self, obj):
        return {'obj': obj.tbl_soa_main, 'col_order': ['id', 'ragioneSociale', 'l_prov', 'l_comune', 'scadenza_gma', 'tipo', 'stato', 'riferimenti']}

    def QTW_soa_pr_dict(self):
        return {'col_name': ['id', 'Ragione Sociale', 'CF', 'Provincia', 'Comune', 'Scadenza', 'Tipo', 'Stato', 'Riferimenti'],
                'col_order': ['id', 'ragioneSociale', 'codFisc', 'l_prov', 'l_comune', 'scadenza_gma', 'tipo', 'stato', 'riferimenti'],
                'title': "Gestione Imprese - SOA"}

    def QTW_iso_dict(self, obj):
        return {'obj': obj.tbl_iso_main, 'col_order': ['id', 'ragioneSociale', 'l_prov', 'l_comune', 
                                                       'scadenzaAnnuale_9001', 'scadenzaFinale_9001', 'ente_9001', 
                                                       'scadenzaAnnuale_14001', 'scadenzaFinale_14001', 'ente_14001', 
                                                       'scadenzaAnnuale_18001', 'scadenzaFinale_18001', 'ente_18001', 
                                                       ]}
    
    def QTW_iso_pr_dict(self):
        return {'col_name': ['id', 'Ragione Sociale', 'Provincia', 'Comune', 
                                                       'Ann9001', 'Fin9001', 'ente 9001', 
                                                       'Ann14001', 'Fin14001', 'ente 14001', 
                                                       'Ann18001', 'Fin18001', 'ente 18001', 
                                                       ],
                'col_order': ['id', 'ragioneSociale', 'l_prov', 'l_comune', 
                                                       'scadenzaAnnuale_9001', 'scadenzaFinale_9001', 'ente_9001', 
                                                       'scadenzaAnnuale_14001', 'scadenzaFinale_14001', 'ente_14001', 
                                                       'scadenzaAnnuale_18001', 'scadenzaFinale_18001', 'ente_18001', 
                                                       ],
                'title': "Gestione Imprese - ISO"}
#%%
