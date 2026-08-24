"""Hand-labeled matching sample used for the Phase 6 accuracy test.

Each entry is ``(gem_title, market_title, is_match)``. ``is_match`` is the
human judgment: do these two titles refer to the same (or sufficiently
similar) product? Labels were written by hand, mixing true matches with
near-misses and obvious non-matches. The market titles are written in the
style of real Amazon/Flipkart listings for the same category.
"""

SAMPLE = [
    # --- Laptops ---
    ("acer Intel Core i5 1245U Mid Level Laptop Notebook",
     "Acer Aspire 5 Intel Core i5-1245U 12th Gen 15.6 inch Laptop", True),
    ("acer Intel Core i3 1215U Entry Level Laptop Notebook",
     "Acer Aspire Lite Intel Core i3 1215U Laptop", True),
    ("acer AMD Ryzen 5 5625U Mid Level Laptop Notebook",
     "Acer Aspire 3 AMD Ryzen 5 5625U Laptop", True),
    ("acer Intel Core i5 1245U Mid Level Laptop Notebook",
     "Lenovo IdeaPad Intel Core i3 1215U Laptop", False),
    ("acer Intel Core i5 1245U Mid Level Laptop Notebook",
     "HP 15s Intel Core i3 1215U 15.6 inch Laptop", False),
    ("acer AMD Ryzen 5 5625U Mid Level Laptop Notebook",
     "Dell Inspiron AMD Ryzen 7 5825U Laptop", False),
    ("INP Intel Core i5 1245U Mid Level Laptop Notebook",
     "INP Intel Core i5-1245U 12th Gen Laptop", True),
    ("CYNIX Intel Core i5 1245U Mid Level Laptop Notebook",
     "Cynix Intel Core i5 1245U 12th Gen Notebook PC", True),
    ("hp Intel Core i5 1245U Mid Level Laptop Notebook",
     "HP ProBook Intel Core i5-1245U Business Laptop", True),
    ("acer Intel Core i3 1215U Entry Level Laptop Notebook",
     "Acer Aspire Lite 16 inch Intel Core i3 1215U", True),

    # --- Monitors ---
    ("SAMSUNG Vertical Alignment (VA) Computer Monitor with a Power Cable and/or Adapter",
     "Samsung 24 inch 75Hz VA Panel Monitor", True),
    ("acer In Plane Switching (IPS) Computer Monitor with a Power Cable and/or Adapter",
     "Acer 21.5 inch IPS LED Computer Monitor", True),
    ("ALGOPLUS Vertical Alignment (VA) Computer Monitor with a Power Cable and/or Adapter",
     "Algo Plus 27 inch VA Curved Monitor", True),
    ("EDLER Vertical Alignment (VA) Computer Monitor with a Power Cable and/or Adapter",
     "Edler 22 inch VA Panel LED Monitor", True),
    ("VOLTRIQ In Plane Switching (IPS) Computer Monitor with a Power Cable and/or Adapter",
     "Voltric 24 inch IPS FHD Monitor", True),
    ("acer In Plane Switching (IPS) Computer Monitor with a Power Cable and/or Adapter",
     "Samsung 27 inch IPS LED Monitor", False),
    ("SAMSUNG Vertical Alignment (VA) Computer Monitor with a Power Cable and/or Adapter",
     "LG 27 inch VA Curved Gaming Monitor", False),
    ("VOLTRIQ In Plane Switching (IPS) Computer Monitor with a Power Cable and/or Adapter",
     "Voltric 27 inch VA Monitor", False),
    ("EDLER Vertical Alignment (VA) Computer Monitor with a Power Cable and/or Adapter",
     "Edler 24 inch IPS Monitor", False),
    ("ALGOPLUS Vertical Alignment (VA) Computer Monitor with a Power Cable and/or Adapter",
     "Algo Plus 24 inch VA Monitor", True),

    # --- Printers ---
    ("brother A4 and Legal Monochrome (Black) Laser Computer Printer",
     "Brother HL-L2445W A4 Monochrome Laser Printer", True),
    ("Canon A4 and Legal Colour Inkjet Computer Printer",
     "Canon PIXMA G3270 A4 Colour Inkjet Printer", True),
    ("Canon A4 and Legal Monochrome (Black) Laser Computer Printer",
     "Canon imageCLASS LBP225dn A4 Laser Printer", True),
    ("TVS ELECTRONICS A4 and Legal Monochrome (Black) Laser Computer Printer",
     "TVS Electronics A4 Mono Laser Printer", True),
    ("brother A4 and Legal Monochrome (Black) Laser Computer Printer",
     "Epson M1100 A4 Monochrome Inkjet Printer", False),
    ("Canon A4 and Legal Colour Inkjet Computer Printer",
     "HP DeskJet 2331 A4 Colour Inkjet Printer", False),
    ("IMAGE KING A4 Monochrome (Black) Laser Computer Printer",
     "Image King A4 Mono Laser Printer", True),
    ("Canon A3, A4 and Legal Colour Inkjet Computer Printer",
     "Canon PIXMA G2370 A4 Colour Inkjet Printer", False),

    # --- Oxygen concentrators ---
    ("EVOX Oxygen Concentrator 1 LPM , Single Oxygen Outlet",
     "Evox O2 Oxygen Concentrator 1 LPM", True),
    ("medoxy Oxygen Concentrator 2 LPM , Single Oxygen Outlet",
     "MedOx 2 LPM Portable Oxygen Concentrator", True),
    ("DEVILBISS Oxygen Concentrator 5 LPM , Single Oxygen Outlet",
     "DeVilbiss 525DS 5 LPM Oxygen Concentrator", True),
    ("TAURUS HEALTHCARE Oxygen Concentrator 5 LPM , Single or Dual Oxygen Outlet",
     "Taurus 5 LPM Oxygen Concentrator with Dual Outlet", True),
    ("Infi Oxygen Concentrator 3 LPM , Single Oxygen Outlet",
     "Infi 3 LPM Oxygen Concentrator Portable", True),
    ("ORNATE Oxygen Concentrator 8 LPM , Single Oxygen Outlet",
     "Ornate 10 LPM Oxygen Concentrator", False),
    ("NISCOPLAST Oxygen Concentrator 6 LPM , Single Oxygen Outlet",
     "Niscoplast 6 LPM Home Oxygen Concentrator", True),
    ("Sleep One Oxygen Concentrator 10 LPM , Single or Dual Oxygen Outlet",
     "SleepOne 10 LPM Oxygen Concentrator", True),
    ("EVOX Oxygen Concentrator 1 LPM , Single Oxygen Outlet",
     "MedOx 2 LPM Oxygen Concentrator", False),
    ("DEVILBISS Oxygen Concentrator 5 LPM , Single Oxygen Outlet",
     "Taurus 5 LPM Oxygen Concentrator", False),
]

TRUE_COUNT = sum(1 for _, _, m in SAMPLE if m)
FALSE_COUNT = len(SAMPLE) - TRUE_COUNT
