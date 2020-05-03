import kfp


def create_load_data_component():
    component = kfp.components.load_component_from_file('./components/loaddata/component.yaml')
    return component


def pipeline():
    load_data_component = create_load_data_component()
    load_data_task = load_data_component(
        # Input name "Input 1" is converted to pythonic parameter name "input_1" # note the converted name here
        aws_access_key_id='',
        aws_secret_access_key='',
        output_path=''
    )


kfp.Client().create_run_from_pipeline_func(pipeline, arguments={})
