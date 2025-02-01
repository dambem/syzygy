import Papa from 'papaparse';

export async function loadStarData() {
    const response = await fetch('/data/StartPositionXYZ.csv');
    const text = await response.text();
    
    // Use Papa Parse for more robust CSV handling
    const results = Papa.parse(text, {
        header: true,
        dynamicTyping: true,
        skipEmptyLines: true
    });
    
    return results.data.map(row => ({
        x: row.x,
        y: row.y,
        z: row.z,
        ra: row.RA,
        dec: row.DEC,
        distance: row.Distance
    }));
}