from Browser import AssertionOperator
from robot.libraries.BuiltIn import BuiltIn
from Browser.utils import PageLoadStates, logger
from robot.api.deco import keyword, not_keyword
from ..librarycomponent import LibraryComponent


class Region(LibraryComponent):
    """
    Handling of Regions. By default of type 'Static Content'.

    Specialized regions have there own LibraryComponent (e.g. Classic Report)
    """
    def __init__(self, library):
        super().__init__(library)

        self.library.locators.update({
            'region': "//div[@role='region' and @aria-label='##NAME##']",
            'region_id': "#R##ID##",
            'region_button': "//button/span[contains(text(),'##TEXT##')]"
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

    @not_keyword
    def _get_region_name(self, locator):
        attrs = self.library.get_attribute_names(locator)
        if 'aria-label' in attrs:
            region_name = self.library.get_attribute(locator, 'aria-label')
        elif 'data-label' in attrs:
            region_name = self.library.get_attribute(locator, 'data-label')
        else:
            region_name = '<Unknown>'
        return region_name
    

    @keyword(tags=('Apex', 'Region'))
    def select_region(self, region, parent=None):
        if parent:
            locator = self.library.get_element(f"{parent} >> {self._get_region_locator(region)}")
        else:
            locator = self.library.get_element(f"{self._get_region_locator(region)}")

        self._check_region_visible(region, locator)
        return locator

    @keyword(tags=('Apex', 'Region'))
    def select_region_by_id(self, region_id, parent=None):
        region_locator = self.library.get_locator('region_id', {'##ID##': region_id}, 'id')  
        if parent:
            locator = self.library.get_element(f"{parent} >> {region_locator}")
        else:
            locator = self.library.get_element(f"{region_locator}")

        self._check_region_visible(region_id, locator)
        return locator

    @keyword(tags=('Apex', 'Region'))
    def region_fill(self, locator, field_definition, data):
        """
        Fills the fields inside the region.
        """
        region_name = self._get_region_name(locator)

        self.library.check_data_in_definition(region_name, field_definition, data)
        self.library.fill_fields(locator, field_definition, data)


    @keyword(tags=('Apex', 'Region'))
    def region_check(self, locator, field_definition, data):
        """
        Check the fields inside the region.
        """
        region_name = self._get_region_name(locator)
        self.library.check_data_in_definition(region_name, field_definition, data)
        self.library.check_fields(locator, field_definition, data)

    @keyword(tags=('Apex', 'Region'))
    def region_button(self, locator, button):
        """
        Click the button within the given region locator.
        """
        region_name = self._get_region_name(locator)
        logger.info(f"Pressing button with text '{button}' in region '{region_name}'")

        btn_locator = self.library.get_locator('region_button', {'##TEXT##': button}) 

        self.library.click(f"{locator} >> {btn_locator}")
        self.library.wait_for_load_state(PageLoadStates.networkidle, 10)
        self.library.wait_for_load_state(PageLoadStates.domcontentloaded, 1)

    @keyword(tags=('Apex', 'Region'))
    def region_get_value(self, locator, field_definition, field_name):
        """
        Get the value of the field inside the region.
        """
        region_name = self._get_region_name(locator)
        if field_name not in field_definition:
            raise AttributeError(f"*WARN* Field '{field_name}' not in definition of region '{region_name}'")
        
        value = self.library.get_field_value(locator, field_definition, field_name)
        
        return value