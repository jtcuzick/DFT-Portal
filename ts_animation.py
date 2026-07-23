from pathlib import Path
import math

import cclib
import py3Dmol


ELEMENTS = {
    1: "H",
    5: "B",
    6: "C",
    7: "N",
    8: "O",
    9: "F",
    14: "Si",
    15: "P",
    16: "S",
    17: "Cl",
    35: "Br",
    53: "I",
}


def load_ts_mode(log_path):
    """
    Read a Gaussian frequency calculation and extract
    the transition-state geometry and imaginary normal mode.
    """

    log_path = Path(log_path)

    if not log_path.exists():
        raise FileNotFoundError(
            f"Could not find Gaussian log file: {log_path}"
        )

    data = cclib.io.ccread(str(log_path))

    if data is None:
        raise ValueError(
            "cclib could not parse the Gaussian log file."
        )

    # Final optimized geometry
    coords = data.atomcoords[-1]

    # Atomic numbers
    atomic_numbers = data.atomnos

    # Make sure frequencies exist
    if not hasattr(data, "vibfreqs"):
        raise ValueError(
            "No vibrational frequencies were found in this file."
        )

    frequencies = data.vibfreqs

    # Find imaginary frequencies
    imaginary_indices = [
        i
        for i, frequency in enumerate(frequencies)
        if frequency < 0
    ]

    if not imaginary_indices:
        raise ValueError(
            "No imaginary frequencies were found."
        )

    # Pick the most negative imaginary frequency
    mode_index = min(
        imaginary_indices,
        key=lambda i: frequencies[i]
    )

    imaginary_frequency = frequencies[mode_index]

    # Make sure displacement vectors exist
    if not hasattr(data, "vibdisps"):
        raise ValueError(
            "No vibrational displacement vectors were found."
        )

    displacement = data.vibdisps[mode_index]

    return {
        "coords": coords,
        "atomic_numbers": atomic_numbers,
        "frequency": imaginary_frequency,
        "displacement": displacement,
    }


def generate_xyz_frames(
    coords,
    atomic_numbers,
    displacement,
    frequency,
    n_frames=30,
    amplitude=0.7,
):
    """
    Generate XYZ frames by moving the atoms along
    the imaginary-frequency normal mode.
    """

    frames = []

    for frame_number in range(n_frames):

        phase = (
            2
            * math.pi
            * frame_number
            / n_frames
        )

        scale = amplitude * math.sin(phase)

        displaced_coords = (
            coords
            + scale * displacement
        )

        xyz_lines = [
            str(len(atomic_numbers)),
            f"Imaginary frequency: {frequency:.2f} cm^-1",
        ]

        for atomic_number, xyz in zip(
            atomic_numbers,
            displaced_coords,
        ):

            element = ELEMENTS.get(
                int(atomic_number),
                "X",
            )

            x, y, z = xyz

            xyz_lines.append(
                f"{element:<2} "
                f"{x:12.6f} "
                f"{y:12.6f} "
                f"{z:12.6f}"
            )

        frames.append(
            "\n".join(xyz_lines)
        )

    return frames

def build_ts_viewer(
    frames,
    width=380,
    height=350,
):
    """
    Create an animated 3D molecular viewer.
    """

    viewer = py3Dmol.view(
        width=width,
        height=height,
    )

    trajectory = "\n".join(frames)

    viewer.addModelsAsFrames(
        trajectory,
        "xyz",
    )

    custom_colors = {
        "H":  "white",  # very light gray / white
        "C":  "#D9D9D9",  # softened black
        "N":  "#6FA8DC",  # light blue
        "O":  "#E57373",  # light red
        "F":  "#81C784",  # light green
        "P":  "#FFB74D",  # light orange
        "S":  "#FFD54F",  # light yellow
        "Cl": "#81C784",  # light green
        "Br": "#BCAAA4",  # light brown
        "I":  "#B39DDB",  # light purple
        "B":  "#F48FB1",  # light pink
    }

    viewer.setStyle(
        {},
        {
            # All bonds gray
            "stick": {
                "radius": 0.10,
                "color": "black",
            },

            # Atoms retain element colors
            "sphere": {
                "scale": 0.20,
                "colorscheme": {
                    "prop": "elem",
                    "map": custom_colors,
                },
            },
        },
    )

    viewer.zoomTo()

    viewer.animate(
        {
            "loop": "backAndForth",
            "reps": 0,
            "interval": 80,
        }
    )

    viewer.spin(
        "y",
        0.5,
    )

    return viewer
