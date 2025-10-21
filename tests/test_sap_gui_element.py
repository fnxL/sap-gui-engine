from sap_gui_engine import SAPGuiEngine, VKey
from datetime import datetime, timezone


def test_constructor(sap: SAPGuiEngine):
    sap.start_transaction(tcode="va01")
    # Sales Organization label id
    element = sap.findById("wnd[0]/usr/lblVBAK-VKORG")
    assert element.name == "VBAK-VKORG"
    assert element.type == "GuiLabel"
    assert element.text == "Sales Organization"
    assert element.changeable is False


def test_set_text_non_changeable(sap: SAPGuiEngine):
    sap.findById("wnd[0]/usr/ctxtVBAK-AUART").text = "ZWEO"
    sap.findById("wnd[0]/usr/ctxtVBAK-VKORG").text = "2200"
    sap.findById("wnd[0]/usr/ctxtVBAK-VTWEG").text = "10"
    sap.findById("wnd[0]/usr/ctxtVBAK-SPART").text = "00"
    sap.sendVKey(VKey.ENTER)

    # Get the unchangeable text field
    element = sap.findById("wnd[0]/usr/subSUBSCREEN_HEADER:SAPMV45A:4021/txtVBAK-NETWR")

    assert element.type == "GuiTextField"
    assert element.changeable is False
    # Try to set the text field
    element.text = "new value"

    # Refresh element
    element = sap.findById("wnd[0]/usr/subSUBSCREEN_HEADER:SAPMV45A:4021/txtVBAK-NETWR")
    assert element.text != "new value"


def test_click_button(sap: SAPGuiEngine):
    assert sap.findById("wnd[0]/tbar[0]/btn[15]").click() is True
    sap.start_transaction(tcode="va01")
    sap.sendVKey(VKey.ENTER)


def test_set_text_field(sap: SAPGuiEngine):
    element = sap.findById(
        "wnd[0]/usr/subSUBSCREEN_HEADER:SAPMV45A:4021/subPART-SUB:SAPMV45A:4701/ctxtKUAGV-KUNNR"
    )
    element.text = "102133"

    # Refresh element
    element = sap.findById(
        "wnd[0]/usr/subSUBSCREEN_HEADER:SAPMV45A:4021/subPART-SUB:SAPMV45A:4701/ctxtKUAGV-KUNNR"
    )
    assert element.text == "102133"
    assert element.type == "GuiCTextField"


def test_set_text_combobox(sap: SAPGuiEngine):
    # Billing block
    element = sap.findById(
        "wnd[0]/usr/tabsTAXI_TABSTRIP_OVERVIEW/tabpT\\01/ssubSUBSCREEN_BODY:SAPMV45A:4400/ssubHEADER_FRAME:SAPMV45A:4440/cmbVBAK-FAKSK"
    )
    element.text = "Calculation Missing"
    assert element.type == "GuiComboBox"

    # Refresh element
    element = sap.findById(
        "wnd[0]/usr/tabsTAXI_TABSTRIP_OVERVIEW/tabpT\\01/ssubSUBSCREEN_BODY:SAPMV45A:4400/ssubHEADER_FRAME:SAPMV45A:4440/cmbVBAK-FAKSK"
    )
    assert element.text == "Calculation Missing"
    assert element.type == "GuiComboBox"


def test_click_tab(sap: SAPGuiEngine):
    # Set PO date
    sap.findById(
        "wnd[0]/usr/subSUBSCREEN_HEADER:SAPMV45A:4021/ctxtVBKD-BSTDK"
    ).text = datetime.now(timezone.utc).strftime("%d.%m.%Y")

    # Set PO number
    sap.findById(
        "wnd[0]/usr/subSUBSCREEN_HEADER:SAPMV45A:4021/txtVBKD-BSTKD"
    ).text = "PO123456"

    # Click Item Overview Tab
    assert (
        sap.findById("wnd[0]/usr/tabsTAXI_TABSTRIP_OVERVIEW/tabpT\\02").click() is True
    )


def test_click_radio_button(sap: SAPGuiEngine):
    sap.start_transaction(tcode="zsd_so_report")
    # Select Close Sales Order Radio Button
    assert sap.findById("wnd[0]/usr/radC2").click() is True


def test_click_checkbox(sap: SAPGuiEngine):
    sap.start_transaction(tcode="se16n")
    sap.findById("wnd[0]/usr/ctxtGD-TAB").text = "VBAK"
    sap.sendVKey(VKey.ENTER)
    # Select Close Sales Order Radio Button
    assert (
        sap.findById(
            "wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC/chkGS_SELFIELDS-MARK[5,1]"
        ).click()
        is True
    )
