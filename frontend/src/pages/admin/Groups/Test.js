import React, { useState } from "react";

const YourComponent = () => {
  const [selectedKeys, setSelectedKeys] = useState([]);

  const handleChange = (newSelectedKeys) => {
    setSelectedKeys(newSelectedKeys);
  };
  const handleTreeNodeSelect = (selectedNodeKeys, info) => {
    // Get the parent node key
    const parentNodeKey = info.node.props.parent;

    // If a child node is selected, check if all siblings are also selected
    if (parentNodeKey && info.selected) {
      const dataRef = info.node.props.dataRef;
      // Add a null check for dataRef
      if (dataRef && dataRef.children) {
        const siblings = dataRef.children.map((child) => child.key);
        const allSiblingsSelected = siblings.every((sibling) =>
          selectedKeys.includes(sibling),
        );

        // If all siblings are selected, select the parent node
        if (allSiblingsSelected) {
          setSelectedKeys([...selectedKeys, parentNodeKey]);
        }
      }
    }
  };

  return (
    <div>
      <h1>test</h1>
      <TreeSelect
        className="w-100 md:w-20rem"
        treeData={[
          {
            title: "Parent 1",
            key: "0-0",
            children: [
              { title: "Child 1", key: "0-0-0" },
              { title: "Child 2", key: "0-0-1" },
            ],
          },
          {
            title: "Parent 2",
            key: "0-1",
            children: [
              { title: "Child 3", key: "0-1-0" },
              { title: "Child 4", key: "0-1-1" },
            ],
          },
        ]}
        treeCheckable
        showCheckedStrategy="SHOW_PARENT"
        value={selectedKeys}
        onChange={handleChange}
        onSelect={handleTreeNodeSelect}
      />
    </div>
  );
};

export default YourComponent;
