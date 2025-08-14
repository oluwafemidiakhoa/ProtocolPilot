# qPCR (SYBR Green) — RUO
> **Research Use Only (not for diagnostic or clinical use).**

## Overview
Quantify target DNA using SYBR Green chemistry on ABI 7500 or Bio-Rad CFX96. Optimized for 20 µL reactions in 96-well plates.

## Materials (see BOM for SKUs)
- 2× SYBR Green qPCR Master Mix
- Forward/Reverse primers (10 µM each)
- Nuclease-free water
- Template DNA (10–100 ng per reaction)
- 96-well qPCR plate + optical seal
- qPCR instrument (ABI 7500 or CFX96)

## Reaction setup (per 20 µL well)
- 10.0 µL 2× Master Mix  
- 0.8 µL Forward primer (10 µM)  
- 0.8 µL Reverse primer (10 µM)  
- 6.4 µL Nuclease-free water  
- 2.0 µL Template DNA  

Prepare a master mix for **N + 10%** wells. Keep on ice.

## Plate loading
1. Dispense **18 µL** master mix into each well.  
2. Add **2 µL** template or water (NTC).  
3. Seal, quick-spin, and inspect for bubbles.

## Cycling program
- **Initial denaturation:** 95 °C 2 min  
- **40 cycles:** 95 °C 15 s; 60 °C 60 s (acquire)  
- **Melt curve:** instrument default

> Adjust annealing temperature to primer Tm as needed (±2 °C).

## Guardrails (automatic QC)
- Flag **Ct > 35** as low input or inhibition.  
- Flag **NTC Ct < 38** as potential contamination.  
- Melt curve with >1 peak → likely off-target amplification.

## Notes
- Use filter tips; prepare master mixes in a clean area.  
- Store aliquoted master mix to minimize freeze-thaw cycles.  
- For multiplex or probes (TaqMan), parameters differ.  

## References
- Bustin et al. Nat Protoc (2009) 4: 787–799.  
- MIQE guidelines (2019 update).
