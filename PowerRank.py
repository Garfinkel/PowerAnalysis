###Output Example: https://imgur.com/a/42iK5SE

import pandas as pd

#pull in Data
Base = pd.read_csv('ProRefSchedule.csv', encoding = "utf-8")
TeamList = pd.read_csv('ListNFLTeams.csv', encoding = "utf-8")


#Calculate Initial Yds/Team
TeamList['YdsF'] = -99
TeamList['YdsA'] = -99
TeamList['Ratio_Offense'] = 0.00
TeamList['Ratio_Defense'] = 0.00
GamesPlayed = 16

#VariablesUsedBelow
UpperCap = 1.33 #Max Ratio Allowed to reduce single game skew
LowerCap = .66  #Min Ratio Allowed to reduce single game skew

#Add Yards for each team to master TeamList
for x in TeamList[Teams]:
    #Calc total Yds F/A
    YardsForInW = Base.loc[Base['Winner/tie'] == x]['YdsW'].sum()
    YardsAgainstInW = Base.loc[Base['Winner/tie'] == x]['YdsL'].sum()
    YardsForInL = Base.loc[Base['Loser/tie'] == x]['YdsL'].sum()
    YardsAgainstInL = Base.loc[Base['Loser/tie'] == x]['YdsW'].sum()
    
    #Append Wins/Loses
    TotalYardsF = YardsForInW + YardsForInL
    TotalYardsA = YardsAgainstInW + YardsAgainstInL   
    
    TeamList['YdsF'][TeamList[Teams] == x] = (TotalYardsF / GamesPlayed)
    TeamList['YdsA'][TeamList[Teams] == x] = (TotalYardsA / GamesPlayed)

TeamList_Initial = TeamList.copy() 
TeamList_Initial = TeamList_Initial[['Teams','YdsF','YdsA']]
TeamList_Initial = TeamList_Initial.rename(index=str, columns={"YdsF": "YdsF_Initial", "YdsA": "YdsA_Initial"})

#Calculate yards for/against based on expected yards based on oponnent, then recalc based on updated values (100 times)
for z in range(5):

    print('Loop #: %s' % (z+1))

    #Calculate Power Ratio for each Offense
    for x in TeamList[Teams]:
        OppList_InWin = Base[Base['Winner/tie'] == x]
        OppList_InWin_Append = pd.merge(OppList_InWin, TeamList, left_on = 'Loser/tie', right_on = 'Teams')
        OppList_InWin_Ratio = OppList_InWin_Append['YdsW']  / OppList_InWin_Append['YdsA'] #Yards gained in each win vs. the Avg Yards each teams typically allows
    
        OppList_InLoss = Base[Base['Loser/tie'] == x]
        OppList_InLoss_Append = pd.merge(OppList_InLoss, TeamList, left_on = 'Winner/tie', right_on = 'Teams')
        OppList_InLoss_Ratio = OppList_InLoss_Append['YdsL']  / OppList_InLoss_Append['YdsA'] #Yards gained in each loss vs. the Avg Yards each teams typically allows
        Offensive_Ratio_List = OppList_InLoss_Ratio.append(OppList_InWin_Ratio)
        
        #Set caps 
        Offensive_Ratio_List[Offensive_Ratio_List>UpperCap] = UpperCap
        Offensive_Ratio_List[Offensive_Ratio_List<LowerCap] = LowerCap
        Offensive_Ratio_Avg = Offensive_Ratio_List.mean()

        #Update Team's Ratio
        TeamList['Ratio_Offense'][TeamList[Teams] == x] = Offensive_Ratio_Avg

    #Apply Ratio to Offense & reset ratio
    TeamList['YdsF'] = TeamList['YdsF'] * TeamList['Ratio_Offense']

    #Calculate Power Ratio for each Defense
    for x in TeamList[Teams]:
        OppList_InWin = Base[Base['Winner/tie'] == x]
        OppList_InWin_Appendb = pd.merge(OppList_InWin, TeamList, left_on = 'Loser/tie', right_on = 'Teams')
        OppList_InWin_Ratiob = OppList_InWin_Appendb['YdsL']  / OppList_InWin_Appendb['YdsF'] #Yards allowed in each win vs. the Avg Yards typically gained by opp.
    
        OppList_InLoss = Base[Base['Loser/tie'] == x]
        OppList_InLoss_Append = pd.merge(OppList_InLoss, TeamList, left_on = 'Winner/tie', right_on = 'Teams')
        OppList_InLoss_Ratiob = OppList_InLoss_Append['YdsW']  / OppList_InLoss_Append['YdsA'] #Yards allowed in each loss vs. the Avg Yards typically gained by opp.
        Deffensive_Ratio_List = OppList_InLoss_Ratiob.append(OppList_InWin_Ratiob)
        
        #Set caps 
        Deffensive_Ratio_List[Deffensive_Ratio_List>UpperCap] = UpperCap
        Deffensive_Ratio_List[Deffensive_Ratio_List<LowerCap] = LowerCap
        Deffensive_Ratio_Avg = Deffensive_Ratio_List.mean()

        #Update Team's Ratio
        TeamList['Ratio_Defense'][TeamList[Teams] == x] = Deffensive_Ratio_Avg

    #Apply Ratio to Defense & reset ratio
    TeamList['YdsA'] = TeamList['YdsA'] * TeamList['Ratio_Defense']

    print(TeamList)

#Pull in initial yardage data for comparison
Outcome = pd.merge(TeamList, TeamList_Initial, left_on = 'Teams', right_on = 'Teams')

#Calc diff from initial
Outcome['Off_Adj_From_Initial'] = (Outcome['YdsF'] - Outcome['YdsF_Initial']).round(2)
Outcome['Deff_Adj_From_Initial'] = (Outcome['YdsA'] - Outcome['YdsA_Initial']).round(2)

#Drop irrelevent columns
Outcome = Outcome.drop(['Ratio_Defense','Ratio_Offense'], axis = 1)
