/* the code in this file initialize a few DOM elements for the react
elements to mount
*/

// insert the divs for the header and editor
const editorElt = document.createElement("div");
editorElt.id = "editor-react-root";
document.body.prepend(editorElt);

const headerElt = document.createElement("div");
headerElt.id = "notebook-header";
document.body.prepend(headerElt);
