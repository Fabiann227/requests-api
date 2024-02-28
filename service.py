from flask import Flask, jsonify
from flask_restful import Api, Resource, reqparse
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
from pymongo import MongoClient

app = Flask(__name__)
CORS(app)

# Setup MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['tes']
collection = db['requests']

# Setup Flask-RESTful
api = Api(app)

# Define endpoints
class Requests(Resource):
    def get(self):
        data = list(collection.find({}, {'_id': 0}))
        return jsonify(data)

class Upload(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('assignee', type=str, required=True, help='Nama penerima tugas')
        parser.add_argument('deadline', type=str, required=True, help='Batas waktu untuk menyelesaikan tugas')
        parser.add_argument('division', type=str, required=True, help='Divisi yang mengirimkan permintaan')
        parser.add_argument('domain', type=str, required=True, help='Domain terkait permintaan')
        parser.add_argument('link', type=str, required=True, help='Link terkait permintaan')
        parser.add_argument('note', type=str, required=True, help='Catatan tambahan')
        parser.add_argument('request_name', type=str, required=True, help='Nama pengirim permintaan')
        parser.add_argument('status', type=str, required=True, help='Status permintaan')
        parser.add_argument('tag', type=str, action='append', required=True, help='Tag-tag terkait permintaan')
        parser.add_argument('list_input', type=dict, action='append', required=True, help='List input')
        args = parser.parse_args()
        
        # Mengakses nilai tag dan list_input dari args dengan benar
        tag = args.pop('tag')
        list_input = args.pop('list_input')
        
        # Mengonversi list_input ke dalam format yang diharapkan
        list_input_formatted = [{'input': item['input'], 'output': item['output']} for item in list_input]
        
        # Menggabungkan kembali nilai tag dan list_input ke dalam args
        args['tag'] = tag
        args['list_input'] = list_input_formatted
        
        inserted_data = collection.insert_one(args)
        
        return {"message": "Data berhasil diupload", "id": str(inserted_data.inserted_id), "status": "Selesai"}
    
# Assign Resources to routes
api.add_resource(Requests, '/api/requests')
api.add_resource(Upload, '/api/upload')

# Generate OpenAPI Specification dynamically
def generate_openapi_spec():
    spec = {
        "openapi": "3.0.0",
        "info": {
            "title": "Tes API",
            "version": "1.0.0",
            "description": "API Tes"
        },
        "paths": {
            "/api/requests": {
                "get": {
                    "summary": "Get data",
                    "responses": {
                        "200": {
                            "description": "Daftar semua data"
                        }
                    }
                }
            },
            "/api/upload": {
                "post": {
                    "summary": "Create data",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "assignee": {
                                            "type": "string",
                                            "description": "Nama penerima tugas"
                                        },
                                        "deadline": {
                                            "type": "string",
                                            "description": "Batas waktu untuk menyelesaikan tugas"
                                        },
                                        "division": {
                                            "type": "string",
                                            "description": "Divisi yang mengirimkan permintaan"
                                        },
                                        "domain": {
                                            "type": "string",
                                            "description": "Domain terkait permintaan"
                                        },
                                        "link": {
                                            "type": "string",
                                            "description": "Link terkait permintaan"
                                        },
                                        "note": {
                                            "type": "string",
                                            "description": "Catatan tambahan"
                                        },
                                        "request_name": {
                                            "type": "string",
                                            "description": "Nama pengirim permintaan"
                                        },
                                        "status": {
                                            "type": "string",
                                            "description": "Status permintaan"
                                        },
                                        "tag": {
                                            "type": "array",
                                            "items": {
                                                "type": "string"
                                            },
                                            "description": "Tag-tag terkait permintaan"
                                        },
                                        "list_input": {
                                            "type": "array",
                                            "items": {
                                                "type": "object",
                                                "properties": {
                                                    "input": {
                                                        "type": "string",
                                                        "description": "Input"
                                                    },
                                                    "output": {
                                                        "type": "string",
                                                        "description": "Output yang ditampilkan akan muncul disini ketika memilih input"
                                                    }
                                                }
                                            },
                                            "description": "List input"
                                        }
                                    },
                                    "required": ["assignee", "deadline", "division", "domain", "link", "note", "request_name", "status", "tag", "list_input"]
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Data berhasil diupload",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "message": {
                                                "type": "string"
                                            },
                                            "id": {
                                                "type": "string"
                                            },
                                            "status": {
                                                "type": "string"
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    return spec


# Route to serve OpenAPI Specification
@app.route('/api/swagger.json')
def serve_openapi_spec():
    spec = generate_openapi_spec()
    return jsonify(spec)

# Configure Swagger UI blueprint
SWAGGER_URL = '/api/docs'
API_URL = '/api/swagger.json'
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={'app_name': "Tes API Documentation"}
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

if __name__ == '__main__':
    app.run(debug=True)
