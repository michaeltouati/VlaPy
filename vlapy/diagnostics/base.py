# MIT License
#
# Copyright (c) 2020 Archis Joglekar
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import os
import time

import mlflow
import numpy as np
from scipy import fft, ifft

from matplotlib import pyplot as plt


def __get_figure_and_plot__():
    this_fig = plt.figure(figsize=(8, 4))
    this_plt = this_fig.add_subplot(111)

    return this_fig, this_plt


def __plot_series__(series_dir, storage_manager):
    for metric, vals in storage_manager.series_dataset.items():
        this_fig, this_plt = __get_figure_and_plot__()
        this_plt.plot(vals.coords["time"].data, vals.data)
        this_plt.grid()
        this_plt.set_xlabel(r"Time ($\omega_p^{-1}$)", fontsize=12)
        this_plt.set_ylabel(metric, fontsize=12)
        this_plt.set_title(metric + " vs Time", fontsize=14)
        this_fig.savefig(
            os.path.join(series_dir, metric + ".png"),
            bbox_inches="tight",
        )
        plt.close(this_fig)


def __plot_fields__(fields_dir, storage_manager):
    for metric, vals in storage_manager.fields_dataset.items():
        this_fig, this_plt = __get_figure_and_plot__()
        cb = this_plt.contourf(
            vals.coords["space"].data, vals.coords["time"].data, vals.data
        )
        this_plt.set_ylabel(r"Time ($\omega_p^{-1}$)", fontsize=12)
        this_plt.set_xlabel(r"Space ($\lambda_D$)", fontsize=12)
        this_plt.set_title(metric + " vs Time and Space", fontsize=14)
        this_fig.colorbar(cb)
        this_fig.savefig(
            os.path.join(fields_dir, metric + ".png"),
            bbox_inches="tight",
        )
        plt.close(this_fig)


def __plot_distribution__(dist_dir, storage_manager):
    this_fig, this_plt = __get_figure_and_plot__()
    cb = this_plt.contourf(
        storage_manager.fields_dataset.coords["space"].data,
        storage_manager.dist_dataset.coords["velocity"].data,
        np.real((storage_manager.current_f - storage_manager.init_f).T),
    )
    this_plt.set_ylabel(r"Velocity ($v_{th}$)", fontsize=12)
    this_plt.set_xlabel(r"Space ($\lambda_D$)", fontsize=12)
    this_plt.set_title("Most Recent Distribution Function", fontsize=14)
    this_fig.colorbar(cb)
    this_fig.savefig(
        os.path.join(dist_dir, "fxv.png"),
        bbox_inches="tight",
    )
    plt.close(this_fig)


def plot_e_vs_t(plots_dir, t, e, title, log=True):
    this_fig, this_plt = __get_figure_and_plot__()

    if log:
        make_mpl_plot = this_plt.semilogy
    else:
        make_mpl_plot = this_plt.plot

    if isinstance(e, list):
        for ik, ek in enumerate(e):
            make_mpl_plot(t, ek, label="k=" + str(ik + 1))
    elif isinstance(e, np.ndarray):
        make_mpl_plot(t, e)
    else:
        raise NotImplementedError

    this_plt.set_xlabel(r"Time ($\omega_p^{-1}$)", fontsize=12)
    this_plt.set_ylabel(r"$\hat{E}_{k=1}$", fontsize=12)
    this_plt.set_title(title, fontsize=14)
    this_plt.grid()
    this_plt.legend()
    if log:
        this_plt.set_ylim(
            1e-9,
        )
        filename = os.path.join(plots_dir, "log_E_vs_time.png")
    else:
        filename = os.path.join(plots_dir, "E_vs_time.png")

    this_fig.savefig(
        filename,
        bbox_inches="tight",
    )
    plt.close(this_fig)


def plot_e_vs_w(plots_dir, w, e, title):
    this_fig, this_plt = __get_figure_and_plot__()
    this_plt.semilogy(np.fft.fftshift(w), np.fft.fftshift(e), "-x")
    this_plt.set_xlabel(r"Frequency ($\omega_p$)", fontsize=12)
    this_plt.set_ylabel(r"$\hat{\hat{E}}_{k=1}$", fontsize=12)
    this_plt.set_title(title, fontsize=14)
    this_plt.grid()
    this_plt.set_xlim(-5, 5)
    this_plt.set_ylim(0.001 * np.amax(e), 1.5 * np.amax(e))
    this_fig.savefig(
        os.path.join(plots_dir, "E_vs_frequency.png"),
        bbox_inches="tight",
    )
    plt.close(this_fig)


def plot_dw_vs_t(plots_dir, t, ek1_shift, title):
    lower_bound = int(0.25 * t.size)
    upper_bound = int(0.7 * t.size)

    this_fig, this_plt = __get_figure_and_plot__()
    this_plt.plot(t[lower_bound:upper_bound], ek1_shift[lower_bound:upper_bound])
    this_plt.set_xlabel(r"Time ($\omega_p^{-1}$)", fontsize=12)
    this_plt.set_ylabel(r"$\Delta \Phi$", fontsize=12)
    this_plt.set_title(title, fontsize=14)
    this_plt.grid()
    this_fig.savefig(
        os.path.join(plots_dir, "nl_frequency_shift_vs_time.png"),
        bbox_inches="tight",
    )
    plt.close(this_fig)


def plot_f_vs_v(plots_dir, f, v, title, ylabel, filename):
    this_fig, this_plt = __get_figure_and_plot__()

    this_plt.plot(v, f[0], label="initial")
    this_plt.plot(v, f[-1], label="final")
    this_plt.legend()
    this_plt.grid()
    this_plt.set_xlabel(r"$v / v_{th}$", fontsize=12)
    this_plt.set_ylabel(ylabel, fontsize=12)
    this_plt.set_title(title, fontsize=14)
    this_fig.savefig(
        os.path.join(plots_dir, filename),
        bbox_inches="tight",
    )
    plt.close(this_fig)


def plot_f_vs_x_and_v(plots_dir, f, x, v, title, filename):
    this_fig, this_plt = __get_figure_and_plot__()

    cb = this_plt.contourf(x, v, f.T, 32, cmap="gist_ncar")
    this_plt.grid()
    this_plt.set_xlabel(r"$x / \lambda_{D}$", fontsize=12)
    this_plt.set_ylabel(r"$v / v_{th}$", fontsize=12)
    this_plt.set_title(title, fontsize=14)
    this_fig.colorbar(cb)
    this_fig.savefig(
        os.path.join(plots_dir, filename),
        bbox_inches="tight",
    )
    plt.close(this_fig)


def __plot_f_k1(self, fk1_kv_t, time, kv, title):

    kv = fft.fftshift(kv)
    fk1_kv_t = fft.fftshift(fk1_kv_t, axes=-1)

    max_fk1_kv = np.amax(fk1_kv_t)
    largest_wavenumber_index_vs_time = [
        np.amax(np.where(fk1_kv_t[it, : fk1_kv_t.shape[1] // 2] < max_fk1_kv * 1e-2))
        for it in range(fk1_kv_t.shape[0])
    ]
    t1 = int(0.3 * fk1_kv_t.shape[0])
    t2 = int(0.7 * fk1_kv_t.shape[0])

    wavenumber_propagation_speed = abs(kv[largest_wavenumber_index_vs_time[t2]]) - abs(
        kv[largest_wavenumber_index_vs_time[t1]]
    )

    wavenumber_propagation_speed /= time[t2] - time[t1]

    this_fig = plt.figure(figsize=(8, 4))
    this_plt = this_fig.add_subplot(111)
    levels = np.linspace(-8, -2, 19)
    cb = this_plt.contourf(kv, time, np.log10(fk1_kv_t), levels=levels)
    this_fig.colorbar(cb)
    this_plt.plot(
        kv[largest_wavenumber_index_vs_time[t2] : kv.size // 2],
        -kv[largest_wavenumber_index_vs_time[t2] : kv.size // 2]
        / wavenumber_propagation_speed,
        "r",
    )
    this_plt.axhline(y=time[t2], ls="--")
    this_plt.axhline(y=time[t1], ls="--")
    this_plt.axvline(x=kv[largest_wavenumber_index_vs_time[t2]], ls="-.")
    this_plt.axvline(x=kv[largest_wavenumber_index_vs_time[t1]], ls="-.")
    this_plt.set_xlabel(r"$k_v$", fontsize=12)
    this_plt.set_ylabel(r"$1/\omega_p$", fontsize=12)
    this_plt.set_title(
        title
        + ", wavenumber propagation speed = "
        + str(round(wavenumber_propagation_speed, 6)),
        fontsize=14,
    )
    this_fig.savefig(
        os.path.join(self.plots_dir, "fk1.png"),
        bbox_inches="tight",
    )
    plt.close(this_fig)


class BaseDiagnostic:
    def __init__(self):
        self.plots_dir = ""
        self.series_dir = ""
        self.fields_dir = ""
        self.dist_dir = ""
        self.rules_to_store_f = None
        self.stepper = 0
        self.timer = time.time()

    def make_dirs(self, storage_manager):
        timestr = time.strftime("%Y%m%d-%H%M%S")
        self.plots_dir = os.path.join(
            storage_manager.paths["long_term"], "plots", timestr
        )
        self.series_dir = os.path.join(
            storage_manager.paths["long_term"], "plots", timestr, "series"
        )
        self.fields_dir = os.path.join(
            storage_manager.paths["long_term"], "plots", timestr, "fields"
        )
        self.dist_dir = os.path.join(
            storage_manager.paths["long_term"], "plots", timestr, "distribution"
        )
        os.makedirs(self.plots_dir, exist_ok=True)
        os.makedirs(self.series_dir, exist_ok=True)
        os.makedirs(self.fields_dir, exist_ok=True)
        os.makedirs(self.dist_dir, exist_ok=True)

    def make_plots(self, storage_manager):
        __plot_series__(series_dir=self.series_dir, storage_manager=storage_manager)
        __plot_fields__(fields_dir=self.fields_dir, storage_manager=storage_manager)
        __plot_distribution__(dist_dir=self.dist_dir, storage_manager=storage_manager)

    def log_series_metrics(self, storage_manager):
        series_metrics = {}
        for key, val in storage_manager.series_dataset.items():
            series_metrics[key] = val.data[-1]

        mlflow.log_metrics(metrics=series_metrics, step=self.stepper)

    def log_custom_metrics(self, metrics):
        mlflow.log_metrics(metrics=metrics, step=self.stepper)

    def leave(self, storage_manager):
        storage_manager.unload_data_over_all_timesteps()
        # mlflow.log_metrics(
        #     metrics={"time_for_logging": time.time() - self.timer}, step=self.stepper
        # )
        # self.timer = time.time()
        self.stepper += 1

    def load_all_data(self, storage_manager):
        storage_manager.load_data_over_all_timesteps()

    def pre_custom_diagnostics(self, storage_manager):
        self.make_dirs(storage_manager)
        self.load_all_data(storage_manager=storage_manager)
        self.log_series_metrics(storage_manager=storage_manager)

    def post_custom_diagnostics(self, storage_manager):
        self.leave(storage_manager=storage_manager)
