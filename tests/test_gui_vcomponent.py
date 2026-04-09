from datetime import date

import pytest

from sap_gui_engine import GuiSession
from sap_gui_engine.exceptions import SAPElementNotChangeable


def test_constructor(session: GuiSession):
    session.start_transaction(tcode="va01")
    # Sales Organization label id
    element = session.find_by_id("wnd[0]/usr/lblVBAK-VKORG")
    assert element.name == "VBAK-VKORG"
    assert element.type == "GuiLabel"
    assert element.text == "Sales Organization"
    assert element.changeable is False


def test_set_text_non_changeable(session: GuiSession):
    session.find_by_id("wnd[0]/usr/ctxtVBAK-AUART").text = "ZWEO"
    session.find_by_id("wnd[0]/usr/ctxtVBAK-VKORG").text = "2200"
    session.find_by_id("wnd[0]/usr/ctxtVBAK-VTWEG").text = "10"
    session.find_by_id("wnd[0]/usr/ctxtVBAK-SPART").text = "00"
    session.press_enter()

    # Get the unchangeable text field
    element = session.find_by_id(
        "wnd[0]/usr/subSUBSCREEN_HEADER:SAPMV45A:4021/txtVBAK-NETWR"
    )

    assert element.type == "GuiTextField"
    assert element.changeable is False
    # Try to set the text field
    with pytest.raises(SAPElementNotChangeable, match="not changeable"):
        element.set_text(
            "new value",
            raise_error=False,
        )


def test_click_button(session: GuiSession):
    assert session.find_by_id("wnd[0]/tbar[0]/btn[15]").click() is True
    session.start_transaction(tcode="va01")
    session.press_enter()


def test_set_text_field(session: GuiSession):
    element = session.find_by_id(
        "wnd[0]/usr/subSUBSCREEN_HEADER:SAPMV45A:4021/subPART-SUB:SAPMV45A:4701/ctxtKUAGV-KUNNR"
    )
    element.text = "102133"

    # Refresh element
    element = session.find_by_id(
        "wnd[0]/usr/subSUBSCREEN_HEADER:SAPMV45A:4021/subPART-SUB:SAPMV45A:4701/ctxtKUAGV-KUNNR"
    )
    assert element.text == "102133"
    assert element.type == "GuiCTextField"


def test_set_text_combobox(session: GuiSession):
    # Billing block
    element = session.find_by_id(
        "wnd[0]/usr/tabsTAXI_TABSTRIP_OVERVIEW/tabpT\\01/ssubSUBSCREEN_BODY:SAPMV45A:4400/ssubHEADER_FRAME:SAPMV45A:4440/cmbVBAK-FAKSK"
    )
    element.text = "Calculation Missing"
    assert element.type == "GuiComboBox"

    # Refresh element
    element = session.find_by_id(
        "wnd[0]/usr/tabsTAXI_TABSTRIP_OVERVIEW/tabpT\\01/ssubSUBSCREEN_BODY:SAPMV45A:4400/ssubHEADER_FRAME:SAPMV45A:4440/cmbVBAK-FAKSK"
    )
    assert element.text == "Calculation Missing"
    assert element.type == "GuiComboBox"


def test_click_tab(session: GuiSession):
    # Set PO date
    session.find_by_id(
        "wnd[0]/usr/subSUBSCREEN_HEADER:SAPMV45A:4021/ctxtVBKD-BSTDK"
    ).text = date.today().strftime("%d.%m.%Y")

    # Set PO number
    session.find_by_id(
        "wnd[0]/usr/subSUBSCREEN_HEADER:SAPMV45A:4021/txtVBKD-BSTKD"
    ).text = "PO123456"

    # Click Item Overview Tab
    assert (
        session.find_by_id("wnd[0]/usr/tabsTAXI_TABSTRIP_OVERVIEW/tabpT\\02").click()
        is True
    )


def test_click_radio_button(session: GuiSession):
    session.start_transaction(tcode="zsd_so_report")
    # Select Close Sales Order Radio Button
    assert session.find_by_id("wnd[0]/usr/radC2").click() is True


def test_click_checkbox(session: GuiSession):
    session.start_transaction(tcode="se16n")
    session.find_by_id("wnd[0]/usr/ctxtGD-TAB").text = "VBAK"
    session.press_enter()

    # Click Checkbox
    session.find_by_id(
        "wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC/chkGS_SELFIELDS-MARK[5,1]"
    ).click()

    checkbox = session.find_by_id(
        "wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC/chkGS_SELFIELDS-MARK[5,1]"
    ).get_checkbox_state()

    assert checkbox is True
