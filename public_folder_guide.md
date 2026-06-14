# React Public Folder Guide (Quick Overview)

The `public/` directory contains static assets that the bundler does not process or bundle. These files are copied directly to the output build folder as-is.

### Key Points:
* **Not Customized:** The files in this folder are currently the default, unmodified boilerplates from `create-react-app`.
* **%PUBLIC_URL%:** In `index.html`, this is replaced with the root URL path during the build to prevent broken links.

### File Directory:
* **[index.html](file:///c:/Users/Chirag%20Pradhan/qna/client/public/index.html):** The main HTML entry point/template where React mounts your component tree.
* **`favicon.ico`:** The small logo displayed in the browser tab.
* **`logo192.png` & `logo512.png`:** Standard launcher icons for Progressive Web Apps (PWAs).
* **`manifest.json`:** Metadata configuration for installing the web app on devices.
* **`robots.txt`:** Rules telling search engine crawlers which pages to index or ignore.
