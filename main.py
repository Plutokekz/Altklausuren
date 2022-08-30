import json
import logging
import os
from pprint import pprint
from typing import Tuple
from zipfile import ZipFile
import typesense
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi.routing import Mount
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from database import engine, Document

typesense_host = os.environ['HOST']
typesense_port = os.environ['PORT']
typesense_api_key = os.environ['KEY']

logger = logging.getLogger(__file__)

app = FastAPI(routes=[Mount("/data", StaticFiles(directory="static_data"), name="data"),
                      Mount("/pdf", StaticFiles(directory="scrap"), name="pdf")])

templates = Jinja2Templates(directory='templates')

session = Session(engine)

client = typesense.Client({
    'nodes': [{
        'host': typesense_host,
        'port': typesense_port,
        'protocol': 'http'
    }],
    'api_key': typesense_api_key,
    'connection_timeout_seconds': 2
})


async def genrate_query(query: str) -> Tuple[dict, dict]:
    filter_query = dict(json.loads(query))
    query = filter_query['query']

    filters = []
    checked = {}
    for key, value in filter_query['filters'].items():
        filters.append(f"{key}:= {[option for option in value.keys()]}")
        checked[key] = [option.lower() for option in value.keys()]

    filters = " && ".join(filters)

    search_parameters = {
        'q': query,
        'query_by': "pages",
        'per_page': '20',
        'filter_by': filters,
        'facet_by': 'semester,degree,faculty,course,professors,document_type,filetype,art',
        'max_facet_values': 500
    }
    return search_parameters, checked


def _genrate_query(query: str) -> Tuple[dict, dict]:
    filter_query = dict(json.loads(query))
    query = filter_query['query']

    filters = []
    checked = {}
    for key, value in filter_query['filters'].items():
        filters.append(f"{key}:= {[option for option in value.keys()]}")
        checked[key] = [option.lower() for option in value.keys()]

    filters = " && ".join(filters)

    search_parameters = {
        'q': query,
        'query_by': "pages",
        'per_page': '20',
        'filter_by': filters,
        'facet_by': 'semester,degree,faculty,course,professors,document_type,filetype,art',
        'max_facet_values': 500
    }
    return search_parameters, checked


@app.get('/', response_class=HTMLResponse)
async def index(request: Request):
    search_parameters = {
        'q': "*",
        'query_by': "pages",
        'per_page': '20',
        'facet_by': 'semester,degree,faculty,course,professors,document_type,filetype,art',
        'max_facet_values': 500,
    }
    results = client.collections['klausuren'].documents.search(search_parameters)
    filter_results = {count['field_name']: count['counts'] for count in results['facet_counts']}
    return templates.TemplateResponse("index.html", {"request": request, "filters": filter_results})


@app.get('/edit/{file_id}', response_class=HTMLResponse)
async def edit(request: Request, file_id: str):
    document: Document = session.query(Document).where(Document.id == file_id).first()
    filename = ".".join(document.filename.split(".")[:-1])
    directory = os.sep.join(document.directory.split("\\")[1:])
    print(directory)
    print(filename)
    json_file = f"{filename}.json"
    with open(os.path.join(os.sep.join(document.directory.split("\\")), json_file), "r") as fp:
        meta = dict(json.load(fp))
    for key, value in meta.items():
        print(key, value)
    return templates.TemplateResponse("edit.html", {"request": request,
                                                    "thumbnail": os.path.join(directory, document.filename),
                                                    "meta": meta})


@app.get('/page', response_class=HTMLResponse)
async def new_page(request: Request, page: int, query: str):
    filter_query = dict(json.loads(query))
    query = filter_query['query']

    filters = []
    for key, value in filter_query['filters'].items():
        filters.append(f"{key}:= {[option for option in value.keys()]}")

    filters = {" && ".join(filters)}

    search_parameters = {
        'q': query,
        'query_by': "pages",
        'per_page': '20',
        'filter_by': filters,
        'facet_by': 'semester,degree,faculty,course,professors,document_type,filetype,art',
        'max_facet_values': 500,
        'page': page
    }

    results = client.collections['klausuren'].documents.search(search_parameters)
    return templates.TemplateResponse("elements.html",
                                      {"request": request, "results": results, "num_per_page": 20, "page": page + 1})


def add_to_zip_file(result: dict, file: ZipFile):
    for hit in result['hits']:
        directory = os.sep.join(hit['document']['directory'].split("\\"))
        file.write(os.path.join(directory, hit['document']['filename']))


@app.get("/generate", response_class=RedirectResponse)
def generate_zip_file(request: Request, query: str):
    search_parameters, _ = _genrate_query(query)
    results = client.collections['klausuren'].documents.search(search_parameters)
    with ZipFile("temp/temp.zip", 'w') as zip:
        add_to_zip_file(results, zip)
        if results['found'] > 20:
            num_of_pages = round(results['found'] / results['request_params']['per_page']) + 1
            for i in range(2, num_of_pages):
                search_parameters['page'] = i
                results = client.collections['klausuren'].documents.search(search_parameters)
                add_to_zip_file(results, zip)
    return HTMLResponse("", headers={"HX-Redirect": f"download/{'temp.zip'}"})


@app.get("/download/{name}", response_class=FileResponse)
async def download(request: Request, name: str):
    return FileResponse(f"temp/{name}")


@app.get("/file/{file_id}", response_class=FileResponse)
async def file(request: Request, file_id: str):
    if (document := session.query(Document).where(Document.id == file_id).first()) is not None:
        directory = os.sep.join(document.directory.split("\\"))
        path = os.path.join(directory, document.filename)
        return FileResponse(path)
    logger.error(f"File with id {file_id} not found")
    return FileResponse("scrap/README.txt")


@app.get("/search", response_class=HTMLResponse)
async def search(request: Request, query: str):
    search_parameters, checked = await genrate_query(query)

    results = client.collections['klausuren'].documents.search(search_parameters)

    filter_results = {count['field_name']: count['counts'] for count in results['facet_counts']}
    return templates.TemplateResponse("results.html",
                                      {"request": request, "results": results, "filters": filter_results,
                                       "checked": checked, "query": search_parameters['q'], "num_per_page": 20})


if __name__ == "__main__":
    uvicorn.run("main:app", port=80, reload=True)
