export const useActiveTab = (tabsInfo, setTabInfo, setIndex, index) => {
  const dataInfo = [...tabsInfo];
  const activeTabIndex = () => {
    const currentIndex = tabsInfo.findIndex((info) => {
      return info.index === index + 1;
    });
    if (currentIndex != -1) {
      dataInfo[currentIndex].active = true;
      dataInfo[currentIndex].completed = false;
      setIndex(index + 1);
    }
    const prevIndex = tabsInfo.findIndex((info) => {
      return info.index === index;
    });

    if (prevIndex != -1) {
      dataInfo[prevIndex].active = false;
      dataInfo[prevIndex].completed = true;
    }
    setTabInfo(dataInfo);
  };

  const prevTabIndex = () => {
    const prevIndex = tabsInfo.findIndex((info) => {
      return info.index === index - 1;
    });
    if (prevIndex != -1) {
      dataInfo[prevIndex].active = true;
      dataInfo[prevIndex].completed = false;
      setIndex(index - 1);
    }
    const currentIndex = tabsInfo.findIndex((info) => {
      return info.index === index;
    });

    if (currentIndex != -1) {
      dataInfo[currentIndex].active = false;
      dataInfo[currentIndex].completed = false;
    }
    setTabInfo(dataInfo);
  };
  return {
    prevTabIndex,
    activeTabIndex,
  };
};
