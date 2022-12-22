# checkmk-ceph-rook-rados
Enable Checkmk ceph plugin to monitor Kubernetes based Rook Ceph installation

## The Problem

If a Kubernetes Rook Ceph installation should be monitored via the great
[Checkmk Ceph Plugin](https://github.com/HeinleinSupport/check_mk_extensions/tree/cmk2.1/ceph) the plugin won't work if
installed locally on the host. This happens because it depends on the module
[rados](https://docs.ceph.com/en/latest/rados/api/python/) which works only with a local installation.

## The Solution

Putting the file [rados.py](https://github.com/HenriWahl/checkmk-ceph-rook-rados/blob/main/rados.py) into the same directory `/usr/lib/check_mk_agent/plugins/58` as the ceph plugin on the host
allows the plugin to [import](https://github.com/HeinleinSupport/check_mk_extensions/blob/cmk2.1/ceph/agents/plugins/ceph#L19)
the module `rados` as before:

```shell
~# ls -l /usr/lib/check_mk_agent/plugins/58
total 12
-rwxr-xr-x 1 root root 4255 Dec 20 15:09 ceph
-rw-r--r-- 1 root root 2784 Dec 21 14:27 rados.py
```

This local `rados.py` uses

```shell
kubectl -n rook-ceph exec -it deploy/rook-ceph-tools -- ceph
```

to execute Ceph commands. Thus it can supply Checkmk with the expected Ceph output and the Rook Ceph instance is
monitored.

## Some Customization

As of now one will need to customize the file `rados.py` to match the real monitor names it is used on.
Rook Ceph names all monitors alphabetically, starting with 'a'. To get the real hostnames in Checkmk some
customization will be required:

- the simplest case might be to change `CEPH_HOSTNAME_TEMPLATE`
- more sophisticated needs can be adjusted in [lines 46-53](https://github.com/HenriWahl/checkmk-ceph-rook-rados/blob/main/rados.py#L46-L53)
