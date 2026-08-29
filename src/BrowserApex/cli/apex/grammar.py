from parsimonious import Grammar, NodeVisitor
from BrowserApex.cli.apex import *
from importlib import resources as impresources
from BrowserApex.cli import apex
from pathlib import Path


class RuleNotImplemented(BaseException):
    pass


class ApxNodeVisitor(NodeVisitor):
    def visit_page_object(self, node, visited_children):
        """ Gets the section name. """
        component_id = visited_children[1]
        body_parts = visited_children[4]
        if type(component_id) is list:
            component_id = component_id[0][1]
        else:
            component_id = None

        page = Page(component_id)
        for item in body_parts:
            if type(item) is tuple:
                if type(item[1]) is dict:
                    page.add_group(item[0], item[1])
                else:
                    page.add_property(item[0], item[1])
            elif isinstance(item, ApexObject):
                page.add_child(item)
            elif item is None:
                continue
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
        component_id = visited_children[2]
        body_parts = visited_children[6]
        if type(component_id) is list:
            component_id = component_id[0][1]
        else:
            component_id = None

        region = Region(component_id)
        for item in body_parts:
            if type(item) is tuple:
                if type(item[1]) is dict:
                    region.add_group(item[0], item[1])
                else:
                    region.add_property(item[0], item[1])
            elif item is None:
                # blanklines
                continue
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
        return ('layout', RegionLayout(d) )
    
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
        return ('appearance', RegionAppearance(d))
    
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

    def visit_region_advanced(self, node, visited_children):
        parts = visited_children[5]
        d = {}
        for item in parts:
            if type(item) is tuple:
                d[item[0]] = item[1]
            else:
                raise RuleNotImplemented()
        return ('advanced', d)
    
    def visit_region_advanced_property_line(self, node, visited_children):
        return visited_children[1]

    def visit_region_advanced_property(self, node, visited_children):
        v = visited_children[0]
        match v[0].text:
            case 'htmlDomId':
                return (v[0].text, v[3])
            case _:
                raise RuleNotImplemented()


    def visit_page_item(self, node, visited_children):
        component_id = visited_children[2]
        body_parts = visited_children[6]
        if type(component_id) is list:
            component_id = component_id[0][1]
        else:
            component_id = None

        page_item = PageItem(component_id)
        for item in body_parts:
            if type(item) is tuple:
                if type(item[1]) is dict:
                    page_item.add_group(item[0], item[1])
                elif isinstance(item[1], ApexGroup):
                    page_item.add_group(item[0], item[1])
                else:
                    page_item.add_property(item[0], item[1])
            elif item is None:
                continue
            else:
                raise RuleNotImplemented(f"unprocessed: {item}")
        return page_item

    def visit_page_item_body_line(self, node, visited_children):
        return visited_children[0]

    def visit_page_item_direct_property_line(self, node, visited_children):
        return visited_children[1]

    def visit_page_item_direct_property(self, node, visited_children):
        v = visited_children[0]
        title, _, _, value = v
        return (title.text, value)

    def visit_page_item_group_block(self, node, visited_children):
        return visited_children[0]


    def visit_page_item_label(self, node, visited_children):
        parts = visited_children[5]
        d = {}
        for item in parts:
            if type(item) is tuple:
                d[item[0]] = item[1]
            else:
                raise RuleNotImplemented()
        return ('label', PageItemLabel(d) )
    
    def visit_page_item_label_property_line(self, node, visited_children):
        return visited_children[1]

    def visit_page_item_label_property(self, node, visited_children):
        v = visited_children[0]
        match v[0].text:
            case 'sequence' | 'label':
                return (v[0].text, v[3])
            case 'alignment' | 'duplicateSubmissionUrl':
                return (v[0].text, v[3][0].text)
            case _:
                raise RuleNotImplemented()


    def visit_page_item_settings(self, node, visited_children):
        parts = visited_children[5]
        d = {}
        for item in parts:
            if type(item) is tuple:
                d[item[0]] = item[1]
            else:
                raise RuleNotImplemented()
        return ('settings', PageItemSettings(d) )
    
    def visit_page_item_settings_property_line(self, node, visited_children):
        return visited_children[1]

    def visit_page_item_settings_property(self, node, visited_children):
        v = visited_children[0]
        match v[0].text:
            # case 'sequence' | 'label':
            #     return (v[0].text, v[3])
            case 'trimSpaces':
                return (v[0].text, v[3][0].text)
            case _:
                raise RuleNotImplemented()

    def visit_page_item_session_state(self, node, visited_children):
        parts = visited_children[5]
        d = {}
        for item in parts:
            if type(item) is tuple:
                d[item[0]] = item[1]
            else:
                raise RuleNotImplemented()
        return ('sessionState', PageItemSessionState(d) )
    
    def visit_page_item_session_state_property_line(self, node, visited_children):
        return visited_children[1]

    def visit_page_item_session_state_property(self, node, visited_children):
        v = visited_children[0]
        match v[0].text:
            # case 'sequence' | 'label':
            #     return (v[0].text, v[3])
            case 'dataType' | 'storage':
                return (v[0].text, v[3][0].text)
            case _:
                raise RuleNotImplemented()


    def visit_page_item_layout(self, node, visited_children):
        parts = visited_children[5]
        d = {}
        for item in parts:
            if type(item) is tuple:
                d[item[0]] = item[1]
            else:
                raise RuleNotImplemented()
        return ('layout', PageItemLayout(d) )
    
    def visit_page_item_layout_property_line(self, node, visited_children):
        return visited_children[1]

    def visit_page_item_layout_property(self, node, visited_children):
        v = visited_children[0]
        match v[0].text:
            case 'sequence' | 'slot' | 'region':
                return (v[0].text, v[3])
            case 'alignment':
                return (v[0].text, v[3][0].text)
            case 'enableMetaTags' | 'enableDuplicatePageSubmissions':
                return (v[0].text, v[3])
            case _:
                raise RuleNotImplemented()

    def visit_page_item_appearance(self, node, visited_children):
        parts = visited_children[5]
        d = {}
        for item in parts:
            if type(item) is tuple:
                d[item[0]] = item[1]
            else:
                raise RuleNotImplemented()
        return ('appearance', PageItemAppearance(d) )
    
    def visit_page_item_appearance_property_line(self, node, visited_children):
        return visited_children[1]

    def visit_page_item_appearance_property(self, node, visited_children):
        v = visited_children[0]
        match v[0].text:
            case 'template' | 'cssClasses' | 'width' | 'valuePlaceholder':
                return (v[0].text, v[3])
            case 'templateOptions':
                return (v[0].text, v[3][0])
            case _:
                raise RuleNotImplemented()

    def visit_page_item_validation(self, node, visited_children):
        parts = visited_children[5]
        d = {}
        for item in parts:
            if type(item) is tuple:
                d[item[0]] = item[1]
            else:
                raise RuleNotImplemented()
        return ('validation', PageItemValidation(d) )
    
    def visit_page_item_validation_property_line(self, node, visited_children):
        return visited_children[1]

    def visit_page_item_validation_property(self, node, visited_children):
        v = visited_children[0]
        match v[0].text:
            case 'valueRequired' | 'maxLength':
                return (v[0].text, v[3])
            case '?':
                return (v[0].text, v[3][0])
            case _:
                raise RuleNotImplemented()

    def visit_page_item_advanced(self, node, visited_children):
        parts = visited_children[5]
        d = {}
        for item in parts:
            if type(item) is tuple:
                d[item[0]] = item[1]
            else:
                raise RuleNotImplemented()
        return ('advanced', PageItemAdvanced(d) )
    
    def visit_page_item_advanced_property_line(self, node, visited_children):
        return visited_children[1]

    def visit_page_item_advanced_property(self, node, visited_children):
        v = visited_children[0]
        match v[0].text:
            case 'customAttributes':
                return (v[0].text, v[3])
            case 'postText':
                return (v[0].text, v[3][0])
            case _:
                raise RuleNotImplemented()


    def visit_page_item_security(self, node, visited_children):
        parts = visited_children[5]
        d = {}
        for item in parts:
            if type(item) is tuple:
                d[item[0]] = item[1]
            else:
                raise RuleNotImplemented()
        return ('security', PageItemSecurity(d) )
    
    def visit_page_item_security_property_line(self, node, visited_children):
        return visited_children[1]

    def visit_page_item_security_property(self, node, visited_children):
        v = visited_children[0]
        match v[0].text:
            case 'encryptSessionState':
                return (v[0].text, v[3])
            case 'sessionStateProtection' | 'restrictedChars':
                return (v[0].text, v[3][0])
            case _:
                raise RuleNotImplemented()

    def visit_button(self, node, visited_children):
        component_id = visited_children[2]
        body_parts = visited_children[6]
        if type(component_id) is list:
            component_id = component_id[0][1]
        else:
            component_id = None

        button = Button(component_id)
        for item in body_parts:
            if type(item) is tuple:
                if type(item[1]) is dict:
                    button.add_group(item[0], item[1])
                elif isinstance(item[1], ApexGroup):
                    button.add_group(item[0], item[1])
                else:
                    button.add_property(item[0], item[1])
            elif item is None:
                continue
            else:
                raise RuleNotImplemented(f"unprocessed: {item}")
        return button

    def visit_button_body_line(self, node, visited_children):
        return visited_children[0]

    def visit_button_direct_property_line(self, node, visited_children):
        return visited_children[1]

    def visit_button_direct_property(self, node, visited_children):
        v = visited_children[0]
        title, _, _, value = v
        return (title.text, value)

    def visit_button_group_block(self, node, visited_children):
        return visited_children[0]

    def visit_button_layout(self, node, visited_children):
        parts = visited_children[5]
        d = {}
        for item in parts:
            if type(item) is tuple:
                d[item[0]] = item[1]
            else:
                raise RuleNotImplemented()
        return ('layout', ButtonLayout(d) )
    
    def visit_button_layout_property_line(self, node, visited_children):
        return visited_children[1]

    def visit_button_layout_property(self, node, visited_children):
        v = visited_children[0]
        match v[0].text:
            # case 'sequence' | 'slot' | 'region':
            #     return (v[0].text, v[3])
            # case 'alignment':
            #     return (v[0].text, v[3][0].text)
            # case 'enableMetaTags' | 'enableDuplicatePageSubmissions':
            #     return (v[0].text, v[3])
            case _:
                raise RuleNotImplemented()


    def visit_button_appearance(self, node, visited_children):
        parts = visited_children[5]
        d = {}
        for item in parts:
            if type(item) is tuple:
                d[item[0]] = item[1]
            else:
                raise RuleNotImplemented()
        return ('appearance', ButtonAppearance(d) )
    
    def visit_button_appearance_property_line(self, node, visited_children):
        return visited_children[1]

    def visit_button_appearance_property(self, node, visited_children):
        v = visited_children[0]
        match v[0].text:
            case 'buttonTemplate' | 'hot':
                 return (v[0].text, v[3])
            # case 'alignment':
            #     return (v[0].text, v[3][0].text)
            # case 'templateOptions' | 'enableDuplicatePageSubmissions':
            #     return (v[0].text, v[3])
            case 'templateOptions':
                return (v[0].text, v[3][0])
            case _:
                raise RuleNotImplemented()

    def visit_button_behavior(self, node, visited_children):
        parts = visited_children[5]
        d = {}
        for item in parts:
            if type(item) is tuple:
                d[item[0]] = item[1]
            else:
                raise RuleNotImplemented()
        return ('behavior', ButtonBehavior(d) )
    
    def visit_button_behavior_property_line(self, node, visited_children):
        return visited_children[1]

    def visit_button_behavior_property(self, node, visited_children):
        v = visited_children[0]
        match v[0].text:
            case 'warnOnUnsavedChanges':
                 return (v[0].text, v[3])
            # case 'alignment':
            #     return (v[0].text, v[3][0].text)
            # case 'enableMetaTags' | 'enableDuplicatePageSubmissions':
            #     return (v[0].text, v[3])
            case _:
                raise RuleNotImplemented()


    def visit_dynamic_action(self, node, visited_children):
        component_id = visited_children[2]
        body_parts = visited_children[6]
        if type(component_id) is list:
            component_id = component_id[0][1]
        else:
            component_id = None

        dynact = DynamicAction(component_id)
        for item in body_parts:
            if type(item) is tuple:
                if type(item[1]) is dict:
                    dynact.add_group(item[0], item[1])
                elif isinstance(item[1], ApexGroup):
                    dynact.add_group(item[0], item[1])
                else:
                    dynact.add_property(item[0], item[1])
            elif isinstance(item, ApexObject):
                dynact.add_child(item)
            elif item is None:
                continue
            else:
                raise RuleNotImplemented(f"unprocessed: {item}")
        return dynact

    def visit_dynamic_action_body_line(self, node, visited_children):
        return visited_children[0]

    def visit_dynamic_action_direct_property_line(self, node, visited_children):
        return visited_children[1]

    def visit_dynamic_action_direct_property(self, node, visited_children):
        v = visited_children[0]
        title, _, _, value = v
        return (title.text, value)

    def visit_dynamic_action_group_block(self, node, visited_children):
        return visited_children[0]

    def visit_dynamic_action_execution(self, node, visited_children):
        parts = visited_children[5]
        d = {}
        for item in parts:
            if type(item) is tuple:
                d[item[0]] = item[1]
            else:
                raise RuleNotImplemented()
        return ('execution', DynamicActionExecution(d) )
    
    def visit_dynamic_action_execution_property_line(self, node, visited_children):
        return visited_children[1]

    def visit_dynamic_action_execution_property(self, node, visited_children):
        v = visited_children[0]
        match v[0].text:
            case 'sequence':
                    return (v[0].text, v[3])
            # case 'alignment':
            #     return (v[0].text, v[3][0].text)
            # case 'enableMetaTags' | 'enableDuplicatePageSubmissions':
            #     return (v[0].text, v[3])
            case _:
                raise RuleNotImplemented()
            
    def visit_dynamic_action_when(self, node, visited_children):
        parts = visited_children[5]
        d = {}
        for item in parts:
            if type(item) is tuple:
                d[item[0]] = item[1]
            else:
                raise RuleNotImplemented()
        return ('when', DynamicActionWhen(d) )
    
    def visit_dynamic_action_when_property_line(self, node, visited_children):
        return visited_children[1]

    def visit_dynamic_action_when_property(self, node, visited_children):
        v = visited_children[0]
        match v[0].text:
            case 'event':
                return (v[0].text, v[3])
            # case 'alignment':
            #     return (v[0].text, v[3][0].text)
            # case 'enableMetaTags' | 'enableDuplicatePageSubmissions':
            #     return (v[0].text, v[3])
            case _:
                raise RuleNotImplemented()

    def visit_dynamic_action_client_side_condition(self, node, visited_children):
        parts = visited_children[5]
        d = {}
        for item in parts:
            if type(item) is tuple:
                d[item[0]] = item[1]
            else:
                raise RuleNotImplemented()
        return ('clientSideCondition', DynamicActionClientSideCondition(d) )
    
    def visit_dynamic_action_client_side_condition_property_line(self, node, visited_children):
        return visited_children[1]

    def visit_dynamic_action_client_side_condition_property(self, node, visited_children):
        v = visited_children[0]
        match v[0].text:
            case 'event' | 'javaScriptExpression':
                return (v[0].text, v[3])
            case 'type':
                return (v[0].text, v[3][0].text)
            # case 'enableMetaTags' | 'enableDuplicatePageSubmissions':
            #     return (v[0].text, v[3])
            case _:
                raise RuleNotImplemented()

    def visit_action_c(self, node, visited_children):
        component_id = visited_children[2]
        body_parts = visited_children[6]
        if type(component_id) is list:
            component_id = component_id[0][1]
        else:
            component_id = None

        act = Action(component_id)
        for item in body_parts:
            if type(item) is tuple:
                if type(item[1]) is dict:
                    act.add_group(item[0], item[1])
                elif isinstance(item[1], ApexGroup):
                    act.add_group(item[0], item[1])
                else:
                    act.add_property(item[0], item[1])
            elif item is None:
                continue
            else:
                raise RuleNotImplemented(f"unprocessed: {item}")
        return act

    def visit_action_c_body_line(self, node, visited_children):
        return visited_children[0]

    def visit_action_c_direct_property_line(self, node, visited_children):
        return visited_children[1]

    def visit_action_c_direct_property(self, node, visited_children):
        v = visited_children[0]
        title, _, _, value = v
        return (title.text, value)

    def visit_action_c_group_block(self, node, visited_children):
        return visited_children[0]

    def visit_action_c_affected_elements(self, node, visited_children):
        parts = visited_children[5]
        d = {}
        for item in parts:
            if type(item) is tuple:
                d[item[0]] = item[1]
            else:
                raise RuleNotImplemented()
        return ('affectedElements', ActionAffectedElements(d) )
    
    def visit_action_c_affected_elements_property_line(self, node, visited_children):
        return visited_children[1]

    def visit_action_c_affected_elements_property(self, node, visited_children):
        v = visited_children[0]
        match v[0].text:
            case 'selectionType' | 'items':
                return (v[0].text, v[3])
            # case 'alignment':
            #     return (v[0].text, v[3][0].text)
            # case 'enableMetaTags' | 'enableDuplicatePageSubmissions':
            #     return (v[0].text, v[3])
            case _:
                raise RuleNotImplemented()

    def visit_action_c_execution(self, node, visited_children):
        parts = visited_children[5]
        d = {}
        for item in parts:
            if type(item) is tuple:
                d[item[0]] = item[1]
            else:
                raise RuleNotImplemented()
        return ('execution', ActionExecution(d) )
    
    def visit_action_c_execution_property_line(self, node, visited_children):
        return visited_children[1]

    def visit_action_c_execution_property(self, node, visited_children):
        v = visited_children[0]
        match v[0].text:
            case 'sequence' | 'fireWhenEventResultIs':
                return (v[0].text, v[3])
            # case 'alignment':
            #     return (v[0].text, v[3][0].text)
            # case 'enableMetaTags' | 'enableDuplicatePageSubmissions':
            #     return (v[0].text, v[3])
            case _:
                raise RuleNotImplemented()



    def visit_process(self, node, visited_children):
        component_id = visited_children[2]
        body_parts = visited_children[6]
        if type(component_id) is list:
            component_id = component_id[0][1]
        else:
            component_id = None

        proc = Process(component_id)
        for item in body_parts:
            if type(item) is tuple:
                if type(item[1]) is dict:
                    proc.add_group(item[0], item[1])
                elif isinstance(item[1], ApexGroup):
                    proc.add_group(item[0], item[1])
                else:
                    proc.add_property(item[0], item[1])
            elif item is None:
                continue
            else:
                raise RuleNotImplemented(f"unprocessed: {item}")
        return proc

    def visit_process_body_line(self, node, visited_children):
        return visited_children[0]

    def visit_process_direct_property_line(self, node, visited_children):
        return visited_children[1]

    def visit_process_direct_property(self, node, visited_children):
        v = visited_children[0]
        title, _, _, value = v
        return (title.text, value)

    def visit_process_group_block(self, node, visited_children):
        return visited_children[0]


    def visit_reference(self, node, visited_children):
        return node.text


    def visit_code_block(self, node, visited_children):
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

    def visit_blank_lines(self, node, visited_children):
            return None
    
    
    def generic_visit(self, node, visited_children):
        """ The generic visit method. """
        return visited_children or node



def parse_apex_file(fn: Path, apex_version : str = "26.1") -> Page:
    inp_file = impresources.files(apex) / f'apexlang-{apex_version}.peg'
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

    page = Page('A')

    page_item = PageItem('B')

    page = parse_apex_file("examples/test.apx")


    
    print(page)

    print(page.appearance)