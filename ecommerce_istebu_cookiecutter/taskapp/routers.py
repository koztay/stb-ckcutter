

def route_task(name, args, kwargs, options, task=None, **kw):
    if name == 'my_importer.tasks.process_dict':
        return {'exchange': 'xml_updater',
                'exchange_type': 'direct',
                'routing_key': 'xml_updater'}
    elif name == 'my_importer.tasks.run_all_steps':
        return {'exchange': 'xml_updater',
                'exchange_type': 'direct',
                'routing_key': 'xml_updater'}
    elif name == 'my_importer.tasks.download_xml_image_for_product':
        return {'exchange': 'xml_updater',
                'exchange_type': 'direct',
                'routing_key': 'image_downloader'}
    elif name == 'importer.tasks.download_image_for_product':
        print("async download_image_for_product")
        return {'exchange': 'xml_updater',
                'exchange_type': 'direct',
                'routing_key': 'image_downloader'}

    elif name == 'importer.tasks.process_xls_row':
        print("async process_xls_row çalıştı")
        return {'exchange': 'xml_updater',
                'exchange_type': 'direct',
                'routing_key': 'xml_updater'}
