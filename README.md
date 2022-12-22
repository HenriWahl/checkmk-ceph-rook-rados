# checkmk-ceph-rook-rados
Enable Checkmk ceph plugin to monitor Kubernetes based Rook Ceph installation

## The Problem

If a Kubernetes Rook Ceph installation should be monitored via the great
[Checkmk Ceph Plugin](https://github.com/HeinleinSupport/check_mk_extensions/tree/cmk2.1/ceph) the plugin won't work if
installed locally on the host. This happens because it depends on the module
[rados](https://docs.ceph.com/en/latest/rados/api/python/) which works only with a local installation.

## The Solution

Putting the file `rados.py` into the same directory `/usr/lib/check_mk_agent/plugins/58` as the ceph plugin on the host
allows the plugin to [import](https://github.com/HeinleinSupport/check_mk_extensions/blob/cmk2.1/ceph/agents/plugins/ceph#L19)
the module `rados` as before.

This local `rados.py` uses

```shell
kubectl -n rook-ceph exec -it deploy/rook-ceph-tools -- ceph
```

to execute Ceph commands. Thus it can supply Checkmk with the expected Ceph output and the Rook Ceph instance is
monitored.

