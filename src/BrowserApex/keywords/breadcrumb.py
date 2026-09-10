from Browser import AssertionOperator
from robot.libraries.BuiltIn import BuiltIn
from Browser.utils import PageLoadStates, logger
from robot.api.deco import keyword, not_keyword
from ..librarycomponent import LibraryComponent


class Breadcrumb(LibraryComponent):
    """
    Handling of Breadcrumb.
    """
    def __init__(self, library):
        super().__init__(library)

        self.library.locators.update({
            'breadcrumb_container': "css=.t-BreadcrumbRegion",
            'breadcrumb_button': "xpath=//button/span[contains(text(),'##TEXT##')]",
        })

    @keyword(tags=('Apex', 'Breadcrumb'))
    def breadcrumb_button(self, button):
        """
        Click the button within the breadcrumb button region.
        """
        logger.info(f"Pressing button with text '{button}' in breadcrumb")

        container = self.library.get_locator('breadcrumb_container') 
        btn_locator = self.library.get_locator('breadcrumb_button', {'##TEXT##': button}) 

        self.library.click(f"{container} >> {btn_locator}")
        self.library.wait_for_load_state(PageLoadStates.networkidle, 10)
        self.library.wait_for_load_state(PageLoadStates.domcontentloaded, 1)