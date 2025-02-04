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
    
    function calculateBrightness(magnitude) {
        // Base dimming factor
        const dimmingFactor = 2.5;
        
        // Calculate relative brightness
        // For magnitude 1, we want 1
        // For magnitude 2, we want 1/2.5
        // For magnitude 3, we want 1/6.25, etc.
        const relativeBrightness = 1 / Math.pow(dimmingFactor, magnitude - 1);
        
        return relativeBrightness;
    }
    
    return results.data.map(row => ({
        hi: row.Index,
        x: row.x,
        y: row.y,
        z: row.z,
        ra: row.RA,
        dec: row.DEC,
        distance: row.Distance,
        brightness: calculateBrightness(row.Vmag)
    }));
}