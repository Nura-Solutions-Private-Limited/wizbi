import React, { useState } from "react";
import s from "./AIForDataScience.module.scss";
import { CopyOutlined } from "@ant-design/icons";
import { Tooltip } from "antd";

export const CodeExtract = (response = '') => {
    const [copied, setCopied] = useState(false);
    let parts = response.split(/(```python\n)|(```\n)|(```)/);
    let [headingText, codeHeading, codeText, codeFooter, footerText] =
        parts.filter((part) => part !== undefined && part !== "");

    const code = `${codeHeading || ""}${codeText || ""}${codeFooter || ""
        }`.replaceAll("```", "");
    const handleCopyText = () => {
        navigator.clipboard.writeText(code).then(() => {
            setCopied(true);
            setTimeout(() => {
                setCopied(false);
            }, 2000);
        });
    };

    return (
        <div>
            <p>{headingText?.replaceAll("```", "") || ""}</p>
            <div className={s.custom_modal_content}>
                <div className={s.container}>
                    <pre> {code}</pre>
                    <Tooltip title={copied ? "Copied" : "Copy"} placement="top">
                        <div className={s.copy_icon} onClick={handleCopyText}>
                            <CopyOutlined />
                        </div>
                    </Tooltip>
                </div>

            </div>

            <p>{footerText?.replaceAll("```", "") || ""}</p>
        </div>
    );
};