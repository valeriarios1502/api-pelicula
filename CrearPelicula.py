import boto3
import uuid
import os
import json
from botocore.exceptions import ClientError


def log(tipo, log_datos): # log estandar en formato json
    log_estandar = {
        'tipo': tipo,
        'log_datos': log_datos
    }
    print(json.dumps(log_estandar, default=str))


def lambda_handler(event, context):
    try: 
        # Entrada (json)
        log('INFO', {'mensaje': 'Evento recibido', 'event': event})

        tenant_id = event['body']['tenant_id']
        pelicula_datos = event['body']['pelicula_datos']
        nombre_tabla = os.environ["TABLE_NAME"]

        # Proceso
        uuidv4 = str(uuid.uuid4())
        pelicula = {
            'tenant_id': tenant_id,
            'uuid': uuidv4,
            'pelicula_datos': pelicula_datos
        }

        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(nombre_tabla)
        response = table.put_item(Item=pelicula)

        # Salida (json) - log de ejecución correcta
        log('INFO', {
            'mensaje': 'Pelicula guardada exitosamente',
            'pelicula': pelicula,
            'response': response
        })

        return {
            'statusCode': 200,
            'pelicula': pelicula,
            'response': response
        }

    except KeyError as e:
        # Error por campos faltantes
        log('ERROR', {
            'mensaje': 'Falta un campo requerido',
            'error': str(e),
            'tipo_error': type(e).__name__
        })
        return {
            'statusCode': 400,
            'error': f'Falta el campo requerido: {str(e)}'
        }

    except ClientError as e:
        # Error propio de servicios AWS 
        log('ERROR', {
            'mensaje': 'Error al interactuar con servicios',
            'error': str(e),
            'tipo_error': type(e).__name__,
            'codigo_error': e.response.get('Error', {}).get('Code', 'Desconocido')
        })
        return {
            'statusCode': 500,
            'error': 'Error al guardar la pelicula en la base de datos'
        }

    except Exception as e:
        # Cualquier otro error 
        log('ERROR', {
            'mensaje': 'Error en la ejecución',
            'error': str(e),
            'tipo_error': type(e).__name__
        })
        return {
            'statusCode': 500,
            'error': 'Error interno del servidor'
        }
