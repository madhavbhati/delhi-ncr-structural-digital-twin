"""
OpenSees Finite Element Model: MODEL_284
Tier: 30 Storeys (105.0m) | Slab: 150mm | Wall: 550mm | Col: 1100mm
Concrete: M40 | Soil: Type III | Setback: 15.0%
DTU High-Rise Structural Digital Twin Research
"""

import os
import sys
import math
import csv
import openseespy.opensees as ops

def run_simulation():
    model_id = 284
    storeys = 30
    h_storey = 3.5
    col_w = 1.1
    wall_t = 0.55
    wall_len = 6.0
    slab_t = 0.15
    fck = 40.0
    soil = "Type III"
    setback = 15.0
    total_h = storeys * h_storey
    floor_area = 576.0 # 24m x 24m
    bays = 4
    bay_w = 6.0
    num_col_lines = 5
    num_frames = 5.0

    cur_dir = os.path.dirname(os.path.abspath(__file__))
    out_dir = os.path.join(cur_dir, "outputs")
    os.makedirs(out_dir, exist_ok=True)

    eigen_file = os.path.join(out_dir, f"MODEL_{model_id:03d}_eigen.out")
    results_file = os.path.join(out_dir, f"MODEL_{model_id:03d}_raw_results.csv")

    # Material properties (IS 456)
    Ec = 5000.0 * math.sqrt(fck) * 1e6 # Pa

    # Cracked section properties (IS 1893:2016 Clause 6.4.3.1)
    Ac = col_w * col_w
    Ic = (col_w * (col_w**3)) / 12.0 * 0.70
    Ab = 0.30 * 0.60
    Ib = (0.30 * (0.60**3)) / 12.0 * 0.35

    # 3D core wall flexural inertia in X direction
    Iw_3d_core = (2.0 * ((wall_t * (wall_len**3)) / 12.0) + 2.0 * (wall_t * wall_len * ((wall_len/2.0)**2))) * 0.70
    Aw_3d_core = 2.0 * (wall_t * wall_len)

    # Floor mass with explicit slab thickness
    w_slab = slab_t * 25.0 # kN/m2
    w_floor_dead = w_slab + 3.0 # finishes + partitions
    w_live_seismic = 0.25 * 3.0 # 25% imposed load
    w_floor_total = w_floor_dead + w_live_seismic
    total_bldg_mass_kg = (floor_area * w_floor_total * 1000.0) / 9.81
    frame_mass_kg = total_bldg_mass_kg / num_frames
    mass_per_node = frame_mass_kg / num_col_lines

    setback_start = int(storeys * 0.80) if setback > 0 else storeys + 1

    ops.wipe()
    ops.model('basic', '-ndm', 2, '-ndf', 3)
    ops.geomTransf('Linear', 1)

    for i in range(num_col_lines):
        tag = i + 1
        ops.node(tag, i * bay_w, 0.0)
        ops.fix(tag, 1, 1, 1)

    node_tag = num_col_lines + 1
    ele_tag = 1
    story_nodes = []
    story_masses_bldg = []

    for s in range(1, storeys + 1):
        y = s * h_storey
        cur_nodes = []
        m_s_bldg = total_bldg_mass_kg
        if s >= setback_start:
            m_s_bldg *= (1.0 - (setback / 100.0))
        story_masses_bldg.append(m_s_bldg)
        m_node = (m_s_bldg / num_frames) / num_col_lines

        for i in range(num_col_lines):
            ops.node(node_tag, i * bay_w, y)
            ops.mass(node_tag, m_node, 1e-6, 1e-6)
            cur_nodes.append(node_tag)
            node_tag += 1
        story_nodes.append(cur_nodes)

    # Frame Columns & Core Wall
    for s in range(storeys):
        bot_nodes = [i + 1 for i in range(num_col_lines)] if s == 0 else story_nodes[s-1]
        top_nodes = story_nodes[s]
        for i in range(num_col_lines):
            if i == 2:
                ops.element('elasticBeamColumn', ele_tag, bot_nodes[i], top_nodes[i], Aw_3d_core / num_frames, Ec, Iw_3d_core / num_frames, 1)
            else:
                ops.element('elasticBeamColumn', ele_tag, bot_nodes[i], top_nodes[i], Ac, Ec, Ic, 1)
            ele_tag += 1

    # Floor Beams & Diaphragms
    for s in range(storeys):
        cur_nodes = story_nodes[s]
        for i in range(bays):
            ops.element('elasticBeamColumn', ele_tag, cur_nodes[i], cur_nodes[i+1], Ab + (24.0/5.0)*slab_t, Ec, Ib, 1)
            ele_tag += 1

    # Modal Analysis
    w2 = ops.eigen(3)
    T1 = 2.0 * math.pi / math.sqrt(w2[0])
    T2 = 2.0 * math.pi / math.sqrt(w2[1])
    T3 = 2.0 * math.pi / math.sqrt(w2[2])

    with open(eigen_file, "w") as ef:
        ef.write(f"MODEL_{model_id:03d} Eigenvalues:\n")
        ef.write(f"Mode 1: T1 = {T1:.6f} s\n")
        ef.write(f"Mode 2: T2 = {T2:.6f} s\n")
        ef.write(f"Mode 3: T3 = {T3:.6f} s\n")

    # Multi-Hazard Cases
    hazards = [{'seismic_scale': 0.8, 'wind_speed': 39.0, 'flood_depth': 0.0}, {'seismic_scale': 0.8, 'wind_speed': 39.0, 'flood_depth': 0.5}, {'seismic_scale': 0.8, 'wind_speed': 39.0, 'flood_depth': 1.0}, {'seismic_scale': 0.8, 'wind_speed': 39.0, 'flood_depth': 1.5}, {'seismic_scale': 0.8, 'wind_speed': 39.0, 'flood_depth': 2.5}, {'seismic_scale': 0.8, 'wind_speed': 44.0, 'flood_depth': 0.0}, {'seismic_scale': 0.8, 'wind_speed': 44.0, 'flood_depth': 0.5}, {'seismic_scale': 0.8, 'wind_speed': 44.0, 'flood_depth': 1.0}, {'seismic_scale': 0.8, 'wind_speed': 44.0, 'flood_depth': 1.5}, {'seismic_scale': 0.8, 'wind_speed': 44.0, 'flood_depth': 2.5}, {'seismic_scale': 0.8, 'wind_speed': 47.0, 'flood_depth': 0.0}, {'seismic_scale': 0.8, 'wind_speed': 47.0, 'flood_depth': 0.5}, {'seismic_scale': 0.8, 'wind_speed': 47.0, 'flood_depth': 1.0}, {'seismic_scale': 0.8, 'wind_speed': 47.0, 'flood_depth': 1.5}, {'seismic_scale': 0.8, 'wind_speed': 47.0, 'flood_depth': 2.5}, {'seismic_scale': 0.8, 'wind_speed': 55.0, 'flood_depth': 0.0}, {'seismic_scale': 0.8, 'wind_speed': 55.0, 'flood_depth': 0.5}, {'seismic_scale': 0.8, 'wind_speed': 55.0, 'flood_depth': 1.0}, {'seismic_scale': 0.8, 'wind_speed': 55.0, 'flood_depth': 1.5}, {'seismic_scale': 0.8, 'wind_speed': 55.0, 'flood_depth': 2.5}, {'seismic_scale': 1.0, 'wind_speed': 39.0, 'flood_depth': 0.0}, {'seismic_scale': 1.0, 'wind_speed': 39.0, 'flood_depth': 0.5}, {'seismic_scale': 1.0, 'wind_speed': 39.0, 'flood_depth': 1.0}, {'seismic_scale': 1.0, 'wind_speed': 39.0, 'flood_depth': 1.5}, {'seismic_scale': 1.0, 'wind_speed': 39.0, 'flood_depth': 2.5}, {'seismic_scale': 1.0, 'wind_speed': 44.0, 'flood_depth': 0.0}, {'seismic_scale': 1.0, 'wind_speed': 44.0, 'flood_depth': 0.5}, {'seismic_scale': 1.0, 'wind_speed': 44.0, 'flood_depth': 1.0}, {'seismic_scale': 1.0, 'wind_speed': 44.0, 'flood_depth': 1.5}, {'seismic_scale': 1.0, 'wind_speed': 44.0, 'flood_depth': 2.5}, {'seismic_scale': 1.0, 'wind_speed': 47.0, 'flood_depth': 0.0}, {'seismic_scale': 1.0, 'wind_speed': 47.0, 'flood_depth': 0.5}, {'seismic_scale': 1.0, 'wind_speed': 47.0, 'flood_depth': 1.0}, {'seismic_scale': 1.0, 'wind_speed': 47.0, 'flood_depth': 1.5}, {'seismic_scale': 1.0, 'wind_speed': 47.0, 'flood_depth': 2.5}, {'seismic_scale': 1.0, 'wind_speed': 55.0, 'flood_depth': 0.0}, {'seismic_scale': 1.0, 'wind_speed': 55.0, 'flood_depth': 0.5}, {'seismic_scale': 1.0, 'wind_speed': 55.0, 'flood_depth': 1.0}, {'seismic_scale': 1.0, 'wind_speed': 55.0, 'flood_depth': 1.5}, {'seismic_scale': 1.0, 'wind_speed': 55.0, 'flood_depth': 2.5}, {'seismic_scale': 1.15, 'wind_speed': 39.0, 'flood_depth': 0.0}, {'seismic_scale': 1.15, 'wind_speed': 39.0, 'flood_depth': 0.5}, {'seismic_scale': 1.15, 'wind_speed': 39.0, 'flood_depth': 1.0}, {'seismic_scale': 1.15, 'wind_speed': 39.0, 'flood_depth': 1.5}, {'seismic_scale': 1.15, 'wind_speed': 39.0, 'flood_depth': 2.5}, {'seismic_scale': 1.15, 'wind_speed': 44.0, 'flood_depth': 0.0}, {'seismic_scale': 1.15, 'wind_speed': 44.0, 'flood_depth': 0.5}, {'seismic_scale': 1.15, 'wind_speed': 44.0, 'flood_depth': 1.0}, {'seismic_scale': 1.15, 'wind_speed': 44.0, 'flood_depth': 1.5}, {'seismic_scale': 1.15, 'wind_speed': 44.0, 'flood_depth': 2.5}, {'seismic_scale': 1.15, 'wind_speed': 47.0, 'flood_depth': 0.0}, {'seismic_scale': 1.15, 'wind_speed': 47.0, 'flood_depth': 0.5}, {'seismic_scale': 1.15, 'wind_speed': 47.0, 'flood_depth': 1.0}, {'seismic_scale': 1.15, 'wind_speed': 47.0, 'flood_depth': 1.5}, {'seismic_scale': 1.15, 'wind_speed': 47.0, 'flood_depth': 2.5}, {'seismic_scale': 1.15, 'wind_speed': 55.0, 'flood_depth': 0.0}, {'seismic_scale': 1.15, 'wind_speed': 55.0, 'flood_depth': 0.5}, {'seismic_scale': 1.15, 'wind_speed': 55.0, 'flood_depth': 1.0}, {'seismic_scale': 1.15, 'wind_speed': 55.0, 'flood_depth': 1.5}, {'seismic_scale': 1.15, 'wind_speed': 55.0, 'flood_depth': 2.5}, {'seismic_scale': 1.3, 'wind_speed': 39.0, 'flood_depth': 0.0}, {'seismic_scale': 1.3, 'wind_speed': 39.0, 'flood_depth': 0.5}, {'seismic_scale': 1.3, 'wind_speed': 39.0, 'flood_depth': 1.0}, {'seismic_scale': 1.3, 'wind_speed': 39.0, 'flood_depth': 1.5}, {'seismic_scale': 1.3, 'wind_speed': 39.0, 'flood_depth': 2.5}, {'seismic_scale': 1.3, 'wind_speed': 44.0, 'flood_depth': 0.0}, {'seismic_scale': 1.3, 'wind_speed': 44.0, 'flood_depth': 0.5}, {'seismic_scale': 1.3, 'wind_speed': 44.0, 'flood_depth': 1.0}, {'seismic_scale': 1.3, 'wind_speed': 44.0, 'flood_depth': 1.5}, {'seismic_scale': 1.3, 'wind_speed': 44.0, 'flood_depth': 2.5}, {'seismic_scale': 1.3, 'wind_speed': 47.0, 'flood_depth': 0.0}, {'seismic_scale': 1.3, 'wind_speed': 47.0, 'flood_depth': 0.5}, {'seismic_scale': 1.3, 'wind_speed': 47.0, 'flood_depth': 1.0}, {'seismic_scale': 1.3, 'wind_speed': 47.0, 'flood_depth': 1.5}, {'seismic_scale': 1.3, 'wind_speed': 47.0, 'flood_depth': 2.5}, {'seismic_scale': 1.3, 'wind_speed': 55.0, 'flood_depth': 0.0}, {'seismic_scale': 1.3, 'wind_speed': 55.0, 'flood_depth': 0.5}, {'seismic_scale': 1.3, 'wind_speed': 55.0, 'flood_depth': 1.0}, {'seismic_scale': 1.3, 'wind_speed': 55.0, 'flood_depth': 1.5}, {'seismic_scale': 1.3, 'wind_speed': 55.0, 'flood_depth': 2.5}, {'seismic_scale': 1.45, 'wind_speed': 39.0, 'flood_depth': 0.0}, {'seismic_scale': 1.45, 'wind_speed': 39.0, 'flood_depth': 0.5}, {'seismic_scale': 1.45, 'wind_speed': 39.0, 'flood_depth': 1.0}, {'seismic_scale': 1.45, 'wind_speed': 39.0, 'flood_depth': 1.5}, {'seismic_scale': 1.45, 'wind_speed': 39.0, 'flood_depth': 2.5}, {'seismic_scale': 1.45, 'wind_speed': 44.0, 'flood_depth': 0.0}, {'seismic_scale': 1.45, 'wind_speed': 44.0, 'flood_depth': 0.5}, {'seismic_scale': 1.45, 'wind_speed': 44.0, 'flood_depth': 1.0}, {'seismic_scale': 1.45, 'wind_speed': 44.0, 'flood_depth': 1.5}, {'seismic_scale': 1.45, 'wind_speed': 44.0, 'flood_depth': 2.5}, {'seismic_scale': 1.45, 'wind_speed': 47.0, 'flood_depth': 0.0}, {'seismic_scale': 1.45, 'wind_speed': 47.0, 'flood_depth': 0.5}, {'seismic_scale': 1.45, 'wind_speed': 47.0, 'flood_depth': 1.0}, {'seismic_scale': 1.45, 'wind_speed': 47.0, 'flood_depth': 1.5}, {'seismic_scale': 1.45, 'wind_speed': 47.0, 'flood_depth': 2.5}, {'seismic_scale': 1.45, 'wind_speed': 55.0, 'flood_depth': 0.0}, {'seismic_scale': 1.45, 'wind_speed': 55.0, 'flood_depth': 0.5}, {'seismic_scale': 1.45, 'wind_speed': 55.0, 'flood_depth': 1.0}, {'seismic_scale': 1.45, 'wind_speed': 55.0, 'flood_depth': 1.5}, {'seismic_scale': 1.45, 'wind_speed': 55.0, 'flood_depth': 2.5}]
    total_W_bldg_kN = sum(story_masses_bldg) * 9.81 / 1000.0
    denom_modal = sum([m * ((s+1) * h_storey)**2 for s, m in enumerate(story_masses_bldg)])

    ops.system('BandGeneral')
    ops.numberer('Plain')
    ops.constraints('Plain')
    ops.integrator('LoadControl', 1.0)
    ops.algorithm('Linear')
    ops.analysis('Static')

    results = []
    case_idx = 1
    for hz in hazards:
        seismic_scale = hz["seismic_scale"]
        wind_speed = hz["wind_speed"]
        flood_depth = hz["flood_depth"]

        sa_g = min(2.5, 1.67 / T1) if soil == "Type III" else min(2.5, 1.36 / T1)
        Ah = (0.24 / 2.0) * (1.2 / 5.0) * sa_g
        Ah = max(Ah, 0.035) * seismic_scale
        Vb_eq_kN = Ah * total_W_bldg_kN

        pz_kN_m2 = 0.6 * (wind_speed**2) / 1000.0
        F_wind_total_kN = pz_kN_m2 * 24.0 * total_h * 1.2
        F_flood_total_kN = 0.5 * 10.0 * (flood_depth**2) * 24.0 if flood_depth > 0 else 0.0

        F_lateral_bldg_kN = Vb_eq_kN + 0.50 * F_wind_total_kN + 0.30 * F_flood_total_kN

        ops.reset()
        ops.timeSeries('Linear', 1)
        ops.pattern('Plain', 1, 1)

        for s in range(storeys):
            hi = (s + 1) * h_storey
            mi = story_masses_bldg[s]
            F_s_bldg = (F_lateral_bldg_kN * mi * (hi**2)) / denom_modal
            F_node = (F_s_bldg / num_frames) / num_col_lines
            for n in story_nodes[s]:
                ops.load(n, F_node * 1000.0, 0.0, 0.0)

        ops.analyze(1)

        disp_roof_m = ops.nodeDisp(story_nodes[-1][2], 1)
        roof_sway_mm = disp_roof_m * 1000.0

        max_drift_pct = 0.0
        for s in range(storeys):
            u_top = ops.nodeDisp(story_nodes[s][2], 1)
            u_bot = 0.0 if s == 0 else ops.nodeDisp(story_nodes[s-1][2], 1)
            drift_s = (u_top - u_bot) / h_storey * 100.0
            if drift_s > max_drift_pct:
                max_drift_pct = drift_s

        ops.reactions()
        total_rxn_N = 0.0
        total_moment_Nm = 0.0
        for i in range(num_col_lines):
            base_n = i + 1
            total_rxn_N += abs(ops.nodeReaction(base_n, 1))
            total_moment_Nm += abs(ops.nodeReaction(base_n, 3)) + abs(ops.nodeReaction(base_n, 2)) * (i * bay_w)

        Vb_final_kN = (total_rxn_N * num_frames) / 1000.0
        Mz_final_kNm = (total_moment_Nm * num_frames) / 1000.0

        ops.remove('loadPattern', 1)
        ops.remove('timeSeries', 1)

        status = "COMPLIANT" if max_drift_pct <= 0.400 else "EXCEEDED"
        results.append([
            case_idx, model_id, storeys, total_h, int(slab_t*1000), int(fck), soil,
            f"{(2.0*wall_t*6.0/floor_area)*100:.3f}", f"{(20*col_w*col_w/floor_area)*100:.3f}",
            int(wall_t*1000), int(col_w*1000), setback,
            seismic_scale, wind_speed, flood_depth,
            f"{T1:.4f}", f"{Vb_final_kN:.2f}", f"{Mz_final_kNm:.2f}",
            f"{max_drift_pct:.5f}", f"{roof_sway_mm:.2f}", status
        ])
        case_idx += 1

    with open(results_file, "w", newline="") as rf:
        writer = csv.writer(rf)
        writer.writerow([
            "Case_ID", "Model_ID", "Storeys", "Height_m", "Slab_Thickness_mm", "Fck_MPa", "Soil_Type",
            "Shear_Wall_Ratio_pct", "Column_Ratio_pct", "Shear_Wall_Thick_mm", "Column_Dim_mm", "Setback_pct",
            "Seismic_Scale", "Wind_Speed_ms", "Flood_Depth_m", "Fundamental_Period_T1_s",
            "Base_Shear_Vb_kN", "Base_Moment_Mz_kNm", "Inter_Storey_Drift_pct", "Roof_Sway_mm", "Compliance_Status"
        ])
        writer.writerows(results)

if __name__ == "__main__":
    run_simulation()
