list_params = {
    "primary_key" : True,
    "max_length": True,
    "description": True,
    'null': True,
    'blank': True,
    'default': True,
    'choices': True,
    'verbose_name': True,
    'help_text': True,
    'unique': True,
    'db_index': True,
    'editable': True,
    'max_length': True,
    'upload_to': True,
    'on_delete': True,
}

django_model_types = {
    "integer": "models.IntegerField",
    "string": "models.CharField",
    "text": "models.TextField",
    "boolean": "models.BooleanField",
    "date": "models.DateField",
    "uuid": "models.UUIDField",
    "datetime": "models.DateTimeField",
    "time": "models.TimeField",
    "foreign_key": "models.Foreignkey"
}

only_value_params = {
    "foreign_table": True
}

def getParsedData(data):
    model_array = []
    for i in data["tables"]:
        table_name = i["name"]
        columns = i["columns"]
        model_output = ""
        class_name = "class " + table_name + "(models.Model):"
        model_output += class_name + "\n"
        for j in columns:
            if j["type"] in django_model_types:
                field_name = django_model_types[j["type"]]
                params = "("
                for param in only_value_params:
                    if param in j:
                        params += str(j[param]) + ","
                for param in list_params:
                    if param in j:
                        params += str(param) + "=" + str(j[param]) + ","
                params += ")"
                query = "    " + j["name"] + "=" + field_name + params
                model_output += query + "\n"
        model_array.append(model_output)
    return model_array