from sap_gui_engine import SAPGuiEngine, VKey

def test_constructor(sap: SAPGuiEngine):
    sap.start_transaction(tcode="va01")
    # Sales Organization label id
    element = sap.findById("wnd[0]/usr/lblVBAK-VKORG")
    assert element.name == "VBAK-VKORG"
    assert element.type == "GuiLabel"
    assert element.text == "Sales Organization"
    assert element.changeable is False


def test_set_text_non_changeable(sap: SAPGuiEngine):
    sap.findById("wnd[0]/usr/ctxtVBAK-AUART").set_text("ZWEO")
    sap.findById("wnd[0]/usr/ctxtVBAK-VKORG").set_text("2200")
    sap.findById("wnd[0]/usr/ctxtVBAK-VTWEG").set_text("10")
    sap.findById("wnd[0]/usr/ctxtVBAK-SPART").set_text("00")
    sap.sendVKey(VKey.ENTER)

    element = sap.findById("wnd[0]/usr/subSUBSCREEN_HEADER:SAPMV45A:4021/txtVBAK-NETWR")

    assert element.type == "GuiTextField"
    assert element.changeable is False
    result = element.set_text("new value")
    assert result is False

def test_set_text_field(sap: SAPGuiEngine):
    element = sap.findById("wnd[0]/usr/subSUBSCREEN_HEADER:SAPMV45A:4021/subPART-SUB:SAPMV45A:4701/ctxtKUAGV-KUNNR")
    result = element.set_text("102133")
    assert result is True
    sap_element_value = sap.findById("wnd[0]/usr/subSUBSCREEN_HEADER:SAPMV45A:4021/subPART-SUB:SAPMV45A:4701/ctxtKUAGV-KUNNR").get_text()
    assert sap_element_value == "102133"
    assert element.type == "GuiCTextField"

def test_set_text_combobox(sap: SAPGuiEngine):
    # Billing block
    element = sap.findById("wnd[0]/usr/tabsTAXI_TABSTRIP_OVERVIEW/tabpT\\01/ssubSUBSCREEN_BODY:SAPMV45A:4400/ssubHEADER_FRAME:SAPMV45A:4440/cmbVBAK-FAKSK")
    result = element.set_text("Calculation Missing")
    assert result is True

    refresh_element = sap.findById("wnd[0]/usr/tabsTAXI_TABSTRIP_OVERVIEW/tabpT\\01/ssubSUBSCREEN_BODY:SAPMV45A:4400/ssubHEADER_FRAME:SAPMV45A:4440/cmbVBAK-FAKSK")
    assert refresh_element.get_text() == "Calculation Missing"
