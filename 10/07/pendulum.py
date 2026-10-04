#!/usr/bin/env python3
# Copyright (C) 2021. Huawei Technologies Co., Ltd. All rights reserved.
# Adapted from the pendulum-generation idea supplied by the user. MIT License.
"""Physical pendulum videos + per-frame time-series labels.

Install: python -m pip install numpy pillow imageio imageio-ffmpeg
Demo:    python simulate_pendulum_videos.py --demo-set --output pendulum_videos --zip
Batch:   python simulate_pendulum_videos.py --randomize --num-videos 20 --output videos_20
Single:  python simulate_pendulum_videos.py --theta0 40 --damping 0.12 --output one_video

Nonlinear ODE: theta'' + damping*theta' + (gravity/length)*sin(theta) = 0.
RK4 integrates at fps * substeps Hz. A changing light affects the shadow,
not the pendulum dynamics. Training videos are clean, without captions.
"""

import argparse
import csv
import json
import math
import shutil
import zipfile
from dataclasses import asdict, dataclass, replace
from pathlib import Path

import imageio.v2 as imageio
import numpy as np
from PIL import Image, ImageDraw, ImageFont

PIVOT = (10.0, 10.5)
DRAW_LENGTH = 8.0  # visual world units; physical length is separately in meters
BOB_RADIUS = 1.5
GROUND_Y, SUN_Y, SUN_RADIUS = -0.5, 20.5, 3.0
WORLD = (-5.0, 25.0, -3.0, 27.0)


@dataclass
class Configuration:
    name: str = "pendulum"
    theta0_deg: float = 35.0
    omega0_rad_s: float = 0.0
    damping_s_inv: float = 0.12
    light_mean_deg: float = 65.0
    light_amplitude_deg: float = 0.0
    light_frequency_hz: float = 0.08
    light_phase_rad: float = -math.pi / 2


def angular_acceleration(theta, omega, gravity, length, damping):
    return -(gravity / length) * math.sin(theta) - damping * omega


def rk4_step(theta, omega, dt, gravity, length, damping):
    """One fourth-order Runge-Kutta step for the nonlinear pendulum."""
    def f(a, b):
        return b, angular_acceleration(a, b, gravity, length, damping)
    k1 = f(theta, omega)
    k2 = f(theta + dt*k1[0]/2, omega + dt*k1[1]/2)
    k3 = f(theta + dt*k2[0]/2, omega + dt*k2[1]/2)
    k4 = f(theta + dt*k3[0], omega + dt*k3[1])
    return (theta + dt*(k1[0]+2*k2[0]+2*k3[0]+k4[0])/6,
            omega + dt*(k1[1]+2*k2[1]+2*k3[1]+k4[1])/6)


def scene_geometry(theta, light_deg):
    phi = math.radians(light_deg)
    cot = math.cos(phi) / math.sin(phi)
    x = PIVOT[0] + DRAW_LENGTH * math.sin(theta)
    y = PIVOT[1] - DRAW_LENGTH * math.cos(theta)
    pivot_shadow = PIVOT[0] + (GROUND_Y - PIVOT[1]) * cot
    bob_shadow = x + (GROUND_Y - y) * cot
    half_width = BOB_RADIUS / abs(math.sin(phi))
    left = min(pivot_shadow, bob_shadow - half_width)
    right = max(pivot_shadow, bob_shadow + half_width)
    return {
        "bob_x_world": x, "bob_y_world": y,
        "light_x_world": PIVOT[0] + (SUN_Y - PIVOT[1]) * cot,
        "shadow_left_world": left, "shadow_right_world": right,
        "shade": right - left, "mid": (left + right) / 2,
    }


def simulate(config, frames, fps, substeps, gravity, length):
    theta, omega = math.radians(config.theta0_deg), config.omega0_rad_s
    dt = 1.0 / (fps * substeps)
    rows = []
    for frame in range(frames):
        t = frame / fps
        light = config.light_mean_deg + config.light_amplitude_deg * math.sin(
            2*math.pi*config.light_frequency_hz*t + config.light_phase_rad)
        row = {
            "frame": frame, "time_s": t,
            "theta_rad": theta, "theta_deg": math.degrees(theta),
            "omega_rad_s": omega,
            "alpha_rad_s2": angular_acceleration(theta, omega, gravity, length,
                                                config.damping_s_inv),
            "light_angle_deg": light,
            "bob_x_m": length * math.sin(theta),
            "bob_y_m": -length * math.cos(theta),
            "energy_j_per_kg": 0.5*length**2*omega**2 + gravity*length*(1-math.cos(theta)),
        }
        row.update(scene_geometry(theta, light))
        rows.append(row)
        if frame < frames - 1:
            for _ in range(substeps):
                theta, omega = rk4_step(theta, omega, dt, gravity, length,
                                        config.damping_s_inv)
    return rows


def validate_scene(row):
    xmin, xmax, ymin, ymax = WORLD
    return (xmin < row["shadow_left_world"] < row["shadow_right_world"] < xmax
            and xmin <= row["bob_x_world"]-BOB_RADIUS
            and row["bob_x_world"]+BOB_RADIUS <= xmax
            and ymin <= row["bob_y_world"]-BOB_RADIUS
            and row["bob_y_world"]+BOB_RADIUS <= ymax
            and xmin <= row["light_x_world"]-SUN_RADIUS
            and row["light_x_world"]+SUN_RADIUS <= xmax)


def render_scene(row, size, supersample=3):
    high = size * supersample
    image = Image.new("RGB", (high, high), "white")
    draw = ImageDraw.Draw(image)
    xmin, xmax, ymin, ymax = WORLD
    scale = (high - 1) / (xmax - xmin)
    def point(x, y):
        return (scale*(x-xmin), scale*(ymax-y))
    def circle(x, y, radius, fill):
        draw.ellipse([point(x-radius, y+radius), point(x+radius, y-radius)], fill=fill)
    circle(row["light_x_world"], SUN_Y, SUN_RADIUS, "#ffa500")
    draw.line([point(xmin, GROUND_Y), point(xmax, GROUND_Y)],
              fill="#cbd5e1", width=max(1, round(0.08*scale)))
    draw.rectangle([point(row["shadow_left_world"], GROUND_Y+0.14),
                    point(row["shadow_right_world"], GROUND_Y-0.14)], fill="#171717")
    draw.line([point(*PIVOT), point(row["bob_x_world"], row["bob_y_world"])],
              fill="#171717", width=max(1, round(0.30*scale)))
    circle(*PIVOT, 0.18, "#171717")
    circle(row["bob_x_world"], row["bob_y_world"], BOB_RADIUS, "#b22222")
    return image.resize((size, size), Image.Resampling.LANCZOS)


def video_writer(path, fps):
    # imageio-ffmpeg supplies an encoder; no separate system FFmpeg is required.
    return imageio.get_writer(str(path), fps=fps, codec="libx264", quality=8,
                             pixelformat="yuv420p", macro_block_size=1,
                             ffmpeg_log_level="error", ffmpeg_params=["-movflags", "+faststart"])


def write_csv(path, rows):
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def load_font(size, bold=False):
    try:
        return ImageFont.truetype("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf", size)
    except OSError:
        try:
            return ImageFont.load_default(size=size)
        except TypeError:
            return ImageFont.load_default()


def make_demo_preview(output, configs, series, fps, duration, substeps):
    """Annotated comparison movie. Clean dataset clips are saved separately."""
    fonts = {n: load_font(n) for n in (11, 12, 13, 14, 15, 16, 22)}
    title_font, card_font = load_font(32, True), load_font(17, True)
    colors = ("#b22a3c", "#287d90", "#8051ad")
    pale = ("#ecd0d5", "#c8e0e5", "#ddd1ed")
    names = ("Undamped / fixed light", "Damped / fixed light", "Damped / moving light")
    base = Image.new("RGB", (1280, 800), "#f3f5f8")
    d = ImageDraw.Draw(base)
    d.text((40, 24), "PENDULUM / TIME-SERIES SIMULATION", font=fonts[13], fill="#536176")
    d.text((40, 49), "A pendulum, now in time.", font=title_font, fill="#152238")
    d.text((40, 96), f"{duration:g} seconds  ·  {fps} fps  ·  nonlinear dynamics  ·  "
           f"RK4 integration at {fps*substeps} Hz", font=fonts[16], fill="#536176")
    for k, (name, color) in enumerate(zip(names, colors)):
        x = 40 + k*410
        d.rounded_rectangle((x, 135, x+380, 566), radius=12, fill="white", outline="#dbe1e8")
        d.ellipse((x+16, 150, x+26, 160), fill=color)
        d.text((x+34, 144), name, font=card_font, fill="#152238")
        d.text((x+16, 176), f"Damping γ = {configs[k].damping_s_inv:.2f} s⁻¹",
               font=fonts[14], fill="#536176")
    d.text((40, 587), "PENDULUM ANGLE (degrees)", font=fonts[13], fill="#536176")
    d.text((740, 587), "Faint line: full trajectory  ·  dark line: elapsed time",
           font=fonts[12], fill="#536176")
    x0, x1, y0, y1 = 76, 1240, 617, 739
    angle_limit = max(10, 5*math.ceil(max(abs(r["theta_deg"]) for s in series for r in s)/5))
    def chart_point(row):
        return (x0+(x1-x0)*row["time_s"]/duration,
                (y0+y1)/2-(y1-y0)*row["theta_deg"]/(2*angle_limit))
    for angle in (-angle_limit, 0, angle_limit):
        y = (y0+y1)/2-(y1-y0)*angle/(2*angle_limit)
        d.line((x0, y, x1, y), fill="#dbe1e8", width=1)
        d.text((40, y-7), f"{angle:+g}°", font=fonts[11], fill="#536176")
    for tick in np.linspace(0, duration, 5):
        x = x0+(x1-x0)*tick/duration
        d.text((x-9, 748), f"{tick:g}s", font=fonts[11], fill="#536176")
    chart_points = [[chart_point(r) for r in s] for s in series]
    # The last two mechanical trajectories coincide exactly. Use nested stroke
    # widths (not displaced coordinates) to show both colors at the same values.
    for k, (points, color) in enumerate(zip(chart_points, pale)):
        d.line(points, fill=color, width=4 if k == 1 else 2)
    d.text((40, 778), "Light changes the shadow, not the mechanics. Clean MP4s + per-frame CSVs are included.",
           font=fonts[12], fill="#536176")
    with video_writer(output / "preview.mp4", fps) as writer:
        for frame in range(len(series[0])):
            canvas = base.copy()
            draw = ImageDraw.Draw(canvas)
            draw.rounded_rectangle((1084, 49, 1240, 92), radius=10, fill="white")
            draw.text((1101, 58), f"t = {frame/fps:05.2f} s", font=fonts[22], fill="#152238")
            for k, (rows, color) in enumerate(zip(series, colors)):
                row, x = rows[frame], 40+k*410
                canvas.paste(render_scene(row, 304), (x+38, 205))
                draw.text((x+16, 517), f"θ {row['theta_deg']:+.1f}°    "
                          f"ω {row['omega_rad_s']:+.2f} rad/s", font=fonts[14], fill="#152238")
                draw.text((x+16, 541), f"Light {row['light_angle_deg']:.1f}°    "
                          f"Shadow {row['shade']:.2f}", font=fonts[14], fill="#536176")
                if frame:
                    draw.line(chart_points[k][:frame+1], fill=color, width=4 if k == 1 else 2)
                cx, cy = chart_points[k][frame]
                radius = 4 if k == 1 else 2
                draw.ellipse((cx-radius, cy-radius, cx+radius, cy+radius), fill=color)
            cursor_x = x0+(x1-x0)*(frame/fps)/duration
            draw.line((cursor_x, y0, cursor_x, y1), fill="#9aa6b7", width=1)
            writer.append_data(np.asarray(canvas))
            if frame == min(len(series[0])-1, fps*3):
                canvas.save(output / "preview.png")


LICENSE_TEXT = """MIT License

Copyright (C) 2021. Huawei Technologies Co., Ltd. All rights reserved.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the \"Software\"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED \"AS IS\", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

README_TEXT = """# Pendulum video / time-series dataset

Silent H.264 MP4s of a **nonlinear physical pendulum**, with frame-aligned CSVs.

## Physics

`theta'' = -(gravity / length) * sin(theta) - damping * theta'`

`gravity` is in m/s², `length` in meters, `damping` in s⁻¹. Integration uses
fourth-order Runge-Kutta (RK4), with multiple substeps per video frame.
`omega_rad_s` is angular velocity and `alpha_rad_s2` angular acceleration.
`energy_j_per_kg` is mechanical energy per unit mass relative to the lowest
position. It is conserved for zero damping, and decays when damping is positive.
The integration is numerical, so conservation is approximate.

Illumination is independently controlled:
`light(t) = mean + amplitude * sin(2*pi*frequency*t + phase)`.
The orange disk marks **parallel-ray light**, not a finite-distance emitter.
The shadow is the exact ground projection of the circular bob and ideal thin
rod, ignoring decorative drawing stroke thickness.

The physical rod length defaults to 1 meter. The drawing uses a fixed length
of 8 **visual world units** so it resembles the earlier image dataset.
`bob_x_m` / `bob_y_m` are physical coordinates relative to the pivot;
`bob_x_world` / `bob_y_world`, `shade`, and `mid` are drawing-world coordinates.
Do not interpret shadow labels as meters.

## Files

- `videos/train/`, `videos/test/`: clean, caption-free MP4s.
- `timeseries/clip_XXXX.csv`: one label row per decoded video frame.
- `index.csv`: video-level paths, splits, configuration, and physical parameters.
- `metadata.json`: timing, model, renderer, and generation settings.
- `preview.mp4`, `preview.png`: annotated three-condition comparison (demo set only).
- `frames/clip_XXXX/`: optional PNGs, enabled with `--save-frames`.

Frame `n` corresponds to CSV row `frame=n`, at `time_s=n/fps`.
For duration 12 seconds and 30 fps there are 360 frames; the last sampled
instant is 11.9666667 seconds. The encoded movie still lasts exactly 12 seconds.
Non-integral duration*fps is rounded; metadata records the actual duration.
All splits are **whole-video splits**, never adjacent-frame splits.

## Examples

```bash
python -m pip install numpy pillow imageio imageio-ffmpeg

# Three comparison clips: undamped, damped, and damped with moving light.
python simulate_pendulum_videos.py --demo-set --output pendulum_demo --zip

# A reproducible dataset with varied initial states, damping, and lighting.
python simulate_pendulum_videos.py --randomize --num-videos 50 \\
  --duration 10 --fps 30 --size 256 --seed 42 --output pendulum_50 --zip

# One custom physical trajectory; optionally also export PNG frames.
python simulate_pendulum_videos.py --theta0 40 --omega0 0 --damping 0.15 \\
  --length 1 --light-angle 90 --light-amplitude 20 --light-frequency 0.08 \\
  --duration 12 --fps 30 --save-frames --output my_pendulum
```

Choose a new or empty output folder. `imageio-ffmpeg` supplies FFmpeg, so a
separate system installation is not necessary. The script has no dependency
on the earlier image generator. All videos are silent.

The three demo profiles are illustrative, not a representative ML benchmark.
The second and third profiles intentionally share the exact same pendulum
trajectory, with different illumination. Their graph traces coincide; nested
stroke widths show both colors without changing any plotted values. For
training, use `--randomize` and many videos. Randomized ranges are initial angle ±15–40°,
initial angular velocity ±0.2 rad/s, damping 0–0.35 s⁻¹, light mean 70–110°,
light amplitude 0–15°, and light frequency 0.04–0.12 Hz. Physical gravity and
length remain the user-selected values for the entire batch.

CSVs preserve raw quantities rather than fitting normalization across splits.
Original supplied code's copyright notice is preserved; see LICENSE.
"""


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--output", type=Path, default=Path("pendulum_videos"))
    p.add_argument("--demo-set", action="store_true", help="three profiles and an annotated comparison video")
    p.add_argument("--num-videos", type=int, default=1)
    p.add_argument("--randomize", action="store_true", help="sample distinct initial conditions and lighting")
    p.add_argument("--duration", type=float, default=12.0)
    p.add_argument("--fps", type=int, default=30)
    p.add_argument("--size", type=int, default=256)
    p.add_argument("--substeps", type=int, default=8)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--test-fraction", type=float, default=0.20)
    p.add_argument("--theta0", type=float, default=35.0, help="initial angle in degrees")
    p.add_argument("--omega0", type=float, default=0.0, help="initial angular velocity in rad/s")
    p.add_argument("--damping", type=float, default=0.12, help="linear damping coefficient in 1/s")
    p.add_argument("--gravity", type=float, default=9.81)
    p.add_argument("--length", type=float, default=1.0, help="physical length in meters")
    p.add_argument("--light-angle", type=float, default=65.0)
    p.add_argument("--light-amplitude", type=float, default=0.0)
    p.add_argument("--light-frequency", type=float, default=0.08)
    p.add_argument("--light-phase", type=float, default=-90.0, help="light phase in degrees")
    p.add_argument("--save-frames", action="store_true")
    p.add_argument("--zip", action="store_true")
    a = p.parse_args()
    floats = (a.duration, a.test_fraction, a.theta0, a.omega0, a.damping, a.gravity,
              a.length, a.light_angle, a.light_amplitude, a.light_frequency, a.light_phase)
    if not all(math.isfinite(x) for x in floats):
        p.error("numeric parameters must be finite")
    if a.fps < 1 or a.substeps < 1 or a.duration <= 0 or a.duration*a.fps < 2:
        p.error("positive timing parameters and at least two frames are required")
    if a.size < 64 or a.size % 2:
        p.error("--size must be even and at least 64 for H.264 video")
    if a.length <= 0 or a.gravity <= 0 or a.damping < 0 or a.light_amplitude < 0:
        p.error("length/gravity must be positive; damping/light amplitude must be nonnegative")
    if a.light_frequency < 0 or a.seed < 0 or a.num_videos < 1 or not 0 < a.test_fraction < 1:
        p.error("invalid frequency, seed, number of videos, or test fraction")
    if a.demo_set and a.randomize:
        p.error("choose either --demo-set or --randomize")
    if a.num_videos != 1 and a.demo_set:
        p.error("--demo-set creates exactly three videos; omit --num-videos")
    if a.num_videos > 1 and not (a.randomize or a.demo_set):
        p.error("use --randomize for multiple videos, to avoid identical sequences")
    output = a.output.resolve()
    archive = output.with_suffix(".zip")
    if output.exists() and (not output.is_dir() or any(output.iterdir())):
        p.error("output folder must be new or empty")
    if a.zip and archive.exists():
        p.error(f"archive already exists: {archive}")

    rng = np.random.default_rng(a.seed)
    base = Configuration(theta0_deg=a.theta0, omega0_rad_s=a.omega0, damping_s_inv=a.damping,
                         light_mean_deg=a.light_angle, light_amplitude_deg=a.light_amplitude,
                         light_frequency_hz=a.light_frequency, light_phase_rad=math.radians(a.light_phase))
    if a.demo_set:
        initial = {"theta0_deg": a.theta0, "omega0_rad_s": a.omega0}
        configs = [Configuration(name="undamped", damping_s_inv=0, **initial),
                   Configuration(name="damped", damping_s_inv=0.28, **initial),
                   Configuration(name="moving_light", damping_s_inv=0.28,
                                 light_mean_deg=90, light_amplitude_deg=25, **initial)]
    elif a.randomize:
        configs = [replace(base, name=f"random_{i:04d}",
                   theta0_deg=float(rng.choice([-1, 1])*rng.uniform(15, 40)),
                   omega0_rad_s=float(rng.uniform(-0.2, 0.2)),
                   damping_s_inv=float(rng.uniform(0, 0.35)),
                   light_mean_deg=float(rng.uniform(70, 110)),
                   light_amplitude_deg=float(rng.uniform(0, 15)),
                   light_frequency_hz=float(rng.uniform(0.04, 0.12)),
                   light_phase_rad=float(rng.uniform(0, 2*math.pi))) for i in range(a.num_videos)]
    else:
        configs = [base]
    if any(not (45 <= c.light_mean_deg-c.light_amplitude_deg
                <= c.light_mean_deg+c.light_amplitude_deg <= 135) for c in configs):
        p.error("light angle ± amplitude must stay within [45, 135] degrees")
    frames = round(a.duration * a.fps)
    duration = frames / a.fps
    series = [simulate(c, frames, a.fps, a.substeps, a.gravity, a.length) for c in configs]
    if not all(math.isfinite(v) for rows in series for r in rows for v in r.values()):
        p.error("unstable integration; increase --substeps or use less extreme parameters")
    if not all(validate_scene(r) for rows in series for r in rows):
        p.error("scene would be clipped; use less extreme initial conditions/light angles or edit WORLD")

    ntest = 0 if len(configs) == 1 else min(len(configs)-1, max(1, round(len(configs)*a.test_fraction)))
    test_indices = set(rng.permutation(len(configs))[:ntest].tolist())
    for folder in ("videos/train", "videos/test", "timeseries"):
        (output / folder).mkdir(parents=True, exist_ok=True)
    index = []
    for i, (config, rows) in enumerate(zip(configs, series)):
        video_id = f"clip_{i:04d}"
        split = "test" if i in test_indices else "train"
        video_path = f"videos/{split}/{video_id}.mp4"
        csv_path = f"timeseries/{video_id}.csv"
        frame_folder = output / "frames" / video_id
        if a.save_frames:
            frame_folder.mkdir(parents=True)
        with video_writer(output / video_path, a.fps) as writer:
            for row in rows:
                image = render_scene(row, a.size)
                writer.append_data(np.asarray(image))
                if a.save_frames:
                    image.save(frame_folder / f"{row['frame']:06d}.png")
        write_csv(output / csv_path, rows)
        index.append({"video_id": video_id, "split": split, "video_path": video_path,
                      "csv_path": csv_path, "frames": frames, "duration_s": duration,
                      "fps": a.fps, "size_px": a.size, "gravity_m_s2": a.gravity,
                      "length_m": a.length, **asdict(config)})
        print(f"Saved {video_id}: {config.name}, {frames} frames, {split}", flush=True)
    write_csv(output / "index.csv", index)
    metadata = {
        "dataset": "physical_pendulum_videos", "seed": a.seed,
        "generation_mode": "demo" if a.demo_set else "random" if a.randomize else "single",
        "num_videos": len(configs), "train_videos": len(configs)-ntest, "test_videos": ntest,
        "requested_duration_s": a.duration, "duration_s": duration,
        "fps": a.fps, "frames_per_video": frames, "image_size": [a.size, a.size],
        "codec": "H.264", "pixel_format": "yuv420p", "audio": False,
        "ode": "theta_ddot = -(gravity/length)*sin(theta) - damping*theta_dot",
        "integrator": "RK4", "substeps_per_frame": a.substeps,
        "integration_dt_s": 1/(a.fps*a.substeps),
        "gravity_m_s2": a.gravity, "length_m": a.length,
        "renderer_world": {"viewport": WORLD, "pivot": PIVOT, "rod_length": DRAW_LENGTH,
                           "bob_radius": BOB_RADIUS, "ground_y": GROUND_Y},
        "timing": "CSV row n and decoded MP4 frame n both sample time n/fps",
        "split_unit": "whole video", "paths_relative_to": "dataset root",
        "normalized_labels": False,
    }
    (output / "metadata.json").write_text(json.dumps(metadata, indent=2)+"\n", encoding="utf-8")
    (output / "README.md").write_text(README_TEXT, encoding="utf-8")
    (output / "LICENSE").write_text(LICENSE_TEXT, encoding="utf-8")
    shutil.copyfile(__file__, output / "simulate_pendulum_videos.py")
    if a.demo_set:
        print("Rendering comparison preview...", flush=True)
        make_demo_preview(output, configs, series, a.fps, duration, a.substeps)
    if a.zip:
        with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as z:
            for path in sorted(output.rglob("*")):
                if path.is_file():
                    z.write(path, path.relative_to(output.parent))
        print(f"Archive: {archive}")
    print(f"Done: {output}")


if __name__ == "__main__":
    main()