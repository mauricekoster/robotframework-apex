"""
Oracle APEX support
"""

from robot.libraries.BuiltIn import BuiltIn
from robot.api.deco import  not_keyword, library
from Browser import  SelectAttribute, ElementState, Browser
from Browser.utils import PageLoadStates, logger
from datetime import datetime

from .keywords import (
    Breadcrumb, 
    ClassicReport,
    Dialog, 
    FieldCommand, 
    LoginTemplate, 
    Region, 
    Tab
)


@library(scope='GLOBAL', auto_keywords=True)
class BrowserApex(Browser):
    def __init__(self, **kwargs):
        if 'test_date_format' in kwargs:
            self.test_date_format = kwargs['test_date_format']
            del kwargs['test_date_format']
        else:
            self.test_date_format = '%m/%d/%Y'

        Browser.__init__(self, **kwargs)

        

        self.container = None

        self.field_input_callbacks = {
            'TextField': self.fill_text_field,
            'Textarea': self.fill_textarea_field,
            'TextFieldwithautocomplete': self.fill_text_autocomplete_field,
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

        self.locators = {}

        self._field_commands = FieldCommand(self)
                
        self.add_library_components([
            Breadcrumb(self),
            ClassicReport(self),
            Dialog(self),
            self._field_commands,
            LoginTemplate(self),
            Region(self),
            Tab(self),

        ])
        
        
    @not_keyword
    def get_locator(self, locator_name, replace_strings={}):
        locator = self.locators.get(locator_name)
        for k, v in replace_strings.items():
            locator = locator.replace(k, v)
       
        return locator


 
    @not_keyword
    def fill_text_field(self, field_name, field_id, value, field_args):
        print(f"*INFO* Filling text field '{field_name}' with value: {value}")
        element = self.get_element(f"{self.container} >> id={field_id}")
        self.fill_text(element, str(value))

    @not_keyword
    def fill_text_autocomplete_field(self, field_name, field_id, value, field_args):
        print(f"*INFO* Filling text field with autocomplete '{field_name}' with value: {value}")
        element = self.get_element(f"{self.container} >> id={field_id} >> xpath=//input")
        self.fill_text(element, str(value))

    @not_keyword
    def fill_textarea_field(self, field_name, field_id, value, field_args):
        print(f"*INFO* Filling textarea field '{field_name}' with value: {value}")
        element = self.get_element(f"{self.container} >> id={field_id}")
        self.fill_text(element, str(value))

    @not_keyword
    def fill_number_field(self, field_name, field_id, value, field_args):
        print(f"*INFO* Filling text field '{field_name}' with value: {value}")
        element = self.get_element(f"{self.container} >> id={field_id}")
        self.fill_text(element, str(value))

    @not_keyword
    def fill_password_field(self, field_name, field_id, value, field_args):
        print(f"*INFO* Filling password field '{field_name}'")
        element = self.get_element(f"{self.container} >> id={field_id}")
        self.fill_text(element, value)

    @not_keyword
    def fill_select_field(self, field_name, field_id, value, field_args):
        print(f"*INFO* Filling select field '{field_name}' with value: {value}")
        element = self.get_element(f"{self.container} >> id={field_id}")
        self.select_options_by(element, SelectAttribute.label, value)

    @not_keyword
    def fill_radio_group(self, field_name, field_id, value, field_args):
        print(f"*INFO* Filling radio group '{field_name}' with value: {value}")
        element = self.get_element(f"{self.container} >> id={field_id} >> xpath=//label[normalize-space(text())='{value}']")
        self.click(element)
        self.wait_for_elements_state(f"{self.container} >> id={field_id}", ElementState.stable)


    @not_keyword
    def fill_date_picker(self, field_name, field_id, value, field_args):
        print(f"*INFO* Filling date picker '{field_name}' with value: {value}")
        datepicker_element = self.get_element(f"{self.container} >> id={field_id}")
        display_as = 'native'
        attrs = self.get_attribute_names(datepicker_element)
        if 'display-as' in attrs:
            display_as = self.get_attribute(datepicker_element, 'display-as')

        match display_as:
            case 'native':
                date_format = BuiltIn().get_variable_value("${datepicker_native_dateformat}", self.test_date_format)
            case 'popup':
                date_format = BuiltIn().get_variable_value("${datepicker_popup_dateformat}", self.test_date_format)
            case _:
                raise f"Unexpected 'display-as' attribute '{display_as}' of datapicker for {field_name}"
        element = f"{datepicker_element} >> xpath=//input"
        
        d = datetime.strptime(value, self.test_date_format)
        print(f"*INFO* datepicker variant: {display_as}. Using date format to type text: {date_format}")
        self.type_text(element, d.strftime(format=date_format))
        

    @not_keyword
    def fill_popup_lov(self, field_name, field_id, value, field_args):
        print(f"*INFO* Filling popup '{field_name}' with value: {value} args: {field_args}")
        # direct input = <id>
        # popup button = <id>_lov_btn
        element = self.get_element(f"{self.container} >> id={field_id}_lov_btn")
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

            if 'manualentry' in field_args:
                logger.info('PopupLOV: Entering manualentry')
                search_element = self.get_element(f'xpath=//div[contains(@class, "a-PopupLOV-dialog") and contains(@id, "{field_id}")] '
                                                           '>> xpath=//input[@aria-label="Zoeken"]')
                self.press_keys(search_element, 'Enter')

                self.wait_for_load_state(PageLoadStates.networkidle, 10)
                self.wait_for_load_state(PageLoadStates.domcontentloaded, 1)

            else:
                # Wait for results, when expecting a row to match
                old_mode = self.set_strict_mode(False)
                self.wait_for_elements_state(f'xpath=//div[contains(@class, "a-PopupLOV-dialog") and contains(@id, "{field_id}")] '
                                                    '>> xpath=//div[contains(@class, "a-PopupLOV-results")] '
                                                    '>> xpath=//tbody/tr')
                self.set_strict_mode(True)

                elements = self.get_elements(f'xpath=//div[contains(@class, "a-PopupLOV-dialog") and contains(@id, "{field_id}")] '
                                                '>> xpath=//div[contains(@class, "a-PopupLOV-results")]'
                                                f'>> xpath=//tbody/tr')

                if len(elements) > 0:
                    element = elements[0]


                self.click(element)
                self.wait_for_load_state(PageLoadStates.domcontentloaded, 10)

            states = self.get_element_states(f'xpath=//div[contains(@class, "a-PopupLOV-dialog") and contains(@id, "{field_id}")] '
                                                            '>> xpath=//div[contains(@class, "a-PopupLOV-results")]')

            if 'visible' not in states:
                break

            # TODO: try, until selected value holds in input

        self.set_selector_prefix(old_prefix)

  
    @not_keyword
    def fill_fields(self, locator, field_definition, data):
        self.container = locator
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
        self.container = None


    @not_keyword
    def check_display_only(self, field_name, field_id, value):
        print(f"*INFO* Checking DisplayOnly '{field_name}' with value: {value}")
        element = self.get_element(f"{self.container} >> id={field_id}")
        real_value = self.get_text(element)
        BuiltIn().should_be_equal_as_strings(value, real_value, f"Field values not equal: {value} <-> {real_value}")
        
    @not_keyword
    def check_text_field(self, field_name, field_id, value):
        print(f"*INFO* Checking TextField '{field_name}' with value: {value}")
        element = self.get_element(f"{self.container} >> id={field_id}")
        real_value = self.get_text(element)
        BuiltIn().should_be_equal_as_strings(value, real_value, f"Field values not equal: {value} <-> {real_value}")

    @not_keyword
    def check_select_list(self, field_name, field_id, value):
        print(f"*INFO* Checking SelectList '{field_name}' with value: {value}")
        element = self.get_element(f"{self.container} >> id={field_id}")
        real_value = self.get_selected_options(element)
        if len(real_value) != 1:
            raise AssertionError("Expected 1 selected option")
        BuiltIn().should_be_equal_as_strings(value, real_value[0], f"Field values not equal: {value} <-> {real_value}")
    
    @not_keyword
    def check_date_picker(self, field_name, field_id, value):
        print(f"*INFO* Checking DatePicker '{field_name}' with value: {value}")
        element = self.get_element(f"{self.container} >> id={field_id} >> //input")
        real_value = self.get_text(element)
        BuiltIn().should_be_equal_as_strings(value, real_value, f"Field values not equal: {value} <-> {real_value}")
    
    @not_keyword
    def check_fields(self, locator, field_definition, data):
        self.container = locator
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
        self.container = None

    @not_keyword
    def get_value_hidden(self, field_id):
        element = self.get_element(f"{self.container} >> id={field_id}")
        value = self.get_text(element)
        return value

    @not_keyword
    def get_value_displayonly(self, field_id):
        element = self.get_element(f"{self.container} >> id={field_id}")
        value = self.get_text(element)
        return value

    @not_keyword
    def get_field_value(self, container, field_definition, field_name):
        self.container = container
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
        self.container = None
        return value
