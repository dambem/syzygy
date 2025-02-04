import pandas as pd
import numpy as np
from astropy.coordinates import SkyCoord

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


def convert_to_xyz(ra_str, dec_str, magnitude):
    # Create SkyCoord object to handle the conversion
    coords = SkyCoord(ra_str, dec_str, unit=(u.hourangle, u.deg))
    
    # Get RA and DEC in radians
    ra_rad = coords.ra.rad
    dec_rad = coords.dec.rad
    
    # Calculate distance from magnitude (using a simple approximation)
    # Distance = 10^((magnitude + 5)/5) parsecs
    distance = 10**((magnitude + 5)/5)
    
    # Convert to Cartesian coordinates
    x = distance * np.cos(dec_rad) * np.cos(ra_rad)
    y = distance * np.cos(dec_rad) * np.sin(ra_rad)
    z = distance * np.sin(dec_rad)
    
    return x, y, z
df = pd.read_json("BSC.json")
df = df.rename(columns={'harvard_ref_#': 'Index'})
print(df)
print(df)
print(df.columns)
# print(df) #todo test

# Calculate RA in degrees


# df.to_csv("StarPosition.csv")



