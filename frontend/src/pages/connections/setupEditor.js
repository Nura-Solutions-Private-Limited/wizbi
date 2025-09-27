// import { EditorState, basicSetup } from "@codemirror/basic-setup";
// import { defaultTabBinding } from "@codemirror/commands";
// import { EditorView, keymap } from "@codemirror/view";
// import { json } from "@codemirror/lang-json";

// export default function setupEditors() {
//   const jsonRequestBody = document.querySelector("[data-json-request-body]");
//   const jsonResponseBody = document.querySelector("[data-json-response-body]");

//   const basicExtensions = [
//     basicSetup,
//     keymap.of([defaultTabBinding]),
//     json(),
//     EditorState.tabSize.of(2),
//   ];

//   const requestEditor = new EditorView({
//     state: EditorState.create({
//       doc: "{\n\t\n}", // Initial content for the request editor
//       extensions: basicExtensions,
//     }),
//     parent: jsonRequestBody,
//   });

//   const responseEditor = new EditorView({
//     state: EditorState.create({
//       doc: "", // Start completely empty
//       extensions: [...basicExtensions, EditorView.editable.of(false)],
//     }),
//     parent: jsonResponseBody,
//   });

//   function updateResponseEditor(value) {
//     // Make sure to clear the previous content fully and replace with new data
//     const jsonString = JSON.stringify(value, null, 2).trim(); // Trim any extra whitespace
//     console.log("Updating response editor with trimmed value:", jsonString);

//     responseEditor.dispatch({
//       changes: {
//         from: 0, // Start from the beginning
//         to: responseEditor.state.doc.length, // Clear the entire content
//         insert: jsonString, // Insert new JSON data
//       },
//     });
//   }

//   return { requestEditor, updateResponseEditor };
// }
