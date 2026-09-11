from Browser import AssertionOperator
from robot.libraries.BuiltIn import BuiltIn
from Browser.utils import PageLoadStates, logger
from robot.api.deco import keyword, not_keyword
from ..librarycomponent import LibraryComponent


class ClassicReport(LibraryComponent):
    """
    Handling of Classic Report region.
    """
    def __init__(self, library):
        super().__init__(library)

        self.library.locators.update({
            'report_container': "css=.t-Report",
            'report_no_data_found': 'css=.nodatafound',
            'report_table': "xpath=//table[@class='t-Report-report']",
            'report_select_row': "xpath=//tbody/tr[##ROWNR##]",
            'report_all_rows': "xpath=//tbody/tr",
            'report_cell': "xpath=//td[@headers='##COL##']",
        })

        self.cell_check_callbacks = {
            'PlainText': self.check_cell_plaintext
        }


    @not_keyword
    def _get_report_locator(self, report):
        if type(report) is str:
            report_name = report
        else:
            if 'name' in report:
                report_name = report['name']
            else:
                raise AttributeError("No name in report")

        return self.library.get_locator('report_container', {'##NAME##': report_name})  

    @not_keyword
    def _check_report_visible(self, report, locator):
        try:
            element = self.library.get_element(f"{locator}")
            self.library.get_element_states(element, AssertionOperator.contains, 'visible')
        except:
            raise AssertionError(f"Classic Report '{report}' not avaiable or visible")


    @keyword(tags=('Apex', 'Classic Report'))
    def select_report(self, report, parent=None):
        if parent:
            locator = self.library.get_element(f"{parent} >> {self._get_report_locator(report)}")
        else:
            locator = self.library.get_element(f"{self._get_report_locator(report)}")

        self._check_report_visible(report, locator)
        return locator

    @keyword(tags=('Apex', 'Classic Report'))
    def classic_report_select_row(self, locator, row_number):
        table_locator = self.library.get_locator('report_table')
        row_locator = self.library.get_locator('report_select_row', {"##ROWNR##": row_number})
        self.library.click(f'{locator} >> {table_locator} >> {row_locator}')
        self.library.wait_for_load_state(PageLoadStates.networkidle, 10)
        self.library.wait_for_load_state(PageLoadStates.domcontentloaded, 1)


    @not_keyword
    def check_cell_plaintext(self, locator, column_name, column_id, value, *field_args):
        logger.info(f"Checking PlainText '{column_name}' with value: {value}. Arguments: {field_args}")
        cell_locator = self.library.get_locator('report_cell', {'##COL##': column_id})
        self.library.get_text(locator + f" >> {cell_locator}", 
                            AssertionOperator.equal, value)


    @not_keyword
    def _check_columns(self, locator, column_definition, data):
        for key, value in data.items():
            if key in column_definition:
                field = column_definition[key]
                if ':' not in field:
                    raise AssertionError(f"Column '{key}' has invalid definition: '{field}'")
                field_id, field_type, *field_args = field.split(':')
                logger.info(f'field_id: {field_id} field_type: {field_type} field_args: {field_args}')
                cb = self.cell_check_callbacks.get(field_type)

                used_value = self.library._field_commands.process_command(value)

                if used_value:
                    if cb is None:
                        raise RuntimeError(f"Column type {field_type} not supported")
                    cb(locator, key, field_id, used_value, field_args)
        
    @keyword(tags=('Apex', 'Classic Report'))
    def classic_report_check_row(self, locator, columns_definition, row_number, data):
        table_locator = self.library.get_locator('report_table')
        row_locator = self.library.get_locator('report_select_row', {"##ROWNR##": row_number})

        container = f'{locator} >> {table_locator} >> {row_locator}'
        self._check_columns(container, columns_definition, data)

    @keyword(tags=('Apex', 'Classic Report'))
    def classic_report_no_data_found(self, locator, message=None):
        """
        locator = Region

        Check if region contains a Classic report, this is in case no data is found, there is no Classic Report.
        """
        table_locator = self.library.get_locator('report_table')
        elems = self.library.get_elements(f"{locator} >> {table_locator}")
        BuiltIn().should_be_equal_as_numbers(len(elems), 0, "Unexpected Classic Report found.")

        if message:
            msg_locator=self.library.get_locator('report_no_data_found')
            self.library.get_text(f"{locator} >> {msg_locator}", AssertionOperator.contains, message)

    
    @keyword(tags=('Apex', 'Classic Report'))
    def classic_report_row_count(self, locator, expected_row_count=None):
        self.library.wait_for_load_state(PageLoadStates.networkidle, 10)
        self.library.wait_for_load_state(PageLoadStates.domcontentloaded, 1)
        table_locator = self.library.get_locator('report_table')
        row_locator = self.library.get_locator('report_all_rows')
        
        row_elements = self.get_elements(f'{locator} >> {table_locator} >> {row_locator}')
        count = len(row_elements)
        if expected_row_count is not None:
            BuiltIn().should_be_equal_as_numbers(count, int(expected_row_count), "Number of report rows incorrect")
        return count

        
