# -*- coding: utf-8 -*-
# vim: noai:ts=4:sw=4:expandtab

import os
import shutil

from mockbuild.exception import Error


class IsolationMode:
    SIMPLE = "simple"
    NSPAWN = "nspawn"
    KVM = "kvm"
    QEMU = "qemu"


_BACKENDS = {}


def register_backend(mode, factory):
    _BACKENDS[mode] = factory


def get_backend_factory(mode):
    try:
        return _BACKENDS[mode]
    except KeyError:
        raise Error(f"Unknown isolation mode: {mode}")


def check_requirements(mode):
    if mode == IsolationMode.KVM:
        if not os.path.exists("/dev/kvm"):
            raise Error("Isolation mode 'kvm' requires /dev/kvm")
    elif mode == IsolationMode.QEMU:
        arches = ("x86_64", "i386", "aarch64", "ppc64le", "s390x", "arm", "riscv64")
        if not any(shutil.which(f"qemu-system-{a}") for a in arches):
            raise Error("Isolation mode 'qemu' requires qemu-system-* binary")


class SimpleBackend:
    name = IsolationMode.SIMPLE

    def __init__(self, config=None):
        self.config = config or {}


class NspawnBackend:
    name = IsolationMode.NSPAWN

    def __init__(self, config=None):
        self.config = config or {}


class KvmBackend:
    name = IsolationMode.KVM

    def __init__(self, config=None):
        check_requirements(IsolationMode.KVM)
        self.config = config or {}


class QemuBackend:
    name = IsolationMode.QEMU

    def __init__(self, config=None):
        check_requirements(IsolationMode.QEMU)
        self.config = config or {}


register_backend(IsolationMode.SIMPLE, SimpleBackend)
register_backend(IsolationMode.NSPAWN, NspawnBackend)
register_backend(IsolationMode.KVM, KvmBackend)
register_backend(IsolationMode.QEMU, QemuBackend)


def resolve(mode, config=None):
    factory = get_backend_factory(mode)
    return factory(config=config)
