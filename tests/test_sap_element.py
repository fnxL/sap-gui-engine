from sap_gui_engine import SAPGuiEngine, VKey

def test_constructor(engine: SAPGuiEngine):
    engine.start_transaction(tcode="va01")
    # Sales Organization label id
    element = engine.findById("wnd[0]/usr/lblVBAK-VKORG")
    assert element.name == "VBAK-VKORG"
    assert element.type == "GuiLabel"
    assert element.text == "Sales Organization"
    assert element.changeable is False


def test_set_text_non_changeable(engine: SAPGuiEngine, caplog):
    engine.findById("wnd[0]/usr/ctxtVBAK-AUART").set_text("ZWEO")
    engine.findById("wnd[0]/usr/ctxtVBAK-VKORG").set_text("2200")
    engine.findById("wnd[0]/usr/ctxtVBAK-VTWEG").set_text("10")
    engine.findById("wnd[0]/usr/ctxtVBAK-SPART").set_text("00")
    engine.sendVKey(VKey.ENTER)

    element = engine.findById("wnd[0]/usr/subSUBSCREEN_HEADER:SAPMV45A:4021/txtVBAK-NETWR")

    assert element.type == "GuiTextField"
    assert element.changeable is False
    result = element.set_text("new value")
    assert result is False

def test_set_text_field(engine: SAPGuiEngine):
    element = engine.findById("wnd[0]/usr/subSUBSCREEN_HEADER:SAPMV45A:4021/subPART-SUB:SAPMV45A:4701/ctxtKUAGV-KUNNR")
    result = element.set_text("102133")
    assert result is True
    sap_element_value = engine.findById("wnd[0]/usr/subSUBSCREEN_HEADER:SAPMV45A:4021/subPART-SUB:SAPMV45A:4701/ctxtKUAGV-KUNNR").get_text()
    assert sap_element_value == "102133"
    assert element.type == "GuiCTextField"

