from Browser import AssertionOperator
from robot.libraries.BuiltIn import BuiltIn
from robot.api.deco import keyword, not_keyword
from ..librarycomponent import LibraryComponent
from Browser.utils import PageLoadStates, logger

class Tab(LibraryComponent):

    def __init__(self, library):
        super().__init__(library)
        self.library.locators.update({
            'tab_header': "xpath=//a[span[text()='##NAME##']]/..",
            'tab_container': "xpath=//div[@data-label='##NAME##']",
            'tab_panel': "xpath=//div[@role='tabpanel' and @data-label='##NAME##']",
        })

    @not_keyword
    def _get_tab_locator(self, tab):
        if type(tab) is str:
            tab_name = tab
        else:
            if 'name' in tab:
                tab_name = tab['name']
            else:
                raise AttributeError("No name in tab")

        return self.library.get_locator('tab_header', {'##NAME##': tab_name})    

    @not_keyword
    def _check_tab_visible(self, tab, locator):
        try:
            element = self.library.get_element(f"{locator}")
            self.library.get_element_states(element, AssertionOperator.contains, 'visible')
        except:
            raise AssertionError(f"Tab '{tab}' not avaiable or visible")

    @keyword(tags=('Apex', 'Tabs'))
    def select_tab(self, tab_name, parent=None):
        """
        Find the tab inside the parent container and select (click) the tab header.
        Returns the tabpanel.
        """
        if parent:
            locator = self.library.get_element(f"{parent} >> {self._get_tab_locator(tab_name)}")
        else:
            locator = self.library.get_element(f"{self._get_tab_locator(tab_name)}")

        self._check_tab_visible(tab_name, locator)

        # Click the header
        self.library.click(locator)
        self.library.wait_for_load_state(PageLoadStates.networkidle, 10)
        self.library.wait_for_load_state(PageLoadStates.domcontentloaded, 1)

        panel = self.library.get_locator('tab_panel', {'##NAME##': tab_name}) 
        if parent:
            locator = f"{parent} >> {panel}"
        else:
            locator = f"{panel}"
        return locator