"""
Oracle APEX support
"""

from robot.libraries.BuiltIn import BuiltIn
from robot.api.deco import keyword, not_keyword, library
from Browser import AssertionOperator, SelectAttribute, ElementState
from Browser.utils import PageLoadStates

selector_prefix = {
    '/': 'xpath', 
    '.': 'css', 
    '#': 'id'
    }

@library(scope='GLOBAL', auto_keywords=True)
class BrowserApex():
    def __init__(self):
        self.browser = None
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
            'DisplayOnly': self.check_display_only
        }
        self.field_commands = {
            'var': self.command_var
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
            'wizard_button': "//button/span[contains(text(),'##TEXT##')]"
        }


    @not_keyword
    def command_var(self, *args):
        print(f"*DEBUG* COMMAND VAR args: {args}")
        value = BuiltIn().get_variable_value(args[0])
        return value

    @keyword
    def register_field_commands(self, **commands_to_register):
        if type(commands_to_register) is not dict:
            raise AttributeError(f"Register Field Commands expect a dictionary as argument")

        self.field_commands.update(commands_to_register)
        print(f"*INFO* Test")

    @not_keyword
    def check_container_visible(self, container_name, container):
        try:
            container_prefix = selector_prefix.get(container[0],'id')
            element = self.browser.get_element(f"{container_prefix}={container}")
            self.browser.get_element_states(element, AssertionOperator.contains, 'visible')
        except:
            raise AssertionError(f"Container '{container_name}' not avaiable or visible")
        
    @not_keyword
    def check_data_in_definition(self, block_name, field_definition, data):

        for key, _ in data.items():
            if key not in field_definition:
                print(f"*WARN* Data field '{key}' not found in definition of block '{block_name}'" )


    @not_keyword
    def check_button(self, block_name, button_fields, button_name):
        if button_name not in button_fields:
            raise AssertionError(f"Button '{button_name}' not in button definition for block '{block_name}'")

    @not_keyword
    def fill_text_field(self, field_name, field_id, value, field_args):
        print(f"*INFO* Filling text field '{field_name}' with value: {value}")
        container_prefix = selector_prefix.get(self.container[0],'id')
        element = self.browser.get_element(f"{container_prefix}={self.container} >> id={field_id}")
        self.browser.fill_text(element, value)

    @not_keyword
    def fill_number_field(self, field_name, field_id, value, field_args):
            print(f"*INFO* Filling text field '{field_name}' with value: {value}")
            container_prefix = selector_prefix.get(self.container[0],'id')
            element = self.browser.get_element(f"{container_prefix}={self.container} >> id={field_id}")
            self.browser.fill_text(element, value)

    @not_keyword
    def fill_password_field(self, field_name, field_id, value, field_args):
        print(f"*INFO* Filling password field '{field_name}'")
        container_prefix = selector_prefix.get(self.container[0],'id')
        element = self.browser.get_element(f"{container_prefix}={self.container} >> id={field_id}")
        self.browser.fill_text(element, value)

    @not_keyword
    def fill_select_field(self, field_name, field_id, value, field_args):
        print(f"*INFO* Filling select field '{field_name}' with value: {value}")
        container_prefix = selector_prefix.get(self.container[0],'id')
        element = self.browser.get_element(f"{container_prefix}={self.container} >> id={field_id}")
        self.browser.select_options_by(element, SelectAttribute.label, value)

    @not_keyword
    def fill_radio_group(self, field_name, field_id, value, field_args):
        print(f"*INFO* Filling radio group '{field_name}' with value: {value}")
        container_prefix = selector_prefix.get(self.container[0],'id')
        element = self.browser.get_element(f"{container_prefix}={self.container} >> id={field_id} >> xpath=//label[normalize-space(text())='{value}']")
        self.browser.click(element)
        self.browser.wait_for_elements_state(f"{container_prefix}={self.container} >> id={field_id}", ElementState.stable)


    @not_keyword
    def fill_date_picker(self, field_name, field_id, value, field_args):
        print(f"*INFO* Filling date picker '{field_name}' with value: {value}")
        container_prefix = selector_prefix.get(self.container[0],'id')
        element = self.browser.get_element(f"{container_prefix}={self.container} >> id={field_id} >> xpath=//input")
        self.browser.type_text(element, value)


    @not_keyword
    def fill_popup_lov(self, field_name, field_id, value, field_args):
        print(f"*INFO* Filling popup '{field_name}' with value: {value}")
        # direct input = <id>
        # popup button = <id>_lov_btn
        container_prefix = selector_prefix.get(self.container[0],'id')
        element = self.browser.get_element(f"{container_prefix}={self.container} >> id={field_id}_lov_btn")
        self.browser.click(element)

        # zoeken zit buiten de dialog (in hoofdpagina) in de DOM
        old_prefix = self.browser.set_selector_prefix("")
        
        nr_retries = 5
        while nr_retries > 0:
            nr_retries -= 1
            search_element = self.browser.get_element(f'xpath=//div[contains(@class, "a-PopupLOV-dialog") and contains(@id, "{field_id}")] '
                                                       '>> xpath=//input[@aria-label="Zoeken"]')
            self.browser.clear_text(search_element)
            self.browser.type_text(search_element, value)

            BuiltIn().sleep(1)
            old_mode = self.browser.set_strict_mode(False)
            self.browser.wait_for_elements_state(f'xpath=//div[contains(@class, "a-PopupLOV-dialog") and contains(@id, "{field_id}")] '
                                                '>> xpath=//div[contains(@class, "a-PopupLOV-results")] '
                                                '>> xpath=//tbody/tr')
            self.browser.set_strict_mode(True)

            if 'manualentry' in field_args:
                search_element = self.browser.get_element(f'xpath=//div[contains(@class, "a-PopupLOV-dialog") and contains(@id, "{field_id}")] '
                                                           '>> xpath=//input[@aria-label="Zoeken"]')
                self.browser.press_keys(search_element, 'Enter')

            else:
                elements = self.browser.get_elements(f'xpath=//div[contains(@class, "a-PopupLOV-dialog") and contains(@id, "{field_id}")] '
                                                '>> xpath=//div[contains(@class, "a-PopupLOV-results")]'
                                                f'>> xpath=//tbody/tr[contains(., "{value}")]')

                if len(elements) > 0:
                    element = elements[0]

                self.browser.click(element)

            states = self.browser.get_element_states(f'xpath=//div[contains(@class, "a-PopupLOV-dialog") and contains(@id, "{field_id}")] '
                                                            '>> xpath=//div[contains(@class, "a-PopupLOV-results")]')

            if 'visible' not in states:
                break

            # TODO: try, until selected value holds in input

        self.browser.set_selector_prefix(old_prefix)


    @not_keyword
    def process_command(self, value):
        used_value = None
        if value[0] in ['&', '!', '$']:
            args = value[1:].split(':')
            cmd_name = args.pop(0)
            print(f"*INFO* command: {cmd_name}  args: {args}")
            if cmd_name in self.field_commands:
                cmd = self.field_commands[cmd_name]
                if type(cmd) is str:
                    # run as keyword
                    used_value = BuiltIn().run_keyword(cmd, *args)

                else:
                    # run as function
                    used_value = cmd(*args)

            else:
                raise AttributeError(f"Field command `{cmd_name}` not found")
            print(f"*INFO* command: {cmd_name}  returned: {used_value}")

        else:
            used_value = value

        return used_value
    
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

                used_value = self.process_command(value)

                if used_value:
                    if cb is None:
                        raise RuntimeError(f"Field type {field_type} not supported")
                    cb(key, field_id, used_value, field_args)

                # set focus on container, to trigger validation on focus lost of field
                self.browser.focus(self.container)
                self.browser.wait_for_load_state(PageLoadStates.domcontentloaded, 1)


    @not_keyword
    def check_display_only(self, field_name, field_id, value):
        print(f"*INFO* Checking DisplayOnly '{field_name}' with value: {value}")
        container_prefix = selector_prefix.get(self.container[0],'id')
        element = self.browser.get_element(f"{container_prefix}={self.container} >> id={field_id}_DISPLAY")
        real_value = self.browser.get_text(element)
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

                used_value = self.process_command(value)

                if used_value:
                    if cb is None:
                        raise RuntimeError(f"Field type {field_type} not supported")
                    cb(key, field_id, used_value)

    @keyword
    def block_fill(self, block_name, field_definition, data):
        self.browser = BuiltIn().get_library_instance('Browser')
        container = self.locators.get('block_container').replace('##TEXT##', block_name)
        self.check_container_visible(block_name, container)
        self.check_data_in_definition(block_name, field_definition, data)
        self.container = container
        self.fill_fields(field_definition, data)
        self.container = None

    @keyword
    def block_button(self, block_name, button_text):
        self.browser = BuiltIn().get_library_instance('Browser')
        container = self.locators.get('block_container').replace('##TEXT##', block_name)
        self.check_container_visible(block_name, container)
        self.container = container

        locator = self.locators.get('block_button').replace('##TEXT##', button_text)

        container_prefix = selector_prefix.get(self.container[0],'text')
        button_prefix = selector_prefix.get(locator[0],'text')
        element = self.browser.get_element(f"{container_prefix}={self.container} >> {button_prefix}={locator}")

        self.browser.click(element)

        self.container = None


    @not_keyword
    def get_value_hidden(self, field_id):
        container_prefix = selector_prefix.get(self.container[0],'id')
        element = self.browser.get_element(f"{container_prefix}={self.container} >> id={field_id}")
        value = self.browser.get_text(element)
        return value

    @not_keyword
    def get_value_displayonly(self, field_id):
        container_prefix = selector_prefix.get(self.container[0],'id')
        element = self.browser.get_element(f"{container_prefix}={self.container} >> id={field_id}_DISPLAY")
        value = self.browser.get_text(element)
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
        self.browser = BuiltIn().get_library_instance('Browser')
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
        self.browser = BuiltIn().get_library_instance('Browser')
        container = self.locators.get('block_container').replace('##TEXT##', block_name)
        self.check_container_visible(block_name, container)
        self.check_data_in_definition(block_name, field_definition, data)
        self.container = container
        self.check_fields(field_definition, data)
        self.container = None
    

    @not_keyword
    def tab_select_helper(self, tab_name):
        
        tab_header = f"//a/span[text()='{tab_name}']"
        tab_container = f"//div[@aria-label='{tab_name}']"
        self.check_container_visible(f"{tab_name}.header", tab_header)

        header_prefix = selector_prefix.get(tab_header[0], 'id')
        element = self.browser.get_element(f"{header_prefix}={tab_header}")
        self.browser.click(element)

        self.check_container_visible(f"{tab_name}.body", tab_container)
        return tab_container
    

    @keyword
    def tab_fill(self, tab_name, field_definition, data):
        self.browser = BuiltIn().get_library_instance('Browser')
        tab_container = self.tab_select_helper(tab_name)
        
        self.container = tab_container

        self.fill_fields(field_definition, data)

        self.container = None

    @keyword
    def tab_button(self, tab_name, button_text):
        self.browser = BuiltIn().get_library_instance('Browser')
        tab_container = self.tab_select_helper(tab_name)
        
        self.container = tab_container
        locator = self.locators.get('tab_button').replace('##TEXT##', button_text)
        
        container_prefix = selector_prefix.get(self.container[0],'text')
        button_prefix = selector_prefix.get(locator[0],'text')
        element = self.browser.get_element(f"{container_prefix}={self.container} >> {button_prefix}={locator}")

        self.browser.click(element)

        self.container = None


    @keyword
    def wizard_button(self, button_text):
        self.browser = BuiltIn().get_library_instance('Browser')
        locator = self.locators.get('wizard_button').replace('##TEXT##', button_text)
        button_prefix = selector_prefix.get(locator[0],'text')
        element = self.browser.get_element(f"{button_prefix}={locator}")
        self.browser.click(element)

    
    @keyword
    def page_button(self, button_text):
        self.browser = BuiltIn().get_library_instance('Browser')
        locator = self.locators.get('page_button').replace('##TEXT##', button_text)
        button_prefix = selector_prefix.get(locator[0],'text')
        element = self.browser.get_element(f"{button_prefix}={locator}")

        self.browser.click(element)

    @keyword
    def page_get_value(self, field_definition, field_name):
        self.browser = BuiltIn().get_library_instance('Browser')
        self.container = ".t-Dialog-body"
        if field_name not in field_definition:
            raise AttributeError(f"*WARN* Field '{field_name}' not in definition of page")

        value = self._get_field_value(field_definition, field_name)
        self.container = None
        return value

    @not_keyword
    def check_cell_plaintext(self, column_name, column_id, value):
        print(f"*INFO* Checking PlainText '{column_name}' with value: {value}")
        td = self.classic_report_row.get_element(f"xpath=//td[headers='{column_id}']")
        pass


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

                used_value = self.process_command(value)

                if used_value:
                    if cb is None:
                        raise RuntimeError(f"Column type {field_type} not supported")
                    cb(key, field_id, used_value)


    @not_keyword
    def _classic_report_select_row(self, rownumber):
        container_prefix = selector_prefix.get(self.container[0],'text')
        element = self.browser.get_element(f'{container_prefix}={self.container} '
                                            '>> xpath=//table[@class="t-Report-report"] '
                                            f'>> xpath=//tbody/tr[{rownumber}]')
        self.browser.click(element)

    @not_keyword
    def _classic_report_check_row(self, columns_definition, rownumber, data):
        container_prefix = selector_prefix.get(self.container[0],'text')
        row_element = self.browser.get_element(f'{container_prefix}={self.container} '
                                                    '>> xpath=//table[@class="t-Report-report"] '
                                                    f'>> xpath=//tbody/tr[{rownumber}]')

        self.classic_report_row = row_element
        self._check_columns(columns_definition, data)
        self.classic_report_row = None
        

    @keyword
    def block_classic_report_select_row(self, block_name, rownumber):
        self.browser = BuiltIn().get_library_instance('Browser')
        container = self.locators.get('block_container').replace('##TEXT##', block_name)
        self.check_container_visible(block_name, container)

        self.container = container
        self._classic_report_select_row(rownumber)
        self.container = None

    @keyword
    def block_classic_report_check_row(self, block_name, tab_columns_definition, rownumber, data):
        self.browser = BuiltIn().get_library_instance('Browser')
        container = self.locators.get('block_container').replace('##TEXT##', block_name)
        
        self.container = container
        self._classic_report_check_row(tab_columns_definition, rownumber, data)
        self.container = None


    @keyword
    def tab_classic_report_select_row(self, tab_name, rownumber):
        self.browser = BuiltIn().get_library_instance('Browser')
        tab_container = self.tab_select_helper(tab_name)
        
        self.container = tab_container
        self._classic_report_select_row(rownumber)
        self.container = None

    @keyword
    def tab_classic_report_check_row(self, tab_name, tab_columns_definition, rownumber, data):
        self.browser = BuiltIn().get_library_instance('Browser')
        tab_container = self.tab_select_helper(tab_name)
        
        self.container = tab_container
        self._classic_report_check_row(tab_columns_definition, rownumber, data)
        self.container = None

    # Template: Login
    @keyword
    def login_fill(self, block_name, field_definition, data):
        self.browser = BuiltIn().get_library_instance('Browser')
        container = self.locators.get('login_container').replace('##TEXT##', block_name)

        self.check_container_visible(block_name, container)
        self.check_data_in_definition(block_name, field_definition, data)
        self.container = container
        self.fill_fields(field_definition, data)
        self.container = None

    @keyword
    def login_button(self, block_name, button_text):
        self.browser = BuiltIn().get_library_instance('Browser')
        
        container = self.locators.get('login_container').replace('##TEXT##', block_name)
        self.check_container_visible(block_name, container)
        self.container = container

        locator = self.locators.get('login_button').replace('##TEXT##', button_text)

        container_prefix = selector_prefix.get(self.container[0],'text')
        button_prefix = selector_prefix.get(locator[0],'text')
        element = self.browser.get_element(f"{container_prefix}={self.container} >> {button_prefix}={locator}")

        self.browser.click(element)

        self.container = None