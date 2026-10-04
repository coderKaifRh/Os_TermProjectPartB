import math
from typing import List, Dict, Tuple

def generate_timeline_svg(series_dict: Dict[str, List[float]],
                          shift_point: int,
                          output_path: str,
                          width: int = 800,
                          height: int = 420):
    margin_left = 60
    margin_right = 30
    margin_top = 40
    margin_bottom = 50
    plot_w = width - margin_left - margin_right
    plot_h = height - margin_top - margin_bottom

    colors = {
        "Optimal (Belady)": "#2b8a3e",
        "Learned (Decision Tree)": "#1c7ed6",
        "LRU": "#f59f00",
        "FIFO": "#e03131"
    }

    max_x = max(len(s) for s in series_dict.values())
    max_y = 100.0
    min_y = 0.0

    def to_screen(x, y):
        sx = margin_left + (x / max(1, max_x)) * plot_w
        sy = margin_top + plot_h - ((y - min_y) / (max_y - min_y)) * plot_h
        return sx, sy

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" style="background-color:#ffffff; font-family:sans-serif;">',
        f'<rect width="{width}" height="{height}" fill="#ffffff" />',
        f'<text x="{width/2}" y="24" text-anchor="middle" font-size="16" font-weight="bold" fill="#212529">Cumulative Hit Ratio Over Time (With Workload Shift)</text>'
    ]

    for y_val in [0, 20, 40, 60, 80, 100]:
        _, sy = to_screen(0, y_val)
        svg.append(f'<line x1="{margin_left}" y1="{sy}" x2="{width - margin_right}" y2="{sy}" stroke="#e9ecef" stroke-width="1" />')
        svg.append(f'<text x="{margin_left - 10}" y="{sy + 4}" text-anchor="end" font-size="11" fill="#495057">{y_val}%</text>')

    shift_x, _ = to_screen(shift_point, 0)
    svg.append(f'<line x1="{shift_x}" y1="{margin_top}" x2="{shift_x}" y2="{height - margin_bottom}" stroke="#868e96" stroke-width="2" stroke-dasharray="6,4" />')
    svg.append(f'<text x="{shift_x + 6}" y="{margin_top + 16}" font-size="11" font-weight="bold" fill="#e03131">WORKLOAD SHIFT (t={shift_point})</text>')
    svg.append(f'<text x="{shift_x - 10}" y="{height - margin_bottom - 10}" text-anchor="end" font-size="11" fill="#495057">Phase 1: Locality-Heavy</text>')
    svg.append(f'<text x="{shift_x + 10}" y="{height - margin_bottom - 10}" text-anchor="start" font-size="11" fill="#495057">Phase 2: Random / Bursty Scan</text>')

    svg.append(f'<line x1="{margin_left}" y1="{height - margin_bottom}" x2="{width - margin_right}" y2="{height - margin_bottom}" stroke="#495057" stroke-width="1.5" />')
    svg.append(f'<line x1="{margin_left}" y1="{margin_top}" x2="{margin_left}" y2="{height - margin_bottom}" stroke="#495057" stroke-width="1.5" />')
    svg.append(f'<text x="{width/2}" y="{height - 12}" text-anchor="middle" font-size="12" fill="#495057">Memory Access Sequence (Timestep t)</text>')

    step_sample = max(1, max_x // 400)
    for name, series in series_dict.items():
        color = colors.get(name, "#333333")
        points = []
        for x in range(0, len(series), step_sample):
            sx, sy = to_screen(x, series[x])
            points.append(f"{sx:.1f},{sy:.1f}")
        sx, sy = to_screen(len(series) - 1, series[-1])
        points.append(f"{sx:.1f},{sy:.1f}")
        svg.append(f'<polyline points="{" ".join(points)}" fill="none" stroke="{color}" stroke-width="2.5" />')

    leg_x = margin_left + 20
    leg_y = margin_top + 30
    for idx, (name, col) in enumerate(colors.items()):
        cur_y = leg_y + idx * 20
        svg.append(f'<line x1="{leg_x}" y1="{cur_y}" x2="{leg_x + 22}" y2="{cur_y}" stroke="{col}" stroke-width="3" />')
        svg.append(f'<text x="{leg_x + 28}" y="{cur_y + 4}" font-size="11" font-weight="bold" fill="#343a40">{name}</text>')

    svg.append('</svg>')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(svg))

def generate_bar_chart_svg(data: Dict[str, Dict[str, float]],
                           output_path: str,
                           metric_title: str,
                           y_label: str,
                           width: int = 700,
                           height: int = 380):
    margin_left = 65
    margin_right = 30
    margin_top = 45
    margin_bottom = 60
    plot_w = width - margin_left - margin_right
    plot_h = height - margin_top - margin_bottom

    categories = list(data.keys())
    series_names = ["Pre-Shift", "Post-Shift", "Overall"]
    series_colors = ["#4dabf7", "#ff8787", "#38d9a9"]

    max_val = 0.0
    for alg, s_dict in data.items():
        for s_name in series_names:
            max_val = max(max_val, s_dict.get(s_name, 0.0))
    max_y = math.ceil(max_val * 1.15) if max_val > 0 else 100

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" style="background-color:#ffffff; font-family:sans-serif;">',
        f'<rect width="{width}" height="{height}" fill="#ffffff" />',
        f'<text x="{width/2}" y="24" text-anchor="middle" font-size="16" font-weight="bold" fill="#212529">{metric_title}</text>'
    ]

    for i in range(6):
        val = (max_y / 5.0) * i
        sy = margin_top + plot_h - (val / max_y) * plot_h
        svg.append(f'<line x1="{margin_left}" y1="{sy}" x2="{width - margin_right}" y2="{sy}" stroke="#e9ecef" stroke-width="1" />')
        svg.append(f'<text x="{margin_left - 8}" y="{sy + 4}" text-anchor="end" font-size="11" fill="#495057">{val:.0f}</text>')

    group_width = plot_w / len(categories)
    bar_width = group_width * 0.22
    spacing = group_width * 0.05

    for g_idx, cat in enumerate(categories):
        cx = margin_left + g_idx * group_width + group_width / 2.0
        start_x = cx - (3 * bar_width + 2 * spacing) / 2.0

        for s_idx, s_name in enumerate(series_names):
            bx = start_x + s_idx * (bar_width + spacing)
            val = data[cat].get(s_name, 0.0)
            bh = (val / max_y) * plot_h
            by = margin_top + plot_h - bh

            col = series_colors[s_idx]
            svg.append(f'<rect x="{bx:.1f}" y="{by:.1f}" width="{bar_width:.1f}" height="{bh:.1f}" rx="2" fill="{col}" />')
            svg.append(f'<text x="{bx + bar_width/2:.1f}" y="{by - 4:.1f}" text-anchor="middle" font-size="10" font-weight="bold" fill="#343a40">{val:.1f}</text>')

        svg.append(f'<text x="{cx:.1f}" y="{height - margin_bottom + 18}" text-anchor="middle" font-size="11" font-weight="bold" fill="#212529">{cat}</text>')

    svg.append(f'<line x1="{margin_left}" y1="{height - margin_bottom}" x2="{width - margin_right}" y2="{height - margin_bottom}" stroke="#495057" stroke-width="1.5" />')
    svg.append(f'<line x1="{margin_left}" y1="{margin_top}" x2="{margin_left}" y2="{height - margin_bottom}" stroke="#495057" stroke-width="1.5" />')
    svg.append(f'<text x="{margin_left - 35}" y="{margin_top - 10}" font-size="11" font-weight="bold" fill="#495057">{y_label}</text>')

    leg_x = width - margin_right - 260
    leg_y = margin_top - 10
    for idx, (s_name, col) in enumerate(zip(series_names, series_colors)):
        cx = leg_x + idx * 90
        svg.append(f'<rect x="{cx}" y="{leg_y}" width="12" height="12" rx="2" fill="{col}" />')
        svg.append(f'<text x="{cx + 16}" y="{leg_y + 10}" font-size="11" fill="#495057">{s_name}</text>')

    svg.append('</svg>')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(svg))

def generate_calibration_svg(calib_data: Dict[str, Dict[str, float]],
                             output_path: str,
                             width: int = 600,
                             height: int = 360):
    margin_left = 60
    margin_right = 30
    margin_top = 45
    margin_bottom = 60
    plot_w = width - margin_left - margin_right
    plot_h = height - margin_top - margin_bottom

    bin_names = list(calib_data.keys())
    accuracies = [calib_data[b]["empirical_accuracy"] for b in bin_names]
    counts = [calib_data[b]["total_decisions"] for b in bin_names]

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" style="background-color:#ffffff; font-family:sans-serif;">',
        f'<rect width="{width}" height="{height}" fill="#ffffff" />',
        f'<text x="{width/2}" y="24" text-anchor="middle" font-size="15" font-weight="bold" fill="#212529">Explanation Confidence Calibration (Bonus Track)</text>'
    ]

    for y_val in [0, 20, 40, 60, 80, 100]:
        sy = margin_top + plot_h - (y_val / 100.0) * plot_h
        svg.append(f'<line x1="{margin_left}" y1="{sy}" x2="{width - margin_right}" y2="{sy}" stroke="#e9ecef" stroke-width="1" />')
        svg.append(f'<text x="{margin_left - 8}" y="{sy + 4}" text-anchor="end" font-size="11" fill="#495057">{y_val}%</text>')

    bar_width = 75.0
    group_w = plot_w / len(bin_names)
    colors = ["#ffd43b", "#74c0fc", "#69db7c"]

    for idx, (b_name, acc, cnt, col) in enumerate(zip(bin_names, accuracies, counts, colors)):
        cx = margin_left + idx * group_w + group_w / 2.0
        bx = cx - bar_width / 2.0
        bh = (acc / 100.0) * plot_h
        by = margin_top + plot_h - bh

        svg.append(f'<rect x="{bx:.1f}" y="{by:.1f}" width="{bar_width}" height="{bh:.1f}" rx="4" fill="{col}" stroke="#343a40" stroke-width="1" />')
        svg.append(f'<text x="{cx:.1f}" y="{by - 6:.1f}" text-anchor="middle" font-size="12" font-weight="bold" fill="#212529">{acc:.1f}%</text>')
        svg.append(f'<text x="{cx:.1f}" y="{by + 16:.1f}" text-anchor="middle" font-size="10" fill="#495057">N={cnt}</text>')

        label_text = b_name.split()[0] + " Conf"
        range_text = b_name[b_name.find('['):]
        svg.append(f'<text x="{cx:.1f}" y="{height - margin_bottom + 18}" text-anchor="middle" font-size="11" font-weight="bold" fill="#212529">{label_text}</text>')
        svg.append(f'<text x="{cx:.1f}" y="{height - margin_bottom + 32}" text-anchor="middle" font-size="10" fill="#868e96">{range_text}</text>')

    svg.append(f'<line x1="{margin_left}" y1="{height - margin_bottom}" x2="{width - margin_right}" y2="{height - margin_bottom}" stroke="#495057" stroke-width="1.5" />')
    svg.append(f'<line x1="{margin_left}" y1="{margin_top}" x2="{margin_left}" y2="{height - margin_bottom}" stroke="#495057" stroke-width="1.5" />')
    svg.append(f'<text x="{margin_left - 45}" y="{margin_top - 10}" font-size="11" font-weight="bold" fill="#495057">Empirical Accuracy (%)</text>')

    svg.append('</svg>')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(svg))
