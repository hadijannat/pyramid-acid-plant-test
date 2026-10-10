# Gate G0: Petrie's figures against the scanned book

Source checked: W. M. F. Petrie, The Pyramids and Temples of Gizeh (1883), archive.org item
cu31924012038927 (Cornell copy), two files of the same scan:
- OCR text, cu31924012038927_djvu.txt, 734,588 bytes:
  https://archive.org/download/cu31924012038927/cu31924012038927_djvu.txt
- page images, cu31924012038927.pdf, 9,301,272 bytes:
  https://archive.org/download/cu31924012038927/cu31924012038927.pdf

Method: for each ledger entry whose source names Petrie, the printed figure was first searched
for in the OCR text and read in its context. A figure that the text did not settle (not found,
too garbled to pair with its row, or printed differently from the ledger) was then read on the
image of its page in the PDF. "metres" quotes the ledger value. The reference for each figure is
Petrie's section number, as cited in the ledger.

"read on" is "text" for a figure settled in the OCR text, where no page was looked up. Otherwise
it is the page of the PDF on whose image the figure was read, counted from the first page of the
file. It is not the number printed at the head of the page.

Verdicts:
- yes: the book prints the figure the ledger was converted from.
- corrected: the page image prints a different figure; the ledger entry was changed in the same
  commit and its note keeps the old figure after "was:".
There is no verdict for a figure that could not be read. The gate stays shut until it is read.

| ledger id | Petrie section | printed value | metres | matches ledger? | read on |
|---|---|---|---|---|---|
| pyr.base_side | s.21 | 9068.8 in | 230.3475 m | yes | text |
| pyr.core_base_side | s.20 | 9001.5 in +/- 1 | 228.6381 m | yes | 77 |
| pyr.casing_thickness | s.25-26 | 71 in | 1.8034 m | yes | text |
| pyr.face_slope | s.24-25 | 51 deg 52 min +/- 2 min adopted mean | 51.8667 deg | yes | text |
| pyr.height_original | s.25 | 5776 in +/- 7 | 146.7104 m | yes | text |
| pyr.height_present | s.25 | 5408.5 in | 137.3759 m | yes | 82 |
| pyr.top_platform_half_width | s.25 | 217.8 in | 5.5321 m | yes | 82 |
| pyr.passage_plane_x | s.64 | 287 in +/- 0.8 | 7.2898 m | yes | 134 |
| dp.entrance.x | s.64 | 287 in +/- 0.8 | 7.2898 m | yes | 134 |
| dp.entrance.y | s.64 | 4010 in +/- 0.3 | 101.854 m | yes | 134 |
| dp.entrance.z | s.64 | 668.2 in +/- 0.1 | 16.9723 m | yes | 134 |
| dp.south_end.x | s.64 | 286.4 in +/- 1 | 7.2746 m | yes | 134 |
| dp.south_end.y | s.64 | 306 in +/- 2 | 7.7724 m | yes | 134 |
| dp.south_end.z | s.64 | -1181 in +/- 1 | -29.9974 m | yes | 134 |
| dp.angle | s.36 | 26 deg 31 min 23 s +/- 5 s over the whole length | 26.5231 deg | yes | text |
| dp.width | s.30 | 41.53 in | 1.0549 m | yes | text |
| dp.height | s.30 | 47.24 in | 1.1999 m | yes | text |
| dp.junction_distance | s.38 | 1110.64 in +/- 0.1 | 28.2103 m | yes | 101 |
| dp.rock_entry_distance | s.35 | 1163.6 in; 1350.7 in (stations; midpoint) | 31.94 m | yes | 95 |
| dp.horizontal.length | s.37 | 346 in | 8.7884 m | yes | 98 |
| dp.horizontal.width | s.37 | 32.45 in | 0.8242 m | yes | 98 |
| dp.horizontal.height | s.37 | about 38 in by Petrie's floor and roof levels, table alignment uncertain | 0.9652 m | yes | 98 |
| dp.horizontal_end.x | s.64 | 286.3 in +/- 1 | 7.272 m | yes | 134 |
| dp.horizontal_end.y | s.64 | -40 in +/- 2 | -1.016 m | yes | 134 |
| dp.horizontal_end.z | s.64 | -1178 in +/- 1 | -29.9212 m | yes | 134 |
| sub.roof_centre.x | s.64 | 25.9 in +/- 2 | 0.6579 m | yes | 134 |
| sub.roof_centre.y | s.64 | -203 in +/- 2 | -5.1562 m | yes | 134 |
| sub.roof_centre.z | s.64 | -1056 in +/- 2 | -26.8224 m | yes | 134 |
| sub.length_ew | s.37 | 553.8 in | 14.0665 m | yes | 98 |
| sub.width_ns | s.37 | 325.9 in | 8.2779 m | yes | 98 |
| sub.floor_depth_east | s.37 | 140 in | 3.556 m | yes | text |
| sub.floor_depth_knob | s.37 | 155 in | 3.937 m | yes | 99 |
| sub.floor_depth_pit | s.37 | 198 in | 5.0292 m | yes | text |
| sub.west_rock_clearance | s.37 | 10 in | 0.254 m | yes | text |
| pit.side | s.37 | 01 table F uses about 1.9 m | 1.9 m | yes | 99 |
| pit.ledge.z | s.37 | -1321 in | -33.5534 m | yes | text |
| pit.ledge_depth | s.37 | 67 in | 1.7018 m | yes | text |
| pit.lower_side | s.37 | 01 table F uses 1.4 m | 1.4 m | yes | text |
| pit.lower_depth_original | s.37 | 40 in | 1.016 m | yes | text |
| sp.north_end.x | s.64 | 284.9 in +/- 1 | 7.2365 m | yes | 134 |
| sp.north_end.y | s.64 | -366 in +/- 2 | -9.2964 m | yes | 134 |
| sp.north_end.z | s.64 | -1219 in +/- 1.5 | -30.9626 m | yes | 134 |
| sp.south_end.x | s.64 | 277.1 in | 7.0383 m | yes | 134 |
| sp.south_end.y | s.64 | -1012 in +/- 3 | -25.7048 m | yes | 134 |
| sp.south_end.z | s.64 | -1213 in +/- 2 | -30.8102 m | yes | 134 |
| sp.length | s.37 | 646 in | 16.4084 m | yes | 98 |
| sp.width | s.37 | 01 table F uses 0.72 m | 0.72 m | yes | 98 |
| ws.mouth_near_edge | s.46 | 21.8 in | 0.5537 m | yes | text |
| ws.mouth_far_edge | s.46 | 49 in | 1.2446 m | yes | text |
| grotto.height | s.46 | height of the lined stretch of well-shaft segment 3 through the Grotto: Haase 'over 2 m' in ten courses, Petrie ten courses of 7.25 to 8 in | 2.0 m | yes | 113 |
| ap.start.x | s.64 | 286.6 in +/- 0.8 | 7.2796 m | yes | 134 |
| ap.start.y | s.64 | 3016.3 in +/- 0.3 | 76.614 m | yes | 134 |
| ap.start.z | s.64 | 172.9 in +/- 0.2 | 4.3917 m | yes | 104 |
| ap.end.x | s.64 | 287 in +/- 1.5 | 7.2898 m | yes | 134 |
| ap.end.y | s.64 | 1626.8 in +/- 0.8 | 41.3207 m | yes | 134 |
| ap.end.z | s.64 | 852.6 in +/- 0.3 | 21.656 m | yes | 134 |
| ap.angle | s.38-39 | mean 26 deg 2 min 30 s | 26.0417 deg | yes | 100 |
| ap.length | s.38-39 | 1546.8 in | 39.2887 m | yes | text |
| ap.width | s.38 | 41.6 in | 1.0566 m | yes | text |
| ap.height | s.38 | 47.3 in | 1.2014 m | yes | text |
| ap.plug_start | s.38 | 74.2 in | 1.8847 m | yes | text |
| ap.plug_length | s.38 | 178.5 in | 4.5339 m | yes | text |
| ap.plug_width | s.38 | 38.2 in lower end, 41.6 in upper end | 0.9919 m | corrected | 102 |
| qp.length | s.40 | 1523.9 in | 38.7071 m | yes | 105 |
| qp.step_distance | s.40 | 1307 in | 33.1978 m | yes | 105 |
| qp.floor_north.z | s.40 | 854.6 in | 21.7068 m | yes | 105 |
| qp.floor_south.z | s.40 | 834.9 in | 21.2065 m | yes | 105 |
| qc.north_wall.y | s.64 | 102 in +/- 0.8 | 2.5908 m | yes | 134 |
| qc.east_wall.x | s.64 | 308 in +/- 3 | 7.8232 m | yes | 134 |
| qc.floor.z | s.64 | 834.4 in +/- 0.4 | 21.1938 m | yes | 134 |
| qc.length_ew | s.41 | 226.47 in +/- 0.2 | 5.7523 m | yes | 105 |
| qc.width_ns | s.41 | 205.85 in +/- 0.2 | 5.2286 m | yes | 105 |
| qc.wall_height | s.41 | 184.47 in | 4.6855 m | yes | text |
| qc.ridge_height | s.41 | 245.1 in | 6.2255 m | yes | text |
| qc.ridge.z | s.64 | 1078.7 in | 27.399 m | yes | 134 |
| qc.niche.depth | s.43 | 41 in +/- 0.3 | 1.0414 m | yes | 109 |
| qc.niche.width_base | s.43 | 62 in +/- 0.3 | 1.5748 m | yes | 109 |
| qc.niche.width_top | s.43 | 20 in +/- 0.3 | 0.508 m | yes | 109 |
| qc.niche.overlaps | s.43 | number of quarter-cubit overlaps | 4.0 1 | yes | text |
| qc.niche.top_width_level | s.43 | 156 in +/- 0.3 | 3.9624 m | yes | 109 |
| qc.niche.height | s.43 | 184 in +/- 0.3 | 4.6736 m | yes | 109 |
| qcs.width | s.44 | about 8 in wide | 0.2032 m | yes | text |
| qcs.north.height | s.44 | 8.6 in | 0.2184 m | yes | text |
| qcs.south.height | s.44 | 8.8 in | 0.2235 m | yes | text |
| qcs.north.horizontal_length | s.44 | 76 in | 1.9304 m | yes | text |
| qcs.south.horizontal_length | s.44 | 80 in | 2.032 m | yes | 109 |
| qcs.north.angle | s.44 | mean 37 deg 28 min, lower sections only, goniometer | 37.4667 deg | yes | text |
| qcs.south.angle | s.44 | mean 38 deg 28 min, lower sections only | 38.4667 deg | yes | text |
| qcs.north.projected_exit.z | s.44 | 2641.3 in | 67.089 m | yes | text |
| qcs.south.projected_exit.z | s.44 | 2679.1 in | 68.0491 m | yes | 110 |
| gg.north_end.x | s.64 | 287 in +/- 1.5 | 7.2898 m | yes | 134 |
| gg.north_end.y | s.64 | 1626.8 in +/- 0.8 | 41.3207 m | yes | 134 |
| gg.north_end.z | s.64 | 852.6 in +/- 0.3 | 21.656 m | yes | 134 |
| gg.south_end.x | s.64 | 284.4 in +/- 3 | 7.2238 m | yes | 134 |
| gg.south_end.y | s.64 | -61.7 in +/- 0.9 | -1.5672 m | yes | 134 |
| gg.south_end.z | s.64 | 1689 in +/- 0.5 | 42.9006 m | yes | 134 |
| gg.step_face.y | s.64 | -0.4 in +/- 0.9 | -0.0102 m | yes | 134 |
| gg.step_top.z | s.64 | 1694.1 in +/- 0.7 | 43.0301 m | yes | 134 |
| gg.floor_length | s.45 | 1883.6 in | 47.8434 m | yes | text |
| gg.floor_length_to_step | s.45 | 1815.5 in | 46.1137 m | yes | 110 |
| gg.roof_length_horizontal | s.46 | 1648.4 in | 41.8694 m | yes | text |
| gg.roof_length_sloping | s.46 | 1838.6 in | 46.7004 m | yes | text |
| gg.angle | s.45 | 26 deg 16 min 40 s | 26.2778 deg | yes | text |
| gg.width | s.30 | 82.42 in | 2.0935 m | yes | text |
| gg.slot_width | s.30, s.46 | 41.2 in = 2 cubits of 20.6 in (not printed) | 1.0465 m | yes | 113 |
| gg.roof_width | s.46 | 41.1 in | 1.0439 m | yes | 112 |
| gg.ramp_height | s.30 | 23.86 in | 0.606 m | yes | text |
| gg.overhang | s.46 | 20.55 in | 0.522 m | yes | text |
| gg.laps | s.46 | number of corbel laps per side | 7.0 1 | yes | text |
| gg.step_height | s.46 | 35.36 in | 0.8981 m | yes | 114 |
| gg.step_length | s.46 | 61.25 in | 1.5557 m | yes | text |
| ante.north_end.y | s.64 | -113.7 in +/- 0.9 | -2.888 m | yes | 134 |
| ante.south_end.y | s.64 | -229.8 in +/- 0.9 | -5.8369 m | yes | 134 |
| ante.floor.z | s.64 | 1692.6 in +/- 0.6 | 42.992 m | yes | 134 |
| ante.roof.z | s.64 | 1841.5 in +/- 0.6 | 46.7741 m | yes | 134 |
| ante.x | s.64 | 284.4 in | 7.2238 m | yes | 134 |
| ante.length | s.48 | 116.3 in | 2.954 m | yes | text |
| ante.width | s.48 | 65 in | 1.651 m | yes | 116 |
| ante.height | s.48 | 149.35 in | 3.7935 m | yes | 116 |
| ante.leaf_thickness | s.50 | 15.68 in | 0.3983 m | yes | 117 |
| ante.leaf_width | s.50 | 40.9 in | 1.0389 m | yes | 118 |
| ante.leaf_top_below_ceiling | s.50 | 55.12 in | 1.4 m | yes | text |
| ante.groove_count | s.49 | vertical grooves in the S wall | 4.0 1 | yes | text |
| ante.groove_depth | s.49 | 2.8 in | 0.0711 m | yes | 117 |
| ante.passage_from_gg.length | s.47 | 52.02 in | 1.3213 m | yes | 114 |
| ante.passage_to_kc.length | s.47 | 100.8 in | 2.5603 m | yes | 115 |
| kc.north_wall.y | s.64 | -330.9 in +/- 0.9 | -8.4049 m | yes | 134 |
| kc.south_wall.y | s.55 | -537 in +/- 0.8 | -13.6398 m | yes | 122 |
| kc.east_wall.x | s.64 | 305 in +/- 3 | 7.747 m | yes | 134 |
| kc.west_wall.x | s.55 | -107.7 in +/- 3 | -2.7356 m | yes | 122 |
| kc.floor.z | s.55, s.64 | 1692.8 in | 42.9971 m | yes | 134 |
| kc.wall_base.z | s.55, s.64 | 1688.5 in | 42.8879 m | yes | text |
| kc.ceiling.z | s.55 | 1922.65 in | 48.8353 m | yes | text |
| kc.length | s.52 | 412.25 in | 10.4711 m | yes | 119 |
| kc.width | s.52 | 206.13 in | 5.2357 m | yes | 119 |
| kc.height | s.55 | 230.1 in | 5.8445 m | yes | text |
| kc.coffer.length | s.59 | 89.62 in | 2.2763 m | yes | text |
| kc.coffer.width | s.59 | 38.5 in | 0.9779 m | yes | text |
| kc.coffer.height | s.59 | 41.31 in | 1.0493 m | yes | 125 |
| kc.coffer.inner_length | s.59 | 78.06 in | 1.9827 m | yes | 125 |
| kc.coffer.inner_width | s.59 | 26.81 in | 0.681 m | yes | text |
| kc.coffer.inner_depth | s.59 | 34.42 in | 0.8743 m | yes | 125 |
| kc.coffer.solid_volume | s.61 | 70,500 in3 of stone | 1.155 m3 | yes | 129 |
| kcs.north.width | s.56 | 9.05 in | 0.2299 m | yes | 123 |
| kcs.north.height | s.56 | 8.73 in | 0.2217 m | yes | text |
| kcs.south.width | s.56 | 8.5 in | 0.2159 m | yes | text |
| kcs.south.height | s.56 | 8.8 in | 0.2235 m | yes | text |
| kcs.north.angle | s.56 | mean 31 deg 33 min over the outermost surviving part | 31.55 deg | yes | 122 |
| kcs.south.angle | s.56 | mean 45 deg 13 min 40 s | 45.2278 deg | yes | text |
| rc.davison_passage.width | s.62 | 26.3 in | 0.668 m | yes | text |
| rc.davison_passage.height | s.62 | 29.4 in | 0.7468 m | yes | text |
| hydro.joint_aperture | s.26 | 0.020 in mean casing joint | 0.000508 m | yes | text |
| plateau.khafre_chamber.length | s.73, s.75 | 557.9 in | 14.1707 m | yes | text |
| plateau.khafre_chamber.width | s.73, s.75 | 195.8 in | 4.9733 m | yes | text |
| plateau.khafre_chamber.wall_height | s.73, s.75 | 206.4 in | 5.2426 m | yes | text |
| plateau.khafre_chamber.ridge_height | s.73, s.75 | 244.4 in | 6.2078 m | yes | text |

## Notes on rows

None of these changed a verdict; every row below is `yes`. They are the places where the ledger and the book are not word for word the same thing, kept here so that nobody has to rediscover them.

- `ap.start.z`: the table of section 64 (PDF page 134) prints +179.9 +/- .2 for the beginning of the Ascending Passage. Section 39 (PDF page 104) prints "(172.9 + 679.7) = 852.6 +/- .3 level above pavement", which closes with the level of the Gallery end (852.6), so the ledger keeps 172.9. The row is read on page 104.
- `kc.south_wall.y`, `kc.west_wall.x`: the ledger cited section 64, but the table has no S-wall or W-wall row. The figures (S wall 537.0 +/- .8 from the centre, W wall 107.7 +/- 3.0 W of the centre) are printed in section 55 (PDF page 122); the rows are read there, and after the gate the ledger `source` of both was changed from `s.64` to `s.55` (values and notes unchanged).
- `kc.east_wall.x`: the table prints 305.0 +/- 3 (the ledger value); section 55 prints 305.1 +/- 3.0.
- `kc.north_wall.y`: the ledger value 330.9 is the table's "King's Chamber, floor" row; the table's "N.E. wall base" row and section 55 print 330.6.
- `kc.wall_base.z`: settled in the text of section 55 (1686.3 to 1688.5); the table of section 64 (PDF page 134) also prints +1688.5 +/- .6.
- `ante.x`: the table prints "same?" in the column for the distance east of the centre; 284.4 is the figure of the Gallery row above it.
- `ante.roof.z`: the table prints +1841.5 +/- .6 (the ledger value); the text of section 49 (PDF page 116) prints 1841.8 +/- .6 for the ceiling over the virtual end of the Gallery floor.
- `kcs.north.width`: the ledger value 9.05 is the midpoint of the printed 8.9 to 9.2; Petrie prints "(mean 9.0)" (PDF page 123).
- `ap.plug_width` (`corrected`): the page (PDF page 102) prints 38.2 at the lower end of the plug and 41.6 at the upper end. The ledger's `high` was 39.9 in = 1.0135 m, a midpoint of those two and not a printed figure; it is now 41.6 in = 1.0566 m, so the range is the printed pair. `value` 0.9919 m (39.05 in, research/01's weighted mean (3 x 38.2 + 41.6) / 4, not a printed figure) and `low` 0.9703 m (38.2 in) are unchanged; the note was rewritten to say so. Old high: 1.0135, new high: 1.0566. (The ledger note does not carry a "was:" figure; the old high is recorded here and in the task report.)
- `gg.slot_width`: Petrie writes "2 cubits" for the space between the ramps (PDF page 113) and gives the cubit as 20.6 in (PDF page 109); 41.2 is 2 x 20.6, not a printed figure. The ledger note now says so; the value is unchanged.
- `pyr.height_present`: the ledger 5408.5 is the mean of the printed 5407.9 and 5409.2 (5408.55, rounded down); `kc.length`: 412.25 is the mean of the printed 412.40 and 412.11 (412.255, rounded down).
- `dp.rock_entry_distance` (`yes`, `verified: false`): the ledger's stations 1164 and 1351 are the rounded forms of the printed 1163.6 (table of section 35, column "E. Wall Top", PDF page 95) and 1350.7 (column "E. Roof"; the text of section 35, PDF page 96, calls it the beginning of the rock on the E side of the roof). Both figures are printed, so the row is `yes`. But 1163.6 is not a rock station: it is where Petrie's rod measuring resumes ("by rods from 1163.6 to the rock", PDF page 95), and the book marks "Rock." only against 1318.5, 1340.1, 1347.5 and 1350.7. The ledger value (31.94 m, research/01's midpoint of 1163.6 and 1350.7) therefore rests on a reading the book does not print, and `verified` stays false, with the note saying so, pending the owner's decision on moving the entry to the printed rock stations (1318.5 to 1350.7 in, 33.5 to 34.3 m). Value, low and high are unchanged.
- `dp.horizontal.height`: the ledger's 38 in is the printed floor level -1181 less the printed roof level -1143; the same table also prints "Top + 38.3" and "Top + 38.9" for the roof above the floor end.
- `gg.floor_length_to_step`: Petrie's row is "Ramp End 1815.5"; the ramps stop 0.30 (E) and 0.44 (W) in short of the step face.
- `qc.length_ew`, `qc.width_ns`, `qc.niche.*`: the figures are printed; the "+/-" values in the ledger are not printed errors (the book gives these figures without one).
- `sub.width_ns`: the OCR text reads the width at 100 in from the W wall as 319.6; the page image prints 329.6 (with a query), which is what the ledger says. The OCR misread that digit.

## Result

Checked on 2026-10-10 by Claude (implementer of Task 8, for the project owner). The PDF has 315 pages.

- yes: 155, of which 60 were read in the OCR text and 95 on a page image
- corrected: 1 (ap.plug_width: `high` 1.0135 m to 1.0566 m, the printed 41.6 in; `value` and `low` unchanged)

Every ledger entry that cites Petrie was read in the scan of the 1883 book. No figure was left unread.
