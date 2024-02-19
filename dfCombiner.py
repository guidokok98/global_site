import os
import pandas as pd
from pathlib import Path

avarageCols = ["winrate", "average", "avarage", "diff", "cc"]
skipCols = ["date", "last_played"]
#checks if given column exist, if not make the column
def FcheckColumn(df, columnName):
    try:
        df[columnName]
    except:
        df = FnewColumn(df, columnName)
    return df

def FnewColumn(df,columnName):
    column = []
    for i in range(0, df.shape[0],1):
        column.append(0)
    df[columnName] = column
    return df

def FaddVal(df, rowColumnName, rowValue, columnName, val):
    df = FcheckColumn(df, columnName)
    oldVal = FreadDf(df, rowColumnName, rowValue, columnName)
    if isinstance(oldVal, str) == False and "id" not in columnName and "ID" not in columnName and "name" not in columnName:
        newVal = oldVal + val
        df=FeditDf(df, rowColumnName, rowValue, columnName, newVal)
    return df

#change given value in the new value
def FeditDf( df, rowColumnName, rowValue, columnName, value):
    rowNumber = FfindRow(df, rowColumnName, rowValue)
    try:
        df.at[rowNumber, columnName] = value #changes the value to the new value
    except:
        if isinstance(value, str):
            df[columnName] = df[columnName].astype(str)
            df.at[rowNumber, columnName] = value #changes the value to the new value
    return df

def FreadDf(df, rowColumnName, rowValue, columnName):
    rowNumber = FfindRow(df, rowColumnName, rowValue)
    if rowNumber == 'None':
        value = 'None'
    else:
        value = df[columnName][rowNumber]
    return value
def FfindRow(df, rowColumnName, rowValue):
    rowNumber = 'None'
    try:
        rowNumber = (df[df[rowColumnName] == rowValue].index.values[0])
    except:
        if isinstance(rowNumber, str):
            rowNumber = 'None'
    return rowNumber

def readCSV(dfName):
    file = dfName
    # print("csv location: ", file)
    tempDf = pd.read_csv(file)
    # print(tempDf)
    return tempDf

def FaverageVal(df, rowColumnName, rowValue, columnValAmountName, columnValName, valAmount, val):
    df = FcheckColumn(df, columnValAmountName)
    df = FcheckColumn(df, columnValName
                      )
    oldValAmount = FreadDf(df, rowColumnName, rowValue, columnValAmountName)
    oldVal = FreadDf(df, rowColumnName, rowValue, columnValName)
    
    newVal = round((oldVal * oldValAmount + valAmount * val)/ (oldValAmount+valAmount),2)
    df=FeditDf(df, rowColumnName, rowValue, columnValName, newVal)
    return df

def dfCombiner(csvDB, mapName, stats):
    global avarageCols
    hits = []
    for singleCsv in csvDB:
        if mapName in singleCsv and stats in singleCsv:
            hits.append(singleCsv)
    # print(hits)
    totalDf = readCSV(hits[0])
    # print("set base: ", hits[0])
    for hit in hits[1:]:
        # print("doing hit: ", hit)
        readDf = readCSV(hit)
        # print("next df: \n", readDf)
        for index, row in readDf.iterrows():
            rowName = readDf.columns[0]
            rowValue = row[readDf.columns[0]]
            rowNbr = FfindRow(totalDf, rowName, rowValue)
            if rowNbr == 'None':
                # print("row missing ")
                totalDf = totalDf.append(row)
            else:
                for column in readDf.columns[1:]:
                    if column in skipCols:
                        None
                    else:
                        if any(ele in column for ele in avarageCols) == True:
                            # print("average this:",column)
                            if "champStats" in stats:
                                totalDf= FaverageVal(totalDf, rowName, rowValue, "tot_played", column, row["tot_played"], row[column])
                            else:
                                totalDf= FaverageVal(totalDf, rowName, rowValue, "played", column, row["played"], row[column])
                        else:
                            # print("add this: ", column)
                            totalDf= FaddVal(totalDf, rowName, rowValue, column, row[column])
    # print("done")
    return totalDf

# def folderScan(givenPath, csvDB):
#     """
#     scans through the given path and do tasks
#     """
#     try:
#         for file in os.listdir(givenPath):
#             # print(file, end="\r")
#             # Inisiating the path of the file
#             file_path = f"{givenPath}/{file}"
#             # Check if file is a folder, if so go in that folder
#             if os.path.isdir(file_path):
#                 newPath = givenPath + "/" + file
#                 csvDB = folderScan(newPath, csvDB)

#             # check if file is a file, if so copy that file
#             elif (file.endswith(".csv")):
#                 # print(file_path)
#                 csvDB.append(file_path)
#     #if there is an error, save it in txt file
#     except Exception as error:
#         print("path problem: ", str(error))
#     return csvDB
# path = r"D:\1.temp\ironsuperhulk"
# csvDB = folderScan(path, [])
# # print(csvDB)
# df = dfCombiner(csvDB, "ARAM", "champStats")
# print(df)