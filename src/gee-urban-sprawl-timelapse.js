// =====================================================================
// URBAN SPRAWL TIME-LAPSE  ·  Landsat 5/7/8/9  ·  1985–2025
// For X video #1 "Dulu ini sawah" (@jalmiburung). See [[X-video-scripts]].
// Paste into the GEE Code Editor: https://code.earthengine.google.com
// =====================================================================

// --- 1. AREA OF INTEREST — change the point to your city ----------------
// Presets (lon, lat):
//   Bandung Selatan / Bojongsoang : 107.6386, -6.9750   (sawah -> perumahan)
//   Bandung Timur / Gedebage      : 107.6960, -6.9460
//   Bekasi–Cikarang (industri)    : 107.1500, -6.2700
//   Karawang (sawah -> industri)  : 107.3000, -6.3200
//   Serpong / BSD (Jabodetabek)   : 106.6700, -6.3000
var center = ee.Geometry.Point([107.6386, -6.9750]);   // <-- EDIT HERE
var aoi    = center.buffer(6000).bounds();              // ~12 km square box
Map.centerObject(aoi, 12);

// --- 2. TIME RANGE ------------------------------------------------------
var startYear = 1985;
var endYear   = 2025;

// --- 3. CLOUD / SHADOW MASK  (Landsat Collection 2 L2, QA_PIXEL) --------
function maskL2(img) {
  var qa = img.select('QA_PIXEL');
  var mask = qa.bitwiseAnd(1 << 1).eq(0)        // dilated cloud
      .and(qa.bitwiseAnd(1 << 3).eq(0))         // cloud
      .and(qa.bitwiseAnd(1 << 4).eq(0))         // cloud shadow
      .and(qa.bitwiseAnd(1 << 2).eq(0));        // cirrus (L8/9)
  return img.updateMask(mask);
}

// --- 4. SCALE TO REFLECTANCE + RENAME TO COMMON BANDS -------------------
function prep(img, era) {
  img = maskL2(img);
  var bands = (era === 'old')
    // L4/5/7 : blue B1, green B2, red B3, nir B4, swir1 B5, swir2 B7
    ? img.select(['SR_B1','SR_B2','SR_B3','SR_B4','SR_B5','SR_B7'],
                 ['blue','green','red','nir','swir1','swir2'])
    // L8/9   : blue B2, green B3, red B4, nir B5, swir1 B6, swir2 B7
    : img.select(['SR_B2','SR_B3','SR_B4','SR_B5','SR_B6','SR_B7'],
                 ['blue','green','red','nir','swir1','swir2']);
  return bands.multiply(0.0000275).add(-0.2)   // C2 L2 scale + offset
              .copyProperties(img, ['system:time_start']);
}

// --- 5. MERGE ALL SENSORS ----------------------------------------------
var L5 = ee.ImageCollection('LANDSAT/LT05/C02/T1_L2').map(function(i){return prep(i,'old');});
var L7 = ee.ImageCollection('LANDSAT/LE07/C02/T1_L2').map(function(i){return prep(i,'old');});
var L8 = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2').map(function(i){return prep(i,'new');});
var L9 = ee.ImageCollection('LANDSAT/LC09/C02/T1_L2').map(function(i){return prep(i,'new');});
var landsat = L5.merge(L7).merge(L8).merge(L9).filterBounds(aoi);

// --- 6. VISUALIZATION ---------------------------------------------------
// True color: vegetation green, built-up grey (matches narration "hijau -> abu-abu")
var vis = {bands: ['red','green','blue'], min: 0.0, max: 0.30, gamma: 1.2};
// False-color alternative (vegetation bright red, urban cyan/grey):
// var vis = {bands: ['nir','red','green'], min: 0.0, max: 0.35, gamma: 1.2};

// --- 7. ONE ANNUAL COMPOSITE PER YEAR (median) -> RGB FRAMES ------------
// Optional burned-in year label (community text package). Comment out the
// 3 marked lines if you'd rather add the year counter in Remotion.
var text = require('users/gena/packages:text');                       // label
var labelPt = ee.Geometry.Point(                                      // label
  ee.List(ee.List(aoi.coordinates().get(0)).get(3)));  // top-left     // label

var years = ee.List.sequence(startYear, endYear);
var frames = ee.ImageCollection(ee.List(years).map(function(y){
  y = ee.Number(y);
  var annual = landsat
      .filterDate(ee.Date.fromYMD(y,1,1), ee.Date.fromYMD(y,12,31))
      .median();
  var rgb = annual.visualize(vis).clip(aoi);
  var lbl = text.draw(y.format('%d'), labelPt, 80,                    // label
            {fontSize:32, textColor:'ffffff',                        // label
             outlineColor:'000000', outlineWidth:2});                // label
  return rgb.blend(lbl).set('year', y);                              // (use `return rgb;` if no label)
}));

// --- 8. QUICK PREVIEW ---------------------------------------------------
Map.addLayer(ee.Image(frames.first()), {}, String(startYear));
Map.addLayer(ee.Image(frames.sort('year', false).first()), {}, String(endYear));
print('Animation preview:', ui.Thumbnail(frames, {
  dimensions: 600, framesPerSecond: 4, region: aoi, crs: 'EPSG:3857'
}));

// --- 9. EXPORT THE VIDEO (run from the Tasks tab) ----------------------
Export.video.toDrive({
  collection: frames,
  description: 'urban_sprawl_timelapse',
  dimensions: 1080,           // square-ish output (AOI is square); good for X
  framesPerSecond: 4,         // 4 fps ~ 10 s for 1985–2025; lower = slower
  region: aoi,
  crs: 'EPSG:3857'
});

// TIPS
// - Blank early frames = no Landsat coverage that year -> raise startYear.
// - Stripes 2003–2013 = Landsat-7 SLC-off; median hides most. Prefer L5/L8 years.
// - For a smoother clip, export at framesPerSecond 2 and slow further in Remotion.
// - Stronger sawah->urban contrast: switch to the false-color `vis` above.
