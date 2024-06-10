from flask import Flask
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient
import os

endpoint = "https://mycustom-nertext.cognitiveservices.azure.com/"
key = os.environ.get('LANGUAGE_KEY')
ner_project_name = "mycustomnerlanguage"
ner_deployment_name = "mycustomnermodeldeploy"
classify_project_name = "customcommandclassify"
classify_deployment_name = "customnclassifymodeldeploy"

app = Flask(__name__)

text_analytics_client = TextAnalyticsClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(key),
    )

@app.route('/api/<string:vcommand>', methods=['GET'])
def getMovieByTitle2(vcommand) :
    print("input: "+ vcommand)
    vals = [vcommand]

    poller = text_analytics_client.begin_recognize_custom_entities(
        vals,
        project_name=ner_project_name,
        deployment_name=ner_deployment_name
    )

    poller_classify = text_analytics_client.begin_single_label_classify(
        vals,
        project_name=classify_project_name,
        deployment_name=classify_deployment_name
    )

    document_results = poller.result()
    entities = []
    for custom_entities_result in document_results:

        if custom_entities_result.kind == "CustomEntityRecognition":
            for entity in custom_entities_result.entities:
                print(
                    "Entity '{}' has category '{}' with confidence score of '{}'".format(
                        entity.text, entity.category, entity.confidence_score
                    )
                )
                entities.append({'text': entity.text, "category": entity.category})
        elif custom_entities_result.is_error is True:
            print("...Is an error with code '{}' and message '{}'".format(
                custom_entities_result.error.code, custom_entities_result.error.message
                )
            )
    commandType = ""
    document_results_classify = poller_classify.result()
    for doc, classification_result in zip(vals, document_results_classify):
        if classification_result.kind == "CustomDocumentClassification":
            classification = classification_result.classifications[0]
            print("The document text '{}' was classified as '{}' with confidence score {}.".format(
                doc, classification.category, classification.confidence_score)
            )
            commandType = classification.category
        elif classification_result.is_error is True:
            print("Document text '{}' has an error with code '{}' and message '{}'".format(
                doc, classification_result.error.code, classification_result.error.message
            ))
    
    return {'commandType': commandType, 'entities': entities}