from Browser import AssertionOperator
from robot.libraries.BuiltIn import BuiltIn
from robot.api import logger
from robot.api.deco import keyword, not_keyword
from ..librarycomponent import LibraryComponent


class Region(LibraryComponent):

    def __init__(self, library):
        super().__init__(library)

        self.library.locators.update({
            'region': "//div[@role='region' and @aria-label='##NAME##']"
        })

    @not_keyword
    def _get_region_locator(self, region):
        if type(region) is str:
            region_name = region
        else:
            if 'name' in region:
                region_name = region['name']
            else:
                raise AttributeError("No name in region")

        return self.library.get_locator('region', {'##NAME##': region_name}, 'id')    

    @not_keyword
    def _check_region_visible(self, region, locator):
        try:
            element = self.library.get_element(f"{locator}")
            self.library.get_element_states(element, AssertionOperator.contains, 'visible')
        except:
            raise AssertionError(f"Region '{region}' not avaiable or visible")

    @keyword
    def select_region(self, region, parent=None):
        if parent:
            locator = self.library.get_element(f"{parent} >> {self._get_region_locator(region)}")
        else:
            locator = self.library.get_element(f"{self._get_region_locator(region)}")

        self._check_region_visible(region, locator)
        return locator

    @keyword
    def region_fill(self, locator, field_definition, data):
        region_name = self.library.get_attribute(locator, 'aria-label')
        self.library.check_data_in_definition(region_name, field_definition, data)
        self.library.fill_fields_new(locator, field_definition, data)