def hello(name: str) -> str:
    return f"Hello, {name}!"
    
    
def check_variable_eligibility(df, var, groupby, min_n=2):
    """Returns True if the variable has enough non-missing values in both groups."""
    if var not in df.columns:
        return False
    groups = df[groupby].dropna().unique()
    for g in groups:
        group_data = df[df[groupby] == g][var].dropna()
        if len(group_data) < min_n or group_data.nunique() <= 1:
            return False
    return True
    
    
    
def table1(df, columns, categorical, nonnormal, group):
    from tableone import TableOne
    from scipy.stats import mannwhitneyu
    import pandas as pd

    if (len(df[group].unique()) == 2) and bool(nonnormal):
        new_p_values = {}
        for variable in nonnormal:
            df[variable] = pd.to_numeric(df[variable], errors='coerce')

        # Perform Mann-Whitney U test for each non-normal variable
        for variable in nonnormal:
            group0 = df[df[group] == df[group].unique()[0]][variable].dropna()
            group1 = df[df[group] == df[group].unique()[1]][variable].dropna()
            statistic, p_value = mannwhitneyu(group0, group1, alternative='two-sided', method='exact', use_continuity=True)
            new_p_values[variable] = round(p_value, 3)

    

        # Create TableOne
        table = TableOne(df, groupby=group, columns=columns,
                         categorical=categorical, nonnormal=nonnormal,
                         normal_test=True, htest_name=True,
                         label_suffix=True, pval=True,
                         display_all=True, include_null=False)

        table1_df = table.tableone
        table1_df.columns = table1_df.columns.get_level_values(1)
        table1_df = table1_df.reset_index()

        # Update p-values using the manually calculated ones
        table1_df["P-Value"] = table1_df["level_0"].apply(
            lambda var: new_p_values.get(var.split(",")[0], table1_df["P-Value"].loc[table1_df["level_0"] == var].iloc[0])
        )

        table1_df.set_index(["level_0", "level_1"], inplace=True)

        # Only keep P-Value in first row of each variable
        first_idx = table1_df.groupby('level_0').head(1).index
        table1_df['P-Value'] = table1_df.apply(lambda row: row['P-Value'] if row.name in first_idx else '', axis=1)

        # Rename test labels
        table1_df['Test'] = table1_df['Test'].replace({'Kruskal-Wallis': 'Mann-Whitney'})

        return table1_df

    else:
        table = TableOne(df, groupby=group, columns=columns,
                         categorical=categorical, nonnormal=nonnormal,
                         normal_test=True, htest_name=True,
                         label_suffix=True, pval=True,
                         display_all=True, include_null=False)
        return table