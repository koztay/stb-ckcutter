from django.template.loader import render_to_string


def product_xml_serialize(query_set):
    xml = render_to_string('xml_export_template.xml', {'query_set': query_set})

    return xml
