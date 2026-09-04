"""
Oracle APEX support
"""

from robot.api import FatalError
from robot.libraries.BuiltIn import BuiltIn
from robot.api.deco import keyword, not_keyword, library
from Browser import AssertionOperator, SelectAttribute, ElementState, Browser
from Browser.utils import PageLoadStates

from .keywords import FieldCommand


selector_prefix = {
    '/': 'xpath', 
    '.': 'css', 
    '#': 'id'
    }

@library(scope='GLOBAL', auto_keywords=True)
class BrowserApex(Browser):
    def __init__(self, **kwargs):
        Browser.__init__(self, **kwargs)

        self._field_commands = FieldCommand(self)
        
        self.add_library_components([
            self._field_commands
        ])
        
        self.container = None
        self.classic_report_row = None

        self.field_input_callbacks = {
            'TextField': self.fill_text_field,
            'NumberField': self.fill_number_field,
            'Password': self.fill_password_field,
            'SelectList': self.fill_select_field,
            'RadioGroup': self.fill_radio_group,
            'DatePicker': self.fill_date_picker,
            'PopupLOV': self.fill_popup_lov,
        }
        self.field_get_callbacks = {
            'Hidden': self.get_value_hidden,
            'DisplayOnly': self.get_value_displayonly
        }
        self.field_check_callbacks = {
            'DisplayOnly': self.check_display_only,
            'TextField': self.check_text_field,
            'SelectList': self.check_select_list,
            'DatePicker': self.check_date_picker,
        }
        

        self.cell_check_callbacks = {
            'PlainText': self.check_cell_plaintext
        }

        self.locators = {
            'login_container': ".t-Login-region",
            'login_button': "//button/span[contains(text(),'##TEXT##')]",
            'block_container': "//div[@aria-label='##TEXT##']",
            'block_button': "//button/span[contains(text(),'##TEXT##')]",
            'page_button': "//button/span[contains(text(),'##TEXT##')]",
            'wizard_button': "//button/span[contains(text(),'##TEXT##')]",
            'tab_button': "//button/span[contains(text(),'##TEXT##')]",
        }


    

    @not_keyword
    def check_container_visible(self, container_name, container):
        try:
            container_prefix = selector_prefix.get(container[0],'id')
            element = self.get_element(f"{container_prefix}={container}")
            self.get_element_states(element, AssertionOperator.contains, 'visible')
        except:
            raise AssertionError(f"Container '{container_name}' not avaiable or visible")
        
    @not_keyword
    def check_data_in_definition(self, block_name, field_definition, data):
        fail_missing = BuiltIn().get_variable_value("${fail_missing_field_definition}", False)
        nr_def_missing = 0
        for key, _ in data.items():
            if key not in field_definition:
                nr_def_missing += 1
                print(f"*WARN* Data field '{key}' not found in definition of block '{block_name}'" )

        if fail_missing and nr_def_missing > 0:
            raise FatalError(f"Missing definitions (count: {nr_def_missing}) in block '{block_name}'. See warnings." )


    @not_keyword
    def check_button(self, block_name, button_fields, button_name):
        if button_name not in button_fields:
            raise AssertionError(f"Button '{button_name}' not in button definition for block '{block_name}'")

    @not_keyword
    def fill_text_field(self, field_name, field_id, value, field_args):
        print(f"*INFO* Filling text field '{field_name}' with value: {value}")
        container_prefix = selector_prefix.get(self.container[0],'id')
        element = self.get_element(f"{container_prefix}={self.container} >> id={field_id}")
        self.fill_text(element, str(value))

    @not_keyword
    def fill_number_field(self, field_name, field_id, value, field_args):
            print(f"*INFO* Filling text field '{field_name}' with value: {value}")
            container_prefix = selector_prefix.get(self.container[0],'id')
            element = self.get_element(f"{container_prefix}={self.container} >> id={field_id}")
            self.fill_text(element, str(value))

    @not_keyword
    def fill_password_field(self, field_name, field_id, value, field_args):
        print(f"*INFO* Filling password field '{field_name}'")
        container_prefix = selector_prefix.get(self.container[0],'id')
        element = self.get_element(f"{container_prefix}={self.container} >> id={field_id}")
        self.fill_text(element, value)

    @not_keyword
    def fill_select_field(self, field_name, field_id, value, field_args):
        print(f"*INFO* Filling select field '{field_name}' with value: {value}")
        container_prefix = selector_prefix.get(self.container[0],'id')
        element = self.get_element(f"{container_prefix}={self.container} >> id={field_id}")
        self.select_options_by(element, SelectAttribute.label, value)

    @not_keyword
    def fill_radio_group(self, field_name, field_id, value, field_args):
        print(f"*INFO* Filling radio group '{field_name}' with value: {value}")
        container_prefix = selector_prefix.get(self.container[0],'id')
        element = self.get_element(f"{container_prefix}={self.container} >> id={field_id} >> xpath=//label[normalize-space(text())='{value}']")
        self.click(element)
        self.wait_for_elements_state(f"{container_prefix}={self.container} >> id={field_id}", ElementState.stable)


    @not_keyword
    def fill_date_picker(self, field_name, field_id, value, field_args):
        print(f"*INFO* Filling date picker '{field_name}' with value: {value}")
        container_prefix = selector_prefix.get(self.container[0],'id')
        element = self.get_element(f"{container_prefix}={self.container} >> id={field_id} >> xpath=//input")
        self.type_text(element, value)


    @not_keyword
    def fill_popup_lov(self, field_name, field_id, value, field_args):
        print(f"*INFO* Filling popup '{field_name}' with value: {value}")
        # direct input = <id>
        # popup button = <id>_lov_btn
        container_prefix = selector_prefix.get(self.container[0],'id')
        element = self.get_element(f"{container_prefix}={self.container} >> id={field_id}_lov_btn")
        self.click(element)
        self.wait_for_load_state(PageLoadStates.domcontentloaded, 1)

        # zoeken zit buiten de dialog (in hoofdpagina) in de DOM
        old_prefix = self.set_selector_prefix("")
        
        nr_retries = 5
        while nr_retries > 0:
            nr_retries -= 1
            search_element = self.get_element(f'xpath=//div[contains(@class, "a-PopupLOV-dialog") and contains(@id, "{field_id}")] '
                                                       '>> xpath=//input[@aria-label="Zoeken"]')
            self.clear_text(search_element)
            BuiltIn().sleep(1)
            self.wait_for_load_state(PageLoadStates.networkidle, 10)
            self.wait_for_load_state(PageLoadStates.domcontentloaded, 1)
            
            self.type_text(search_element, value)
            BuiltIn().sleep(1)
            self.wait_for_load_state(PageLoadStates.networkidle, 10)
            self.wait_for_load_state(PageLoadStates.domcontentloaded, 1)
            
            old_mode = self.set_strict_mode(False)
            self.wait_for_elements_state(f'xpath=//div[contains(@class, "a-PopupLOV-dialog") and contains(@id, "{field_id}")] '
                                                '>> xpath=//div[contains(@class, "a-PopupLOV-results")] '
                                                '>> xpath=//tbody/tr')
            self.set_strict_mode(True)

            if 'manualentry' in field_args:
                search_element = self.get_element(f'xpath=//div[contains(@class, "a-PopupLOV-dialog") and contains(@id, "{field_id}")] '
                                                           '>> xpath=//input[@aria-label="Zoeken"]')
                self.press_keys(search_element, 'Enter')

                self.wait_for_load_state(PageLoadStates.networkidle, 10)
                self.wait_for_load_state(PageLoadStates.domcontentloaded, 1)

            else:
                elements = self.get_elements(f'xpath=//div[contains(@class, "a-PopupLOV-dialog") and contains(@id, "{field_id}")] '
                                                '>> xpath=//div[contains(@class, "a-PopupLOV-results")]'
                                                f'>> xpath=//tbody/tr[contains(., "{value}")]')

                if len(elements) > 0:
                    element = elements[0]

                self.click(element)
                self.wait_for_load_state(PageLoadStates.domcontentloaded, 1)

            states = self.get_element_states(f'xpath=//div[contains(@class, "a-PopupLOV-dialog") and contains(@id, "{field_id}")] '
                                                            '>> xpath=//div[contains(@class, "a-PopupLOV-results")]')

            if 'visible' not in states:
                break

            # TODO: try, until selected value holds in input

        self.set_selector_prefix(old_prefix)


   
    
    @not_keyword
    def fill_fields(self, field_definition, data):
        for key, value in data.items():
            if key in field_definition:
                field = field_definition[key]
                if ':' not in field:
                    raise AssertionError(f"Field '{key}' has invalid definition: '{field}'")
                field_id, field_type, *field_args = field.split(':')
                print(f'*INFO* field_id: {field_id} field_type: {field_type} field_args: {field_args}')
                cb = self.field_input_callbacks.get(field_type)

                used_value = self._field_commands.process_command(value)

                if used_value:
                    if cb is None:
                        raise RuntimeError(f"Field type {field_type} not supported")
                    cb(key, field_id, used_value, field_args)

                # set focus on container, to trigger validation on focus lost of field
                self.focus(self.container)
                self.wait_for_load_state(PageLoadStates.domcontentloaded, 1)


    @not_keyword
    def check_display_only(self, field_name, field_id, value):
        print(f"*INFO* Checking DisplayOnly '{field_name}' with value: {value}")
        container_prefix = selector_prefix.get(self.container[0],'id')
        element = self.get_element(f"{container_prefix}={self.container} >> id={field_id}")
        real_value = self.get_text(element)
        BuiltIn().should_be_equal_as_strings(value, real_value, f"Field values not equal: {value} <-> {real_value}")
        
    @not_keyword
    def check_text_field(self, field_name, field_id, value):
        print(f"*INFO* Checking TextField '{field_name}' with value: {value}")
        container_prefix = selector_prefix.get(self.container[0],'id')
        element = self.get_element(f"{container_prefix}={self.container} >> id={field_id}")
        real_value = self.get_text(element)
        BuiltIn().should_be_equal_as_strings(value, real_value, f"Field values not equal: {value} <-> {real_value}")

    @not_keyword
    def check_select_list(self, field_name, field_id, value):
        print(f"*INFO* Checking SelectList '{field_name}' with value: {value}")
        container_prefix = selector_prefix.get(self.container[0],'id')
        element = self.get_element(f"{container_prefix}={self.container} >> id={field_id}")
        real_value = self.get_selected_options(element)
        if len(real_value) != 1:
            raise AssertionError("Expected 1 selected option")
        BuiltIn().should_be_equal_as_strings(value, real_value[0], f"Field values not equal: {value} <-> {real_value}")
    
    @not_keyword
    def check_date_picker(self, field_name, field_id, value):
        print(f"*INFO* Checking DatePicker '{field_name}' with value: {value}")
        container_prefix = selector_prefix.get(self.container[0],'id')
        element = self.get_element(f"{container_prefix}={self.container} >> id={field_id} >> //input")
        real_value = self.get_text(element)
        BuiltIn().should_be_equal_as_strings(value, real_value, f"Field values not equal: {value} <-> {real_value}")
    
    @not_keyword
    def check_fields(self, field_definition, data):
        for key, value in data.items():
            if key in field_definition:
                field = field_definition[key]
                if ':' not in field:
                    raise AssertionError(f"Field '{key}' has invalid definition: '{field}'")
                field_id, field_type, *field_args = field.split(':')
                print(f'*INFO* field_id: {field_id} field_type: {field_type} field_args: {field_args}')
                cb = self.field_check_callbacks.get(field_type)

                used_value = self._field_commands.process_command(value)

                if used_value:
                    if cb is None:
                        raise RuntimeError(f"Field type {field_type} not supported")
                    cb(key, field_id, used_value)
                

    @keyword
    def block_fill(self, block_name, field_definition, data):
        container = self.locators.get('block_container').replace('##TEXT##', block_name)
        self.check_container_visible(block_name, container)
        self.check_data_in_definition(block_name, field_definition, data)
        self.container = container
        self.fill_fields(field_definition, data)
        self.container = None

    @keyword
    def block_button(self, block_name, button_text):
        container = self.locators.get('block_container').replace('##TEXT##', block_name)
        self.check_container_visible(block_name, container)
        self.container = container

        locator = self.locators.get('block_button').replace('##TEXT##', button_text)

        container_prefix = selector_prefix.get(self.container[0],'text')
        button_prefix = selector_prefix.get(locator[0],'text')
        element = self.get_element(f"{container_prefix}={self.container} >> {button_prefix}={locator}")

        self.click(element)
        self.wait_for_load_state(PageLoadStates.networkidle, 10)
        self.wait_for_load_state(PageLoadStates.domcontentloaded, 1)
        self.container = None


    @not_keyword
    def get_value_hidden(self, field_id):
        container_prefix = selector_prefix.get(self.container[0],'id')
        element = self.get_element(f"{container_prefix}={self.container} >> id={field_id}")
        value = self.get_text(element)
        return value

    @not_keyword
    def get_value_displayonly(self, field_id):
        container_prefix = selector_prefix.get(self.container[0],'id')
        element = self.get_element(f"{container_prefix}={self.container} >> id={field_id}_DISPLAY")
        value = self.get_text(element)
        return value

    @not_keyword
    def _get_field_value(self, field_definition, field_name):
        field = field_definition[field_name]
        if ':' not in field:
            raise AssertionError(f"Field '{field_name}' has invalid definition: '{field}'")
        field_id, field_type, *field_args = field.split(':')
        print(f'*INFO* field_id: {field_id} field_type: {field_type} field_args: {field_args}')
        cb = self.field_get_callbacks.get(field_type)
        if cb is None:
            raise AttributeError(f"*WARN* No getter for field type: {field_type}")

        value = cb(field_id)
        print(f"*INFO* get value from: '{field_name}' of type '{field_type}'  returned: {value}")
        return value


    @keyword
    def block_get_value(self, block_name, field_definition, field_name):
        container = self.locators.get('block_container').replace('##TEXT##', block_name)
        self.check_container_visible(block_name, container)
        self.container = container

        if field_name not in field_definition:
            raise AttributeError(f"*WARN* Field '{field_name}' not in definition of block {block_name}")
        
        self.container = container
        value = self._get_field_value(field_definition, field_name)
        self.container = None
        
        return value


    @keyword
    def block_check(self, block_name, field_definition, data):
        container = self.locators.get('block_container').replace('##TEXT##', block_name)
        self.check_container_visible(block_name, container)
        self.check_data_in_definition(block_name, field_definition, data)
        self.container = container
        self.check_fields(field_definition, data)
        self.container = None
    

    @not_keyword
    def tab_select_helper(self, tab_name):
        
        tab_header = f"//a[span[text()='{tab_name}']]/.."
        tab_container = f"//div[@data-label='{tab_name}']"
        self.check_container_visible(f"{tab_name}.header", tab_header)

        header_prefix = selector_prefix.get(tab_header[0], 'id')
        element = self.get_element(f"{header_prefix}={tab_header}")
        self.click(element)
        self.wait_for_load_state(PageLoadStates.networkidle, 10)
        self.wait_for_load_state(PageLoadStates.domcontentloaded, 1)

        self.check_container_visible(f"{tab_name}.body", tab_container)
        return tab_container
    

    @keyword
    def tab_fill(self, tab_name, field_definition, data):
        """
        Assumes the tab contains 1 region with same label as tab
        """
        tab_container = self.tab_select_helper(tab_name)
        
        self.container = tab_container

        self.fill_fields(field_definition, data)

        self.container = None


    @keyword
    def tab_check(self, tab_name, field_definition, data):
        tab_container = self.tab_select_helper(tab_name)
                
        self.container = tab_container
        self.check_data_in_definition(tab_name, field_definition, data)
        self.check_fields(field_definition, data)
        self.container = None


    @keyword
    def tab_subregion_fill(self, tab_name, region, field_definition, data):
        """
        Assumes the tab contains several regions with own label name
        """
        tab_container = self.tab_select_helper(tab_name)

        region_locator = self.locators.get('block_container').replace('##TEXT##', region)

        container = self.get_element(tab_container + ' >> ' + region_locator)
        self.check_container_visible(region, container)
        self.check_data_in_definition(region, field_definition, data)
        
        self.container = container

        self.fill_fields(field_definition, data)

        self.container = None

    @keyword
    def tab_subregion_check(self, tab_name, region, field_definition, data):
        tab_container = self.tab_select_helper(tab_name)

        region_locator = self.locators.get('block_container').replace('##TEXT##', region)
        
        container = self.get_element(tab_container + ' >> ' + region_locator)
        self.check_container_visible(region, container)

        self.container = container
        self.check_data_in_definition(region, field_definition, data)
        self.check_fields(field_definition, data)
        self.container = None


    @keyword
    def tab_button(self, tab_name, button_text):
        tab_container = self.tab_select_helper(tab_name)
        
        self.container = tab_container
        locator = self.locators.get('tab_button').replace('##TEXT##', button_text)
        
        container_prefix = selector_prefix.get(self.container[0],'text')
        button_prefix = selector_prefix.get(locator[0],'text')
        element = self.get_element(f"{container_prefix}={self.container} >> {button_prefix}={locator}")

        self.click(element)
        self.wait_for_load_state(PageLoadStates.networkidle, 10)
        self.wait_for_load_state(PageLoadStates.domcontentloaded, 1)
        self.container = None

    @keyword
    def tab_subregion_button(self, tab_name, region, button):
        tab_container = self.tab_select_helper(tab_name)
        
        region_locator = self.locators.get('block_container').replace('##TEXT##', region)

        container = self.get_element(tab_container + ' >> ' + region_locator)
        self.check_container_visible(region, container)


        locator = self.locators.get('tab_button').replace('##TEXT##', button)
        
        button_prefix = selector_prefix.get(locator[0],'text')
        element = self.get_element(f"{container} >> {button_prefix}={locator}")

        self.click(element)
        self.wait_for_load_state(PageLoadStates.networkidle, 10)
        self.wait_for_load_state(PageLoadStates.domcontentloaded, 1)
        self.container = None


    @keyword
    def wizard_button(self, button_text):
        locator = self.locators.get('wizard_button').replace('##TEXT##', button_text)
        button_prefix = selector_prefix.get(locator[0],'text')
        element = self.get_element(f"{button_prefix}={locator}")
        self.click(element)
        self.wait_for_load_state(PageLoadStates.networkidle, 10)
        self.wait_for_load_state(PageLoadStates.domcontentloaded, 1)

    
    @keyword
    def page_button(self, button_text):
        locator = self.locators.get('page_button').replace('##TEXT##', button_text)
        button_prefix = selector_prefix.get(locator[0],'text')
        element = self.get_element(f"{button_prefix}={locator}")

        self.click(element)
        self.wait_for_load_state(PageLoadStates.networkidle, 10)
        self.wait_for_load_state(PageLoadStates.domcontentloaded, 1)

    @keyword
    def page_get_value(self, field_definition, field_name):
        self.container = ".t-Dialog-body"
        if field_name not in field_definition:
            raise AttributeError(f"*WARN* Field '{field_name}' not in definition of page")

        value = self._get_field_value(field_definition, field_name)
        self.container = None
        return value

    @not_keyword
    def check_cell_plaintext(self, column_name, column_id, value):
        print(f"*INFO* Checking PlainText '{column_name}' with value: {value}")
        text = self.get_text(self.classic_report_row + f">> xpath=//td[@headers='{column_id}']")
        BuiltIn().should_be_equal_as_strings(value, text, f"Field values not equal: {value} <-> {text}")


    @not_keyword
    def _check_columns(self, column_definition, data):
        for key, value in data.items():
            if key in column_definition:
                field = column_definition[key]
                if ':' not in field:
                    raise AssertionError(f"Column '{key}' has invalid definition: '{field}'")
                field_id, field_type, *field_args = field.split(':')
                print(f'*INFO* field_id: {field_id} field_type: {field_type} field_args: {field_args}')
                cb = self.cell_check_callbacks.get(field_type)

                used_value = self._field_commands.process_command(value)

                if used_value:
                    if cb is None:
                        raise RuntimeError(f"Column type {field_type} not supported")
                    cb(key, field_id, used_value)


    @not_keyword
    def _classic_report_select_row(self, rownumber):
        container_prefix = selector_prefix.get(self.container[0],'text')
        element = self.get_element(f'{container_prefix}={self.container} '
                                            '>> xpath=//table[@class="t-Report-report"] '
                                            f'>> xpath=//tbody/tr[{rownumber}]')
        self.click(element)
        self.wait_for_load_state(PageLoadStates.networkidle, 10)
        self.wait_for_load_state(PageLoadStates.domcontentloaded, 1)

    @not_keyword
    def _classic_report_check_row(self, columns_definition, rownumber, data, table_number=1):
        container_prefix = selector_prefix.get(self.container[0],'text')
        row_element = self.get_element(f'{container_prefix}={self.container} '
                                                    f'>> xpath=//table[@class="t-Report-report"][{table_number}] '
                                                    f'>> xpath=//tbody/tr[{rownumber}]')

        self.classic_report_row = row_element
        self._check_columns(columns_definition, data)
        self.classic_report_row = None

    @not_keyword
    def _classic_report_row_count(self):
        container_prefix = selector_prefix.get(self.container[0],'text')
        self.wait_for_load_state(PageLoadStates.networkidle, 10)
        self.wait_for_load_state(PageLoadStates.domcontentloaded, 1)
        row_elements = self.get_elements(f'{container_prefix}={self.container} '
                                                    '>> xpath=//table[@class="t-Report-report"] '
                                                    f'>> xpath=//tbody/tr')
        return len(row_elements)

        

    @keyword
    def block_classic_report_select_row(self, block_name, rownumber):
        container = self.locators.get('block_container').replace('##TEXT##', block_name)
        self.check_container_visible(block_name, container)

        self.container = container
        self._classic_report_select_row(rownumber)
        
        self.container = None

    @keyword
    def block_classic_report_check_row(self, block_name, columns_definition, rownumber, data, table_number=1):
        container = self.locators.get('block_container').replace('##TEXT##', block_name)
        
        self.container = container
        self._classic_report_check_row(columns_definition, rownumber, data, table_number)
        self.container = None

    @keyword
    def block_classic_report_row_count(self, block_name, expected_row_count=None):
        container = self.locators.get('block_container').replace('##TEXT##', block_name)
        
        self.container = container
        count = self._classic_report_row_count()
        if expected_row_count is not None:
            BuiltIn().should_be_equal_as_numbers(count, int(expected_row_count), "Number of report rows incorrect")
        self.container = None
        return count

    @keyword
    def tab_classic_report_select_row(self, tab_name, rownumber):
        tab_container = self.tab_select_helper(tab_name)
        
        self.container = tab_container
        self._classic_report_select_row(rownumber)
        self.container = None

    @keyword
    def tab_classic_report_check_row(self, tab_name, tab_columns_definition, rownumber, data):
        tab_container = self.tab_select_helper(tab_name)
        
        self.container = tab_container
        self._classic_report_check_row(tab_columns_definition, rownumber, data)
        self.container = None


    @keyword
    def tab_subregion_select_row(self, tab_name, region, rownumber):
        tab_container = self.tab_select_helper(tab_name)
        
        region_locator = self.locators.get('block_container').replace('##TEXT##', region)

        container = self.get_element(tab_container + ' >> ' + region_locator)
        self.check_container_visible(region, container)
        
        self.container = container
        self._classic_report_select_row(rownumber)
        self.container = None

    @keyword
    def tab_subregion_check_row(self, tab_name, tab_columns_definition, rownumber, data):
        tab_container = self.tab_select_helper(tab_name)
        
        self.container = tab_container
        self._classic_report_check_row(tab_columns_definition, rownumber, data)
        self.container = None


    # Template: Login
    @keyword
    def login_fill(self, block_name, field_definition, data):
        container = self.locators.get('login_container').replace('##TEXT##', block_name)

        self.check_container_visible(block_name, container)
        self.check_data_in_definition(block_name, field_definition, data)
        self.container = container
        self.fill_fields(field_definition, data)
        self.container = None

    @keyword
    def login_button(self, block_name, button_text):
        
        container = self.locators.get('login_container').replace('##TEXT##', block_name)
        self.check_container_visible(block_name, container)
        self.container = container

        locator = self.locators.get('login_button').replace('##TEXT##', button_text)

        container_prefix = selector_prefix.get(self.container[0],'text')
        button_prefix = selector_prefix.get(locator[0],'text')
        element = self.get_element(f"{container_prefix}={self.container} >> {button_prefix}={locator}")

        self.click(element)
        self.wait_for_load_state(PageLoadStates.networkidle, 10)
        self.wait_for_load_state(PageLoadStates.domcontentloaded, 1)
        self.container = None