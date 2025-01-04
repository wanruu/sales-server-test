import os
import json
import shutil

report_root = 'report'
latest_filepath = os.path.join(report_root, 'latest.json')
svgs_dirpath = os.path.join(report_root, 'svgs')
src_dirpath = os.path.join(report_root, 'src')

latest = []
max_latest_length = 30

def save_latest(data):
    global latest
    latest.insert(0, data)
    if len(latest) > max_latest_length:
        latest = latest[:max_latest_length]

    def gen_latest_row(item):
        svg_name = 'success' if item["total_steps"] == item["success_steps"] else 'failed'
        return f'''
            <tr>
                <td><img src="./svgs/{svg_name}.svg" width="20" height="20" /></td>
                <td><a href="src/{item["dirname"]}/index.html">{item["name"]}</a></td>
                <td>{item["success_steps"] / item["total_steps"] * 100:.1f}%</td>
            </tr>
        '''
    latest_html = f'''<!DOCTYPE html>
        <html>
        <head>
            <title>Test Report</title>
            <link rel="stylesheet" href="base.css" />
        </head>
        <body>
            <h1>Test Report</h1>
            <table>
                <tr>
                    <th></th>
                    <th>Testcase</th>
                    <th>Pass Rate</th>
                </tr>
                {''.join([gen_latest_row(item) for item in latest])}
            </table>
        </body>
        </html>'''
    with open(os.path.join(report_root, 'index.html'), 'w+') as f:
        f.write(latest_html)
    with open(latest_filepath, 'w+') as f:
        json.dump(latest, f)

def prepare():
    if not os.path.exists(report_root):
        os.mkdir(report_root)
    if not os.path.exists(svgs_dirpath):
        os.mkdir(svgs_dirpath)
    if not os.path.exists(src_dirpath):
        os.mkdir(src_dirpath)

    global latest
    if os.path.exists(latest_filepath):
        with open(latest_filepath, 'r') as f:
            latest = json.load(f)
    latest_dirnames = [item['dirname'] for item in latest]
    actual_dirnames = [os.path.basename(dirname) for dirname in os.listdir(src_dirpath) if os.path.isdir(os.path.join(src_dirpath, dirname))]
    for dirname in actual_dirnames:
        if (dirname not in latest_dirnames and dirname != 'svgs'):
            shutil.rmtree(os.path.join(src_dirpath, dirname))

    with open(os.path.join(report_root, 'svgs', 'failed.svg'), 'w+') as f:
        f.write('''<?xml version="1.0" encoding="iso-8859-1"?>
            <!-- Uploaded to: SVG Repo, www.svgrepo.com, Generator: SVG Repo Mixer Tools -->
            <!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
            <svg fill="red" version="1.1" id="Capa_1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" 
                width="800px" height="800px" viewBox="0 0 399.362 399.362"
                xml:space="preserve">
            <g>
                <path d="M393.917,135.248C369.437,30.596,258.665-7.96,163.193,9.788C72.618,26.923-6.331,99.14,0.401,195.835
                    c6.12,82.008,92.412,203.796,184.824,197.676c7.956,0,16.523-1.224,22.644-1.836c4.896-0.611,12.24-0.611,20.196-1.224
                    c43.451-1.224,89.352-30.601,116.892-59.364C392.081,281.515,409.217,200.732,393.917,135.248z M201.749,369.032
                    c-0.611,0-1.224,0.611-1.835,0.611c-1.224-0.611-2.448-0.611-3.672-1.224c-3.672-1.836-6.732,0-8.568,2.448
                    c-0.612-0.612-0.612-0.612-1.224-0.612c0.612-0.612,1.836-1.224,2.448-2.448c4.896,0,9.792,0,14.688,0c0.612,0,0.612,0,1.224,0
                    C204.197,368.419,202.973,368.419,201.749,369.032z M307.625,216.032c0,4.284-0.612,11.628-0.612,18.359
                    c-29.376-2.447-60.588,0-88.739,0.612c-41.004,0.612-82.62,0-123.624,4.896c-1.224,0-1.836-0.612-3.06-0.612
                    c0.612-1.224,0-1.836,0-2.448c0,0,0,0,0-0.612c0.612-3.06,0-6.731,0-9.18c0-9.18,0.612-18.36,1.224-26.928
                    c0.612-10.404,3.672-23.256,4.284-34.884c9.792,2.448,22.644,0.612,30.6,1.224c26.928,0,54.468-0.612,81.395-1.224
                    c27.54-0.612,55.08-1.224,82.62-1.836c5.508,0,13.464,0.612,20.809,0.612C311.297,180.536,308.237,198.284,307.625,216.032z"/>
            </g>
            </svg>
        ''')

    with open(os.path.join(report_root, 'svgs', 'success.svg'), 'w+') as f:
        f.write('''<?xml version="1.0" encoding="iso-8859-1"?>
            <!-- Uploaded to: SVG Repo, www.svgrepo.com, Generator: SVG Repo Mixer Tools -->
            <!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
            <svg fill="green" version="1.1" id="Capa_1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" 
                width="800px" height="800px" viewBox="0 0 352.62 352.62"
                xml:space="preserve">
            <g>
                <path d="M337.222,22.952c-15.912-8.568-33.66,7.956-44.064,17.748c-23.867,23.256-44.063,50.184-66.708,74.664
                    c-25.092,26.928-48.348,53.856-74.052,80.173c-14.688,14.688-30.6,30.6-40.392,48.96c-22.032-21.421-41.004-44.677-65.484-63.648
                    c-17.748-13.464-47.124-23.256-46.512,9.18c1.224,42.229,38.556,87.517,66.096,116.28c11.628,12.24,26.928,25.092,44.676,25.704
                    c21.42,1.224,43.452-24.48,56.304-38.556c22.645-24.48,41.005-52.021,61.812-77.112c26.928-33.048,54.468-65.485,80.784-99.145
                    C326.206,96.392,378.226,44.983,337.222,22.952z M26.937,187.581c-0.612,0-1.224,0-2.448,0.611
                    c-2.448-0.611-4.284-1.224-6.732-2.448l0,0C19.593,184.52,22.653,185.132,26.937,187.581z"/>
            </g>
            </svg>
        ''')

    with open(os.path.join(report_root, 'base.css'), 'w+') as f:
        f.write('''
            table {
                border-collapse: collapse;
                width: 100%;
                font-size: 13pt;
                line-height: 30px;
            }

            tr:nth-child(odd) {
                background-color: #e9f3e9
            }

            th,
            td {
                text-align: left;
                padding: 8px;
                word-break: break-all;
            }

            th:first-child, td:first-child {
                border-radius: 5px 0 0 5px;
            }

            th:last-child, td:last-child {
                border-radius: 0 5px 5px 0;
            }

            th {
                background-color: #77c57b;
                color: white;
            }

            .tab {
                overflow: hidden;
                border: 1px solid #ccc;
                background-color: #f1f1f1;
                border-radius: 5px 5px 0 0;
            }

            .tab button {
                background-color: inherit;
                float: left;
                border: none;
                outline: none;
                cursor: pointer;
                padding: 14px 16px;
                transition: 0.3s;
                
                color: #bbb;
            }

            .tab button:hover,
            .tab button:active {
                background-color: inherit;
                border-radius: 0;
                color: #239e23;
            }

            .tab button.active {
                color: #239e23;
                font-weight: bold;
            }

            .tab-content {
                display: none;
                padding: 16px 20px;
                border: 1px solid #ccc;
                border-top: none;
                border-radius: 0 0 5px 5px;
            }

            button {
                padding: 10px 16px;
                font-size: 16px;
                border: none;
                cursor: pointer;
                border-radius: 5px;
            }

            button:hover,
            button:active {
                background-color: #77c57b;
                color: white
            }
                
            img {
                vertical-align: middle;
                margin: 5px;
            }
        ''')

    with open(os.path.join(report_root, 'script.js'), 'w+') as f:
        f.write('''
            function openTab(evt, tabName) {
                // Declare all variables
                var i, tabContent, tabLinks;

                // Get all elements with class="tab-content" and hide them
                tabContent = document.getElementsByClassName("tab-content");
                for (i = 0; i < tabContent.length; i++) {
                    tabContent[i].style.display = "none";
                }

                // Get all elements with class="tab-links" and remove the class "active"
                tabLinks = document.getElementsByClassName("tab-links");
                for (i = 0; i < tabLinks.length; i++) {
                    tabLinks[i].className = tabLinks[i].className.replace(" active", "");
                }

                // Show the current tab, and add an "active" class to the button that opened the tab
                document.getElementById(tabName).style.display = "block";
                evt.currentTarget.className += " active";
            }
        ''')