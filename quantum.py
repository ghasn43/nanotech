import streamlit as st
import py3Dmol
from ase.build import molecule

st.set_page_config(page_title="NanoTech Lab Studio", layout="wide")

st.title("🧪 Nanotech Lab Studio - Interactive")

molecule_choice = st.selectbox("Select Molecule:", ["H2O", "CH4", "NH3", "CO2"])
atoms = molecule(molecule_choice)

# Convert to XYZ format
xyz = atoms.get_chemical_symbols()
coords = atoms.get_positions()

xyz_str = f"{len(xyz)}\n{molecule_choice}\n"
for i, atom in enumerate(xyz):
    x, y, z = coords[i]
    xyz_str += f"{atom} {x:.4f} {y:.4f} {z:.4f}\n"

# Interactive 3D viewer
viewer = py3Dmol.view(width=400, height=400)
viewer.addModel(xyz_str, "xyz")
viewer.setStyle({'stick': {}})
viewer.zoomTo()

st.subheader("3D Interactive Structure")
st.components.v1.html(viewer._make_html(), height=450)
