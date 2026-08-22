from parsimonious import Grammar, NodeVisitor
from BrowserApex.cli.apex import Page, Region
from importlib import resources as impresources
from BrowserApex.cli import apex
from pathlib import Path


class RuleNotImplemented(BaseException):
    pass


class ApxNodeVisitor(NodeVisitor):
    def visit_page_object(self, node, visited_children):
        """ Gets the section name. """
        _, component_id, _, _, _, body_parts, _, _, _ = visited_children
        if type(component_id) is list:
            component_id = component_id[0][1]
        else:
            component_id = None

        page = Page(component_id)
        for item in body_parts:
            if type(item) is tuple:
                page[item[0]] = item[1]
            elif type(item) is Region:
                page.add_region(item)
            else:
                raise RuleNotImplemented(f"unprocessed: {item}")
        return page

    def visit_component_id(self, node, visited_children):
        return node.text

    def visit_page_body_line(self, node, visited_children):
        return visited_children[0]

    def visit_page_group_block(self, node, visited_children):
        return visited_children[0]

    def visit_page_child_component(self, node, visited_children):
        return visited_children[0]


    def visit_page_direct_property_line(self, node, visited_children):
        return visited_children[1]

    def visit_page_direct_property(self, node, visited_children):
        v = visited_children[0]
        title, _, _, value = v
        return (title.text, value)


    def visit_page_appearance(self, node, visited_children):
        parts = visited_children[5]
        d = {}
        for item in parts:
            if type(item) is tuple:
                d[item[0]] = item[1]
            else:
                raise RuleNotImplemented()
        return ('appearance', d)

    def visit_page_appearance_property_line(self, node, visited_children):
        return visited_children[1]

    def visit_page_appearance_property(self, node, visited_children):
        v = visited_children[0]
        return (v[0].text, v[3])


    def visit_page_navigation(self, node, visited_children):
        parts = visited_children[5]
        d = {}
        for item in parts:
            if type(item) is tuple:
                d[item[0]] = item[1]
            else:
                raise RuleNotImplemented()
        return ('navigation', d)
    
    def visit_page_navigation_property_line(self, node, visited_children):
        return visited_children[1]

    def visit_page_navigation_property(self, node, visited_children):
        v = visited_children[0]
        match v[0].text:
            case 'cursorFocus':
                return (v[0].text, v[3][0].text)
            case 'warnOnUnsavedChanges':
                return (v[0].text, v[3])


    def visit_page_css(self, node, visited_children):
        parts = visited_children[5]
        d = {}
        for item in parts:
            if type(item) is tuple:
                d[item[0]] = item[1]
            else:
                raise RuleNotImplemented()
        return ('css', d)

    def visit_page_css_property_line(self, node, visited_children):
        return visited_children[1]


    def visit_page_css_property(self, node, visited_children):
        v = visited_children[0]
        match v[0].text:
            case 'inline':
                return (v[0].text, v[-1])
            case 'fileUrls':
                return (v[0].text, v[3])

    def visit_page_security(self, node, visited_children):
        parts = visited_children[5]
        d = {}
        for item in parts:
            if type(item) is tuple:
                d[item[0]] = item[1]
            else:
                raise RuleNotImplemented()
        return ('security', d)

    def visit_page_security_property_line(self, node, visited_children):
        return visited_children[1]


    def visit_page_security_property(self, node, visited_children):
        v = visited_children[0]
        match v[0].text:
            case 'authentication' | 'pageAccessProtection':
                return (v[0].text, v[3][0].text)
            case 'formAutoComplete':
                return (v[0].text, v[3])
            case _:
                raise RuleNotImplemented()

    def visit_page_advanced(self, node, visited_children):
        parts = visited_children[5]
        d = {}
        for item in parts:
            if type(item) is tuple:
                d[item[0]] = item[1]
            else:
                raise RuleNotImplemented()
        return ('advanced', d)

    def visit_page_advanced_property_line(self, node, visited_children):
        return visited_children[1]


    def visit_page_advanced_property(self, node, visited_children):
        v = visited_children[0]
        match v[0].text:
            case 'reloadOnSubmit' | 'duplicateSubmissionUrl':
                return (v[0].text, v[3][0].text)
            case 'enableMetaTags' | 'enableDuplicatePageSubmissions':
                return (v[0].text, v[3])
            case _:
                raise RuleNotImplemented()


    def visit_region(self, node, visited_children):
        _, _, component_id, _, _, _, body_parts, _, _, _ = visited_children
        if type(component_id) is list:
            component_id = component_id[0][1]
        else:
            component_id = None

        region = Region(component_id)
        for item in body_parts:
            if type(item) is tuple:
                region[item[0]] = item[1]
            else:
                raise RuleNotImplemented(f"unprocessed: {item}")
        return region

    def visit_region_body_line(self, node, visited_children):
        return visited_children[0]

    def visit_region_direct_property_line(self, node, visited_children):
        return visited_children[1]

    def visit_region_direct_property(self, node, visited_children):
        v = visited_children[0]
        title, _, _, value = v
        return (title.text, value)

    def visit_region_group_block(self, node, visited_children):
        return visited_children[0]

    def visit_region_layout(self, node, visited_children):
        parts = visited_children[5]
        d = {}
        for item in parts:
            if type(item) is tuple:
                d[item[0]] = item[1]
            else:
                raise RuleNotImplemented()
        return ('layout', d)
    
    def visit_region_layout_property_line(self, node, visited_children):
        return visited_children[1]

    def visit_region_layout_property(self, node, visited_children):
        v = visited_children[0]
        match v[0].text:
            case 'sequence' | 'slot':
                return (v[0].text, v[3])
            case 'reloadOnSubmit' | 'duplicateSubmissionUrl':
                return (v[0].text, v[3][0].text)
            case 'enableMetaTags' | 'enableDuplicatePageSubmissions':
                return (v[0].text, v[3])
            case _:
                raise RuleNotImplemented()

    def visit_region_appearance(self, node, visited_children):
        parts = visited_children[5]
        d = {}
        for item in parts:
            if type(item) is tuple:
                d[item[0]] = item[1]
            else:
                raise RuleNotImplemented()
        return ('appearance', d)
    
    def visit_region_appearance_property_line(self, node, visited_children):
        return visited_children[1]

    def visit_region_appearance_property(self, node, visited_children):
        v = visited_children[0]
        match v[0].text:
            case 'template':
                return (v[0].text, v[3])
            case 'templateOptions':
                return (v[0].text, v[3][0])
            case 'reloadOnSubmit' | 'duplicateSubmissionUrl':
                return (v[0].text, v[3][0].text)
            case 'enableMetaTags' | 'enableDuplicatePageSubmissions':
                return (v[0].text, v[3])
            case _:
                raise RuleNotImplemented()

    def visit_region_image(self, node, visited_children):
        parts = visited_children[5]
        d = {}
        for item in parts:
            if type(item) is tuple:
                d[item[0]] = item[1]
            else:
                raise RuleNotImplemented()
        return ('image', d)
    
    def visit_region_image_property_line(self, node, visited_children):
        return visited_children[1]

    def visit_region_image_property(self, node, visited_children):
        v = visited_children[0]
        match v[0].text:
            case 'fileUrl' | 'accessibleDescription' | 'customAttributes':
                return (v[0].text, v[3])
            case _:
                raise RuleNotImplemented()


    def visit_reference(self, node, visited_children):
        return node.text


    def visit_multiline_string(self, node, visited_children):
        return node.text

    def visit_array_of_string_like_value(self, node, visited_children):
        values = visited_children[1]
        ret = []
        for v in values:
            ret.append(v[2])

        return ret

    def visit_string_like_value(self, node, visited_children):
        t = node.text
        if t[0] == '"' and t[-1] == '"':
            return t[1:-1]
        else:
            return t

    def visit_identifier(self, node, visited_children):
        return node.text

    def visit_string(self, node, visited_children):
        return node.text[1:-1]

    def visit_boolean(self, node, visited_children):
        return node.text == 'true'

    def visit_number(self, node, visited_children):
        if '.' in node.text:
            return float(node.text)
        else:
            return int(node.text)
    
    def visit_required_ws(self, node, visited_children):
        return None

    def visit_ws(self, node, visited_children):
        return None
    
    def generic_visit(self, node, visited_children):
        """ The generic visit method. """
        return visited_children or node



def parse_file(fn: Path) -> Page:
    inp_file = impresources.files(apex) / 'apexlang-26.1.peg'
    with inp_file.open("rt") as f:
        template = f.read()

    grammar = Grammar(template)

    with open(fn, 'r') as f:
        data = f.read()

    nodes = grammar.parse(data)

    visitor = ApxNodeVisitor()
    output = visitor.visit(nodes)
    return output

if __name__ == '__main__':    # pragma: no cover

    page = parse_file("examples/test.apx")

    
    print(page['title'])

    print(page.appearance)