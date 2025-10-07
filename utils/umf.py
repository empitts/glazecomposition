# glaze_umf_calculator.py

OXIDE_MW = {
    'SiO2': 60.09, 'B2O3': 69.62, 'Al2O3': 101.96, 'Li2O': 29.88, 'Na2O': 61.98, 'K2O': 94.20,
    'MgO': 40.31, 'CaO': 56.08, 'SrO': 103.62, 'BaO': 153.70, 'ZnO': 81.39, 'Fe2O3': 159.70,
    'TiO2': 80.90, 'MnO': 70.94, 'CuO': 79.55, 'CoO': 74.93, 'Cr2O3': 151.99, 'NiO': 74.69,
    'V2O5': 181.88, 'SnO2': 150.71, 'ZrO2': 123.22, 'PbO': 223.20, 'Sb2O3': 291.52, 'MoO3': 143.94
}

INGREDIENTS = {
    'EPK': {'SiO2': 46.69, 'Al2O3': 36.32, 'K2O': 0.17, 'MgO': 0.12, 'CaO': 0.26},
    'Flint': {'SiO2': 98.54},
    'Neph Sy': {'SiO2': 61.66, 'Al2O3': 22.63, 'Na2O': 10.07, 'K2O': 5.03, 'CaO': 0.47},
}

INGREDIENT_ALIASES = {
    'EPK': ['Kaolin', 'Kaoline'],
    'Flint': ['Silica', 'Quartz'],
    'Neph Sy': ['Nepheline Syenite', 'NephSyenite']
}

FLUX_OXIDES = ['Na2O', 'K2O', 'Li2O', 'CaO', 'MgO', 'BaO', 'SrO', 'ZnO']
COLORANTS_OPACIFIERS = ['Fe2O3', 'TiO2', 'MnO', 'CuO', 'CoO', 'Cr2O3', 'NiO', 'V2O5', 'SnO2', 'ZrO2', 'PbO', 'Sb2O3', 'MoO3']

def resolve_ingredient_name(name):
    lowered = name.lower()
    for canonical in INGREDIENTS:
        if canonical.lower() == lowered:
            return canonical
    for canonical, aliases in INGREDIENT_ALIASES.items():
        if any(alias.lower() == lowered for alias in aliases):
            return canonical
    return None

def compute_umf(recipe):
    total_moles = {}
    for ing_name, weight in recipe:
        resolved = resolve_ingredient_name(ing_name)
        if not resolved:
            print(f"Warning: Ingredient '{ing_name}' not found.")
            continue
        for oxide, wt_percent in INGREDIENTS[resolved].items():
            if oxide in OXIDE_MW:
                moles = (weight * (wt_percent / 100)) / OXIDE_MW[oxide]
                total_moles[oxide] = total_moles.get(oxide, 0) + moles

    total_flux_moles = sum(total_moles.get(oxide, 0) for oxide in FLUX_OXIDES)
    if total_flux_moles == 0:
        print("Error: Total flux moles is zero. Cannot normalize.")
        return {}

    umf = {}
    for oxide in sorted(set(total_moles.keys()) | set(COLORANTS_OPACIFIERS)):
        umf[oxide] = total_moles.get(oxide, 0) / total_flux_moles

    return umf

def main():
    recipe = [('kaolin', 20), ('quartz', 30), ('nepheline syenite', 50)]
    umf = compute_umf(recipe)

    print("\n--- Unity Molecular Formula ---")
    print("Fluxes:")
    for oxide in FLUX_OXIDES:
        print(f"  {oxide}: {umf.get(oxide, 0):.3f}")

    print("\nGlass Formers:")
    for oxide in ['SiO2', 'Al2O3', 'B2O3']:
        print(f"  {oxide}: {umf.get(oxide, 0):.3f}")

    print("\nColorants & Opacifiers:")
    for oxide in COLORANTS_OPACIFIERS:
        print(f"  {oxide}: {umf.get(oxide, 0):.3f}")

if __name__ == "__main__":
    main()
