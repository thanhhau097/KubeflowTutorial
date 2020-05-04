import kfp


def create_load_data_component():
    component = kfp.components.load_component_from_file('./components/loaddata/component.yaml')
    return component


def create_ocr_preprocess_component():
    component = kfp.components.load_component_from_file('./components/ocr/ocrpreprocess/component.yaml')
    return component


@kfp.dsl.pipeline(
  name='My pipeline',
  description='My machine learning pipeline'
)
def pipeline():
    load_data_component = create_load_data_component()
    load_data_task = load_data_component(
        # Input name "Input 1" is converted to pythonic parameter name "input_1" # note the converted name here
        aws_access_key_id='AKIAXYIULNYY2WOJ2FLD',
        aws_secret_access_key='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',
    )

    # output_path of load data component must be same as input_path of ocr preprocess component
    ocr_preprocess_component = create_ocr_preprocess_component()
    ocr_preprocess_task = ocr_preprocess_component(
        # input_path=load_data_task.outputs['output_path'],
    )


# kfp.Client().create_run_from_pipeline_func(pipeline, arguments={})
kfp.compiler.Compiler().compile(pipeline, 'my-pipeline.zip')
client = kfp.Client()
my_experiment = client.create_experiment(name='demo')
my_run = client.run_pipeline(my_experiment.id, 'my-pipeline', 'my-pipeline.zip')