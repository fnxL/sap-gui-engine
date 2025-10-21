from sap_gui_engine import SAPGuiEngine
from datetime import datetime, timezone
from pathlib import Path
import polars as pl


def test_fill_table(sap: SAPGuiEngine):
    df_path = Path("tests/data/fill_table.xlsx")
    if not df_path.exists():
        return True  # Skip test if file does not exist

    df = pl.read_excel(df_path)
    sap.start_transaction(tcode="va01")
    sap.findById("wnd[0]/usr/ctxtVBAK-AUART").text = "ZWEO"
    sap.findById("wnd[0]/usr/ctxtVBAK-VKORG").text = "2200"
    sap.findById("wnd[0]/usr/ctxtVBAK-VTWEG").text = "10"
    sap.findById("wnd[0]/usr/ctxtVBAK-SPART").text = "00"
    sap.send_enter()
    sap.findById(
        "wnd[0]/usr/subSUBSCREEN_HEADER:SAPMV45A:4021/subPART-SUB:SAPMV45A:4701/ctxtKUAGV-KUNNR"
    ).text = "102380"
    sap.findById(
        "wnd[0]/usr/subSUBSCREEN_HEADER:SAPMV45A:4021/subPART-SUB:SAPMV45A:4701/ctxtKUWEV-KUNNR"
    ).text = "102172"
    sap.findById(
        "wnd[0]/usr/subSUBSCREEN_HEADER:SAPMV45A:4021/ctxtVBKD-BSTDK"
    ).text = datetime.now(timezone.utc).strftime("%d.%m.%Y")
    sap.send_enter()
    sap.findById("wnd[0]/usr/tabsTAXI_TABSTRIP_OVERVIEW/tabpT\\08").click()
    sap.findById(
        r"wnd[0]/usr/tabsTAXI_TABSTRIP_OVERVIEW/tabpT\08/ssubSUBSCREEN_BODY:SAPMV45A:7901/cmbRV45A-MUEBS"
    ).text = "Towel - Vapi"
    sap.fill_table(
        r"wnd[0]/usr/tabsTAXI_TABSTRIP_OVERVIEW/tabpT\08/ssubSUBSCREEN_BODY:SAPMV45A:7901/subSUBSCREEN_TC:SAPMV45A:7905/tblSAPMV45ATCTRL_U_MILL_SE_KONFIG",
        df,
    )
    items_list = []
    for row in sap.findById(
        r"wnd[0]/usr/tabsTAXI_TABSTRIP_OVERVIEW/tabpT\08/ssubSUBSCREEN_BODY:SAPMV45A:7901/subSUBSCREEN_TC:SAPMV45A:7905/tblSAPMV45ATCTRL_U_MILL_SE_KONFIG"
    ).element.rows:
        items_list.append(str(row.Item(0).text).strip().lower())

    assert "0300" in items_list
