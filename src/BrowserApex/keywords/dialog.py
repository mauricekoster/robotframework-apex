from Browser import AssertionOperator
from robot.libraries.BuiltIn import BuiltIn
from Browser.utils import PageLoadStates, logger
from robot.api.deco import keyword, not_keyword
from ..librarycomponent import LibraryComponent


class Dialog(LibraryComponent):
    """
    Handling of Dialogs.
    """
    def __init__(self, library):
        super().__init__(library)

        self.library.locators.update({
            'dialog_container': "//div[@role='dialog]",
            'dialog_button': "//button/span[contains(text(),'##TEXT##')]",
        })

    @keyword(tags=('Apex', 'Dialog'))
    def dialog_button(self, button):
        """
        Click the button within the dialog button region.
        """
        logger.info(f"Pressing button with text '{button}' in dialog")

        container = self.library.get_locator('dialog_container') 
        btn_locator = self.library.get_locator('dialog_button', {'##TEXT##': button}) 

        self.library.click(f"{container} >> {btn_locator}")
        self.library.wait_for_load_state(PageLoadStates.networkidle, 10)
        self.library.wait_for_load_state(PageLoadStates.domcontentloaded, 1)