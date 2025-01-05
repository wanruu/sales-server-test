import os
import json
import datetime
import shutil
from bs4 import BeautifulSoup as bs


# - report
#   - testcases
#     - testcase1
#       - index.html
#       - step1.html
#   - testcases.json
#   - index.html
# - static
#   - css
#   - images
#   - js

_ROOT_DIR_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_REPORT_DIR_PATH = os.path.join(_ROOT_DIR_PATH, "report")
_TESTCASES_DIR_PATH = os.path.join(_REPORT_DIR_PATH, "testcases")
_RECENT_FILE_PATH = os.path.join(_REPORT_DIR_PATH, "recent.json")

# static files
_STATIC_DIR_PATH = os.path.join(_ROOT_DIR_PATH, "static")
_CSS_DIR_PATH = os.path.join(_STATIC_DIR_PATH, "css")
_IMG_DIR_PATH = os.path.join(_STATIC_DIR_PATH, "images")
_JS_DIR_PATH = os.path.join(_STATIC_DIR_PATH, "js")
_TEMPLATE_DIR_PATH = os.path.join(_STATIC_DIR_PATH, "templates")

_MAX_TESTCASE_NUM = 20


# auto include base.css, script.js
def gen_html_head(title, cur_dirpath):
    base_css = os.path.join(_CSS_DIR_PATH, "base.css")
    script = os.path.join(_JS_DIR_PATH, "script.js")
    relative_base_css = os.path.relpath(base_css, cur_dirpath)
    relative_script = os.path.relpath(script, cur_dirpath)
    return bs(
        f"""<title>{title}</title>
    <link rel="stylesheet" href="{relative_base_css}">
    <script src="{relative_script}"></script>""",
        "html.parser",
    )


def get_svg(success: bool, cur_dirpath):
    svg_name = "success" if success else "failed"
    svg_path = os.path.join(_IMG_DIR_PATH, f"{svg_name}.svg")
    relative_svg_path = os.path.relpath(svg_path, cur_dirpath)
    return bs(
        f'<img src="{relative_svg_path}" width="20" height="20" />', "html.parser"
    )


class Recent:
    def __init__(self):
        self.__load()
        self.__clean_old_testcases()

    @property
    def data(self):
        return self.__data

    def add(self, name, dirname, date, total_steps, success_steps):
        self.__data.insert(
            0,
            {
                "name": name,
                "dirname": dirname,
                "date": date,
                "total_steps": total_steps,
                "success_steps": success_steps,
            },
        )
        if len(self.__data) > _MAX_TESTCASE_NUM:
            self.__data = self.__data[:_MAX_TESTCASE_NUM]

    def save(self):
        with open(_RECENT_FILE_PATH, "w+") as f:
            json.dump(self.__data, f)

    def __clean_old_testcases(self):
        if (os.path.exists(_TESTCASES_DIR_PATH)):
            whitelist_dirnames = [t["dirname"] for t in self.__data]
            existing_dirnames = [
                os.path.basename(dirname)
                for dirname in os.listdir(_TESTCASES_DIR_PATH)
                if os.path.isdir(os.path.join(_TESTCASES_DIR_PATH, dirname))
            ]
            for dirname in existing_dirnames:
                if dirname not in whitelist_dirnames:
                    shutil.rmtree(os.path.join(_TESTCASES_DIR_PATH, dirname))
            for dirname in whitelist_dirnames:
                if not os.path.exists(os.path.join(_TESTCASES_DIR_PATH, dirname)):
                    whitelist_dirnames.remove(dirname)

    def __load(self):
        try:
            with open(_RECENT_FILE_PATH, "r") as f:
                self.__data = json.load(f)
        except Exception:
            self.__data = []


class HtmlSaver:
    def __init__(self):
        self.__recent = Recent()  # time desc
        self.__new_testcases = []  # time asc
        with open(os.path.join(_TEMPLATE_DIR_PATH, "step.html"), "r") as f:
            self.__step_html = f.read()
        with open(os.path.join(_TEMPLATE_DIR_PATH, "testcase.html"), "r") as f:
            self.__testcase_html = f.read()
        with open(os.path.join(_TEMPLATE_DIR_PATH, "report.html"), "r") as f:
            self.__report_html = f.read()

    def add_testcase(self, testcase):
        self.__recent.add(
            testcase.name,
            testcase.dirname,
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            len(testcase.steps),
            sum(1 for step in testcase.steps if step.success),
        )
        self.__new_testcases.append(testcase)

    def save(self):
        self.__prepare_save()
        self.__recent.save()

        # report: index.html
        with open(os.path.join(_REPORT_DIR_PATH, "index.html"), "w+") as f:
            f.write(self.__gen_index_html_body(_REPORT_DIR_PATH))

        # testcase: index.html, step1.html, step2.html, ...
        for idx, testcase in enumerate(self.__new_testcases):
            # normal
            testcase_dirpath = os.path.join(_TESTCASES_DIR_PATH, testcase.dirname)
            with open(os.path.join(testcase_dirpath, "index.html"), "w+") as f:
                f.write(self.__gen_testcase_html_body(testcase, testcase_dirpath))
            for i, step in enumerate(testcase.steps):
                with open(
                    os.path.join(testcase_dirpath, f"{step.name}.html"), "w+"
                ) as f:
                    f.write(self.__gen_step_html_body(testcase, i, testcase_dirpath))
            # extra: latest
            if idx == len(self.__new_testcases) - 1:
                testcase_dirpath = os.path.join(_TESTCASES_DIR_PATH, "latest")
                with open(os.path.join(testcase_dirpath, "index.html"), "w+") as f:
                    f.write(self.__gen_testcase_html_body(testcase, testcase_dirpath))
                for i, step in enumerate(testcase.steps):
                    with open(
                        os.path.join(testcase_dirpath, f"{step.name}.html"), "w+"
                    ) as f:
                        f.write(
                            self.__gen_step_html_body(testcase, i, testcase_dirpath)
                        )

    def __prepare_save(self):
        if not os.path.exists(_REPORT_DIR_PATH):
            os.makedirs(_REPORT_DIR_PATH)
        if not os.path.exists(_TESTCASES_DIR_PATH):
            os.makedirs(_TESTCASES_DIR_PATH)
        for new_testcase in self.__new_testcases:
            new_testcase_dirpath = os.path.join(
                _TESTCASES_DIR_PATH, new_testcase.dirname
            )
            if not os.path.exists(new_testcase_dirpath):
                os.makedirs(new_testcase_dirpath)
        latest_testcase_dirpath = os.path.join(_TESTCASES_DIR_PATH, "latest")
        if not os.path.exists(latest_testcase_dirpath):
            os.makedirs(latest_testcase_dirpath)

    def __gen_step_html_body(self, testcase, index, dirpath):
        step = testcase.steps[index]
        soup = bs(self.__step_html, "html.parser")
        # set head
        head = gen_html_head(f"Testcase: {testcase.name}, step {index+1}", dirpath)
        soup.find("head").append(head)
        # set title
        soup.find(attrs={"id": "testcase_title"}).string = (
            f"{testcase.name}: #{index+1}"
        )
        soup.find(attrs={"id": "step_title"}).string = step.name
        # set check list
        checklist = soup.find(attrs={"id": "checklist"})
        for ret, msg in step.results:
            svg = get_svg(ret, dirpath)
            p = soup.new_tag("p")
            p.append(svg)
            p.append(f" {msg}")
            checklist.append(p)
        # set response
        soup.find(attrs={"id": "status_code"}).string = str(
            step.response["status_code"]
        )
        soup.find(attrs={"id": "response_time"}).string = (
            f"{step.response['response_time']*1000:.0f} ms"
        )
        soup.find(attrs={"id": "response_body"}).string = json.dumps(
            step.response["body"], indent=4
        )

        def set_headers_table(element, data):
            for key, value in data.items():
                tr = soup.new_tag("tr")
                td = soup.new_tag("td")
                td.string = key
                tr.append(td)
                td = soup.new_tag("td")
                td.string = value
                tr.append(td)
                element.append(tr)

        set_headers_table(
            soup.find(attrs={"id": "response_headers"}), step.response["headers"]
        )
        # set request
        soup.find(attrs={"id": "request_method_url"}).string = (
            f"{step.method.upper()} {step.request['url']}"
        )
        soup.find(attrs={"id": "request_body"}).string = json.dumps(
            step.request["body"], indent=4
        )
        set_headers_table(
            soup.find(attrs={"id": "request_headers"}), step.request["headers"]
        )
        # set prev/next buttons
        prev_button = soup.find(attrs={"id": "prev_button"})
        next_button = soup.find(attrs={"id": "next_button"})
        if index == 0:
            prev_button["disabled"] = True
        else:
            prev_button["onclick"] = (
                f"window.location.href='{testcase.steps[index-1].name}.html'"
            )
        if index == len(testcase.steps) - 1:
            next_button["disabled"] = True
        else:
            next_button["onclick"] = (
                f"window.location.href='{testcase.steps[index+1].name}.html'"
            )
        return soup.prettify()

    def __gen_testcase_html_body(self, testcase, dirpath):
        soup = bs(self.__testcase_html, "html.parser")
        # set head
        head = gen_html_head(f"Testcase: {testcase.name}", dirpath)
        soup.find("head").append(head)
        # set title
        soup.find(attrs={"id": "testcase_title"}).string = testcase.name
        # set description
        if testcase.description:
            soup.find(attrs={"id": "description"}).string = testcase.description
        else:
            soup.find(attrs={"id": "description"}).decompose()
        # set steps
        table = soup.find(attrs={"id": "steps_table"})
        for step in testcase.steps:
            row = soup.new_tag("tr")
            # col 1: status
            td = soup.new_tag("td")
            svg = get_svg(step.success, dirpath)
            td.append(svg)
            row.append(td)
            # col 2: step name
            td = soup.new_tag("td")
            a = soup.new_tag("a")
            a["href"] = f"{step.name}.html"
            a.string = step.name
            td.append(a)
            row.append(td)
            # col 3: method
            td = soup.new_tag("td")
            td.string = step.method.upper()
            row.append(td)
            # col 4: url
            td = soup.new_tag("td")
            td.string = step.request["url"]
            row.append(td)
            # col 5: status code
            td = soup.new_tag("td")
            td.string = str(step.response["status_code"])
            row.append(td)
            # col 5: response time
            td = soup.new_tag("td")
            td.string = f"{step.response['response_time']*1000:.0f} ms"
            row.append(td)

            table.append(row)
        # set back button
        back_button = soup.find(attrs={"id": "back_button"})
        back_href = os.path.relpath(
            os.path.join(_REPORT_DIR_PATH, "index.html"), dirpath
        )
        back_button["onclick"] = f"window.location.href='{back_href}'"
        return soup.prettify()

    def __gen_index_html_body(self, dirpath):
        soup = bs(self.__report_html, "html.parser")
        head = gen_html_head("API Send Report", dirpath)
        soup.find("head").append(head)
        table = soup.find(attrs={"id": "testcases_table"})
        for idx, recent in enumerate(self.__recent.data):
            row = soup.new_tag("tr")
            # col 1: status
            td = soup.new_tag("td")
            success = recent["success_steps"] == recent["total_steps"]
            svg = get_svg(success, dirpath)
            td.append(svg)
            row.append(td)
            # col 2: name
            td = soup.new_tag("td")
            name_link = soup.new_tag("a")
            if idx == 0:
                name_link["href"] = os.path.relpath(
                    os.path.join(_TESTCASES_DIR_PATH, "latest", "index.html"),
                    dirpath,
                )
            else:
                name_link["href"] = os.path.relpath(
                    os.path.join(_TESTCASES_DIR_PATH, recent["dirname"], "index.html"),
                    dirpath,
                )
            name_link.string = recent["name"]
            td.append(name_link)
            row.append(td)
            # col 3: pass rate
            td = soup.new_tag("td")
            pass_rate = recent["success_steps"] / recent["total_steps"] * 100
            td.string = f"{pass_rate:.2f}%"
            row.append(td)
            # col 4: date
            td = soup.new_tag("td")
            td.string = recent["date"]
            row.append(td)

            table.append(row)
        return soup.prettify()
