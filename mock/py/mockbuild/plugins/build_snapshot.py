# -*- coding: utf-8 -*-
# vim: noai:ts=4:sw=4:expandtab

import os
import tarfile

from mockbuild.trace_decorator import getLog, traceLog

requires_api_version = "1.1"


class BuildSnapshot(object):
    """Tar rpmbuild/BUILD into resultdir for external SBOM tools."""
    @traceLog()
    def __init__(self, plugins, conf, buildroot):
        self.buildroot = buildroot
        self.state = conf
        plugins.add_hook("postbuild", self._make_snapshot)
        getLog().info("build_snapshot: initialized")

    @traceLog()
    def _make_snapshot(self):
        log = getLog()
        build_path = os.path.join(
            self.buildroot.make_chroot_path(self.buildroot.builddir), "BUILD"
        )
        if not os.path.isdir(build_path):
            log.warning("build_snapshot: BUILD dir not found: %s", build_path)
            return

        name = self.state.get("name", "build-snapshot.tar.gz")
        compress = self.state.get("compress", "gz")
        mode = "w" if compress == "none" else "w:" + compress
        outfile = os.path.join(self.buildroot.resultdir, name)

        log.info("build_snapshot: creating %s", outfile)
        with tarfile.open(outfile, mode) as tar:
            tar.add(build_path, arcname="BUILD")
        log.info("build_snapshot: done")
