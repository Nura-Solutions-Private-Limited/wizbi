import React, { useState, useEffect } from "react";
import s from "./AIForDataScience.module.scss";
import { CopyOutlined } from "@ant-design/icons";
import { Tooltip } from "antd";

export const GenAIDashboardCodeExtract = (response) => {
    const [copied, setCopied] = useState(false);
    const collections = Object.keys(response ?? {}) || [];
    const handleCopyText = (code) => {
        navigator.clipboard.writeText(code).then(() => {
            setCopied(true);
            setTimeout(() => {
                setCopied(false);
            }, 2000);
        });
    };

    return (
        <>
            {
                collections.map((key, index) => {
                    const { description, sqlcommands, title } = response[key];
                    return <div>
                        <p>{(index + 1)}. {title}</p><div className={s.custom_modal_content}>
                            <div className={s.container}>
                                <pre> {sqlcommands}</pre>
                                <Tooltip title={copied ? "Copied" : "Copy"} placement="top">
                                    <div className={s.copy_icon} onClick={() => { handleCopyText(sqlcommands) }}>
                                        <CopyOutlined />
                                    </div>
                                </Tooltip>
                            </div>

                        </div>
                    </div>
                })
            }
        </>

    );
};