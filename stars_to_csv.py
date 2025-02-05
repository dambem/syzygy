import pandas as pd
import numpy as np
from astropy.coordinates import SkyCoord
import astropy.units as u

type = 'json'

if type =='fwf':
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
        (102, 108), #Vmag
        (161, 166) # Parallax 
    ]
    columns = [
        'Index', 'Star_ID', "RAh", 
        "RAm", "RAs", "DE_sign", "DEd",
        "DEm", "DEs", "Vmag", 'Parallax'
    ]


    # big_dipper = ["Alp UMa", "Alp"]

    def calculate_radius(self, vmag: float, parallax: float, temp: float, 
                            luminosity_modifier: float) -> float:
            """
            Calculate stellar radius in solar radii.
            
            Args:
                vmag: Visual magnitude
                parallax: Parallax in arcseconds
                temp: Effective temperature in Kelvin
                luminosity_modifier: Modifier based on luminosity class
            """
            if parallax <= 0:
                return None
                
            # Calculate absolute magnitude
            distance = 1000.0 / parallax  # Distance in parsecs
            abs_mag = vmag - 5 * np.log10(distance) + 5
            
            # Calculate bolometric correction (approximate)
            bc = -4.75 * np.log10(temp / 5778)
            
            # Calculate bolometric magnitude
            mbol = abs_mag + bc
            
            # Calculate luminosity relative to Sun
            luminosity = 10 ** ((4.75 - mbol) / 2.5)
            
            # Apply luminosity class modifier
            luminosity *= luminosity_modifier
            
            # Calculate radius using L = 4πR²σT⁴
            radius = np.sqrt(luminosity * (5778/temp)**4)
            
            return radius

    df = pd.read_fwf("catalog", colspecs=colspecs, names=columns, skiprows=0)
    df['RA'] = 15 * (df['RAh'] + df['RAm']/60 + df['RAs']/3600)
    #Calculating DEC in degrees
    dec_sign = df['DE_sign'].map({'-': -1, '+':1}).fillna(1)
    df['DEC'] = dec_sign * (df['DEd'] + df['DEm']/60 + df['DEs']/3600)
    # df['DEC'] =
    df['Distance'] = 1000/df['Parallax']  # parsecs, where parallax available
    df.loc[df['Distance'].isna(), 'Distance'] = 100
    df = df[['Index', 'RA', 'DEC', 'Distance', 'Vmag']]
    for col in columns:
        if col not in ["DE_sign", "Star_ID"]:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    def star_to_cartesian(df):
        ra_rad = np.radians(df['RA'])
        dec_rad = np.radians(df['DEC'])

        df['x'] = df['Distance'] * np.cos(dec_rad) * np.cos(ra_rad)
        df['y'] = df['Distance'] * np.cos(dec_rad) * np.sin(ra_rad)
        df['z'] = df['Distance'] * np.sin(dec_rad)
        
        return df

    stars = star_to_cartesian(df)
    stars = stars.replace([np.inf, -np.inf], np.nan).dropna()
    stars.to_csv('StartPositionXYZ.csv')


def convert_df_to_xyz_sphere(df):
    coords = SkyCoord(df['RA'], df['DEC'], unit=(u.hourangle, u.deg))
    
    # Get RA and DEC in radians
    ra_rad = coords.ra.rad
    dec_rad = coords.dec.rad
    
    # Distance = 10^((magnitude + 5)/5) parsecs
    df['Distance'] = 10**((df['MAG'] + 5)/5)
    
    # Convert to Cartesian coordinates
    df['x'] = np.cos(dec_rad) * np.cos(ra_rad)
    df['y'] = np.cos(dec_rad) * np.sin(ra_rad)
    df['z'] = np.sin(dec_rad)
    
    return df

df = pd.read_json("BSC.json")
df2 = pd.read_json("bsc5.json")
columns_to_keep = ['HR', 'SpectralCls']
df2 = df2[columns_to_keep]
df = df.rename(columns={'harvard_ref_#': 'Index'})
df = df.merge(
    df2,
    left_on='Index',
    right_on='HR',
    how='left'
)

result = convert_df_to_xyz_sphere(df)
result.to_csv('StartPositionXYZ2.csv')
print(result)
# print(df) #todo test

# Calculate RA in degrees


# df.to_csv("StarPosition.csv")



