from datetime import date

from sap_gui_engine.objects import GuiSession


def test_va01_transaction(session: GuiSession):
    session.start_transaction("va01")

    session.find_by_id("wnd[0]/usr/ctxtVBAK-AUART").set_text("ZWEO", set_focus=True)
    session.find_by_id("wnd[0]/usr/ctxtVBAK-VKORG").set_text("2200", set_focus=True)
    session.find_by_id("wnd[0]/usr/ctxtVBAK-VTWEG").set_text("10", set_focus=True)
    session.find_by_id("wnd[0]/usr/ctxtVBAK-SPART").set_text("00", set_focus=True)

    session.press_enter()
    session.find_by_id(
        "wnd[0]/usr/subSUBSCREEN_HEADER:SAPMV45A:4021/subPART-SUB:SAPMV45A:4701/ctxtKUAGV-KUNNR"
    ).set_text(
        "102016",
        set_focus=True,
    )
    session.find_by_id(
        "wnd[0]/usr/subSUBSCREEN_HEADER:SAPMV45A:4021/subPART-SUB:SAPMV45A:4701/ctxtKUWEV-KUNNR",
    ).set_text(
        "102016",
        set_focus=True,
    )

    session.find_by_id(
        "wnd[0]/usr/subSUBSCREEN_HEADER:SAPMV45A:4021/ctxtVBKD-BSTDK"
    ).set_text(
        date.today(),
        set_focus=True,
    )

    session.find_by_id(
        "wnd[0]/usr/subSUBSCREEN_HEADER:SAPMV45A:4021/txtVBKD-BSTKD"
    ).set_text(
        "TBC",
        set_focus=True,
    )

    session.press_enter()
