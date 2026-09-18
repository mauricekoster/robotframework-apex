from Browser import AssertionOperator
from robot.libraries.BuiltIn import BuiltIn
from Browser.utils import PageLoadStates, logger, ElementState
from robot.api.deco import keyword, not_keyword
from ..librarycomponent import LibraryComponent


class Dialog(LibraryComponent):
    """
    Handling of Dialogs.
    """
    def __init__(self, library):
        super().__init__(library)

        self.library.locators.update({
            'dialog_container': "xpath=//div[@role='dialog']",
            'dialog_container_by_title': "xpath=//div[@role='dialog' and @aria-label='##TITLE##']",
            #'dialog_container': "css=.ui-dialog--apex",
            'dialog_button': "xpath=//button/span[contains(text(),'##TEXT##')]",
            'dialog_close_button': "xpath=//button[contains(@class, 'ui-dialog-titlebar-close')]",
        })

    @keyword(tags=('Apex', 'Dialog'))
    def select_dialog(self, title, parent=None):
        container = self.library.get_locator('dialog_container_by_title', {'##TITLE##': title}) 
        if parent:
            container = f"{parent} >> {container}"
        self.library.wait_for_elements_state(container, ElementState.visible)
        return container

    @keyword(tags=('Apex', 'Dialog'))
    def dialog_button(self, button):
        """
        Click the button within the dialog button region.
        """
        logger.info(f"Pressing button with text '{button}' in dialog")

        container = self.library.get_locator('dialog_container') 
        btn_locator = self.library.get_locator('dialog_button', {'##TEXT##': button}) 

        btn = f"{container} >> {btn_locator}"
        self.library.wait_for_elements_state(btn, ElementState.visible)

        self.library.click(btn)
        self.library.wait_for_load_state(PageLoadStates.networkidle, 10)
        self.library.wait_for_load_state(PageLoadStates.domcontentloaded, 1)

    @keyword(tags=('Apex', 'Dialog'))
    def dialog_close(self):
        """
        Click the top-right close button of the dialog.
        """
        logger.info(f"Pressing the dialog close button.")


        container = self.library.get_locator('dialog_container') 
        btn_locator = self.library.get_locator('dialog_close_button') 

        old_prefix = self.library.set_selector_prefix(None)
        btn = f"{container} >> {btn_locator}"
        # self.library.wait_for_elements_state(btn, ElementState.visible)

        self.library.click(btn)
        self.library.wait_for_load_state(PageLoadStates.networkidle, 10)
        self.library.wait_for_load_state(PageLoadStates.domcontentloaded, 1)
        self.library.set_selector_prefix(old_prefix)