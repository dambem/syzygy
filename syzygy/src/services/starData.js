import Papa from 'papaparse';

export async function loadStarData() {
    const response = await fetch('/data/StartPositionXYZ3.csv');
    const text = await response.text();
    
    // Use Papa Parse for more robust CSV handling
    const results = Papa.parse(text, {
        header: true,
        dynamicTyping: true,
        skipEmptyLines: true
    });
    
    const class_to_color ={
        'O':'#0000FF',
        'B':'#A0CAF0',
        'A':'#FFFFFF',
        'F':'#FFF7C8',
        'G':'#FFE87C',
        'K':'#FFA500',
        'M':'#FF6B61',
    
      }
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

    function slice_class(test) {
        if (!test) return 'A'; // Handle null/undefined
        return test[0]; // Get first character
    }
    
    function colorStar(test) {
        if (!test) return '#FFFFFF'; // Handle null/undefined
        return class_to_color[test[0]]; // Get first character

    }
    return results.data.map(row => ({
        hi: row.Index,
        x: row.x,
        y: row.y,
        z: row.z,
        ra: row.RA,
        dec: row.DEC,
        distance: row.Distance*10,
        class: slice_class(row.SpectralCls),
        color: colorStar(row.SpectralCls),
        brightness: calculateBrightness(row.MAG)
    }));
}