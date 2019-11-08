from fastapi import FastAPI, File
from gi_sql import viewIso, viewSoa, newImpresa, viewAllDetail, rmImpresa, updateImpresa, searchSoa, searchIso, staticList
from pydantic import BaseModel

app = FastAPI()

class UpdateImpresaStruct(BaseModel):
    imp: dict
    soa: dict
    iso: dict

class SearchSoaStruct(BaseModel):
    ragione_sociale: str = None
    cf: str = None
    idImpresa: int = None
    
    stato: str = None
    riferimenti: str = None
    categoria: str = None
    
    prov: str = None
    comune: str = None
    classifica: str = None
    
    da: str = None
    a: str = None
    
class SearchIsoStruct(BaseModel):
    ragione_sociale: str = None
    cf: str = None
    idImpresa: int = None
    
    stato: str = None
    riferimenti: str = None
    prov: str = None

    
@app.get("/viewAllDetail")
async def view_all_detail(id_impresa: int):
    return viewAllDetail(id_impresa)

@app.get("/newImpresa")
async def new_impresa():
    return newImpresa()

@app.get("/rmImpresa")
async def rm_impresa(id_impresa: int):
    return rmImpresa(id_impresa)

@app.post("/updateImpresa")
async def update_impresa(id_impresa: int, item: UpdateImpresaStruct):
    return updateImpresa(id_impresa, item.imp, item.soa, item.iso)

@app.post("/searchSoa")
async def search_soa(item: SearchSoaStruct):
    return searchSoa(item)

@app.post("/searchIso")
async def search_iso(item: SearchIsoStruct):
    return searchIso(item)

@app.get("/staticList")
async def static_list():
    return staticList()




'''
# Obsolete
@app.get("/listIso")
async def list_ISO():
    """
    Lista delle imprese
    """
    return viewIso()

@app.get("/listSoa")
async def list_ISO():
    """
    Lista delle imprese
    """
    return viewSoa()


@app.get("/download")
async def download():
    """
    Lista delle imprese
    """
    with open('download/termometro.png', 'rb') as f:
        #return File(f.read())
        return File('download/termometro.png')



@app.get("/searchImprese")
async def search_imprese(ragione_sociale: str = None, cf: str = None, id: int = None, comune: str = None,
                         prov: str = None):
    """
    Cerca un'impresa
    """
    wc = ' WHERE 1=1 ' # where cond
    wcp = []
    if ragione_sociale is not None:
        wc += "AND ragioneSociale LIKE ? "
        wcp.append(f'%{ragione_sociale}%')
    if cf is not None:
        wc += "AND UPPER(codFisc) LIKE UPPER(?) "
        wcp.append(f'%{cf}%')
    if id is not None:
        wc += "AND id = ? "
        wcp.append(id)
    if comune is not None:
        wc += "AND (UPPER(l_comune) = UPPER(?) OR UPPER(o_comune) = UPPER(?)) "
        wcp.append(comune)
        wcp.append(comune)
    if prov is not None:
        wc += "AND (UPPER(l_prov) = UPPER(?) OR UPPER(o_prov) = UPPER(?)) "
        wcp.append(prov)
        wcp.append(prov)

    return viewImprese(wc, wcp)
'''