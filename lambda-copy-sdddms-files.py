import json, boto3

aws_access_key_id = ''
aws_secret_access_key = ''
region_name = 'sa-east-1'

s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name=region_name)

def copiar_arquivos_origin(bucket, origem_prefixo, destino_prefixo):
    try:
        objetos = s3.list_objects(Bucket=bucket, Prefix=origem_prefixo)

        for objeto in objetos.get('Contents', []):
            chave_origem = objeto['Key']
            chave_destino = chave_origem.replace(origem_prefixo, destino_prefixo)

            s3.copy_object(Bucket=bucket, CopySource={'Bucket': bucket, 'Key': chave_origem}, Key=chave_destino)

        print("Dados copiados com sucesso!")

    except Exception as e:
        return {
            'statusCode': 400,
            'body': json.dumps(str(e))
        }

def copiar_arquivos_csv2rdf(bucket, origem_prefixo, destino_prefixo, lista_arquivos):
    try:
        # Copiar cada arquivo para a pasta de destino
        for arquivo in lista_arquivos:
            if arquivo.startswith('RDF'):
                destino_prefixo = destino_prefixo + "rdf/"
            chave_origem = f"{origem_prefixo}/{arquivo}"
            chave_destino = f"{destino_prefixo}{arquivo}"

            s3.copy_object(Bucket=bucket, CopySource={'Bucket': bucket, 'Key': chave_origem}, Key=chave_destino)
            print(f"{arquivo} copiado")

    except Exception as e:
        return {
            'statusCode': 400,
            'body': json.dumps(str(e))
        }

def lambda_handler(event, context):
    id_exec = event["id_exec"]

    bucket = 'bucket-rdf'
    origem_prefixo = 'jar/origin/'
    destino_prefixo = f'jar/{id_exec}/'

    copiar_arquivos_origin(bucket, origem_prefixo, destino_prefixo)

    origem_prefixo = f'files/{id_exec}'
    lista_arquivos = ["mapping.jsonld", "ontology.owl", f"RDF_{id_exec}.ntriples"]

    copiar_arquivos_csv2rdf(bucket, origem_prefixo, destino_prefixo, lista_arquivos)

    return {
        'statusCode': 200,
        'body': json.dumps('Arquivos copiados com sucesso')
    }
