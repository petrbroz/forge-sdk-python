Autodesk.Viewing.Initializer({ accessToken: document.getElementById('token').value }, async function () {
    const config = {};
    const viewer = new Autodesk.Viewing.GuiViewer3D(document.getElementById('preview'), config);
    viewer.start();
    viewer.setTheme('light-theme');
    setupModelSelection(viewer);
});

async function setupModelSelection(viewer) {
    const models = document.getElementById('models');
    models.onchange = () => loadModel(viewer, models.value);
    if (!viewer.model && models.value) {
        loadModel(viewer, models.value);
    }
}

function loadModel(viewer, urn) {
    function onDocumentLoadSuccess(doc) {
        viewer.loadDocumentNode(doc, doc.getRoot().getDefaultGeometry());
    }
    function onDocumentLoadFailure(code, message) {
        alert('Could not load model. See the console for more details.');
        console.error(message);
    }
    Autodesk.Viewing.Document.load('urn:' + urn, onDocumentLoadSuccess, onDocumentLoadFailure);
}
