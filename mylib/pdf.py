import os

from django.template.loader import render_to_string
from weasyprint import HTML, CSS


def test_generate_pdf(template, data):
    """Generate pdf."""
    # Model data
    # Rendered
    """
from mylib.pdf import test_generate_pdf
imga="https://wsgi.request.africa/media/CACHE/images/4d6c1e59-bc56-46ce-8a2e-593c653cb794/eaad8fc9076600765acc33b414828a58.png"
data={"image":imga, "thedate":"2019-08-09","k":"eqqe","data":[{"value":"Kiss Fm","plays":100,"country":"KE"}],"name":"Nviiri"}
test_generate_pdf("exports/top-5-template.html",data)
    """
    # html_string = render_to_string(template, data)
    # # print(html_string)
    # html = HTML(string=html_string)
    # result = html.write_png("/Users/micha/Documents/mypdf.png")
    # print(result)
    return generate_pdf(template, data, "/Users/micha/Documents/mypdf.png")


def generate_pdf(template, data, file_path, export_type="png", orientation="landscape"):
    if os.path.exists(file_path):
        os.remove(file_path)

    # print(template)
    # print(data)
    html_string = render_to_string(template, data)
    # print(html_string)
    html = HTML(string=html_string)

    # css2 = CSS(url="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css")
    # font = CSS(url="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;800&display=swap")

    if export_type == "pdf":
        result = html.write_pdf(
            file_path,
        )
    elif export_type == "png":
        result = html.write_png(file_path)
    else:
        with open(file_path, "w") as static_file:
            static_file.write(html_string)
    return file_path
