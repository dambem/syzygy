import pandas as pd
import numpy as np

colspecs = [
    (0, 4),      # Index
    (5, 14),     # Star ID
    (75, 77), #Hours RA,
    (77, 79), #Minutes RA
    (79, 83), #Seconds RA
    (83, 84), # Sign DEC EQuinox J2000 
    (84, 86), # Hours DEgrees DES
    (86, 88), # Minutes DEgrees DEC
    (88, 90), # Seconds DES'
    (161, 166) # Parallax 
]
columns = [
    'Index', 'Star_ID', "RAh", 
    "RAm", "RAs", "DE_sign", "DEd",
    "DEm", "DEs", 'Parallax'
]


df = pd.read_fwf("catalog", colspecs=colspecs, names=columns, skiprows=0)
print(df)

for col in columns:
    if col not in ["DE_sign", "Star_ID"]:
        df[col] = pd.to_numeric(df[col], errors='coerce')
# print(df) #todo test

# Calculate RA in degrees
df['RA'] = 15 * (df['RAh'] + df['RAm']/60 + df['RAs']/3600)

#Calculating DEC in degrees
dec_sign = df['DE_sign'].map({'-': -1, '+':1}).fillna(1)
df['DEC'] = dec_sign * (df['DEd'] + df['DEm']/60 + df['DEs']/3600)
# df['DEC'] =
df['Distance'] = 1000/df['Parallax']  # parsecs, where parallax available
df.loc[df['Distance'].isna(), 'Distance'] = 100

df = df[['RA', 'DEC', 'Distance']]

df.to_csv("StarPosition.csv")


def star_to_cartesian(df):
    ra_rad = np.radians(df['RA'])
    dec_rad = np.radians(df['DEC'])

    df['x'] = df['Distance'] * np.cos(dec_rad) * np.cos(ra_rad)
    df['y'] = df['Distance'] * np.cos(dec_rad) * np.sin(ra_rad)
    df['z'] = df['Distance'] * np.sin(dec_rad)
    
    return df

stars = star_to_cartesian(df)
print(stars)
stars = stars.replace([np.inf, -np.inf], np.nan).dropna()
stars.to_csv('StartPositionXYZ.csv')
