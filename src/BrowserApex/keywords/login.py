from Browser import AssertionOperator
from robot.libraries.BuiltIn import BuiltIn
from Browser.utils import PageLoadStates, logger
from robot.api.deco import keyword, not_keyword
from ..librarycomponent import LibraryComponent


class LoginTemplate(LibraryComponent):
    """
    Handling of regions with page template 'Login'.
    """
    def __init__(self, library):
        super().__init__(library)

        self.library.locators.update({
            'login_container': ".t-Login-region",
            'login_button': "//button/span[contains(text(),'##TEXT##')]",
        })

    @not_keyword
    def _check_container_visible(self, container):
        try:
            element = self.library.get_element(container)
            self.library.get_element_states(element, AssertionOperator.contains, 'visible')
        except:
            raise AssertionError(f"Login not avaiable or visible")
    
    # Template: Login
    @keyword(tags=('Apex', 'Login'))
    def login_fill(self, field_definition, data):
        container = self.library.get_locator('login_container')

        self._check_container_visible(container)
        self.library.check_data_in_definition('Login', field_definition, data)
        self.library.fill_fields(container, field_definition, data)

    @keyword(tags=('Apex', 'Login'))
    def login_button(self, button_text):
        container = self.library.get_locator('login_container')
        self.library.check_container_visible('Login', container)
        locator = self.library.get_locator('login_button', {'##TEXT##': button_text})

        self.library.click(f"{container} >> {locator}")
        self.library.wait_for_load_state(PageLoadStates.networkidle, 10)
        self.library.wait_for_load_state(PageLoadStates.domcontentloaded, 1)