import json

test_data = [[1.23, 3.45],[4.36,5.36]]
REPORT_AUX_INFO = {
    "heatmap":{
        "leftColumnTeam" : {},
        "rightColumnTeam" : {},
        "ballFromLeftSide" : {}
    },
    "attackRoute" :{
        "leftColumnTeam" : {},
        "rightColumnTeam" : {}
    },
    "heatmapBySection":{
        "leftColumnTeam" : {},
        "rightColumnTeam" : {}
    }
}

REPORT_AUX_INFO["heatmap"]["leftColumnTeam"] = {'data': test_data}
print(obj)


"""

obj["heatmap"].append({
    leftColum
})

"""