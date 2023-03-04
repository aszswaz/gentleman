pkgname=python-genleman
pkgver=v1.0.0
pkgrel=1
pkgdesc="bilibili instructional video downloader."
arch=(any)
license=('GPL')
makedepends=(python-build python-installer python-wheel)
depends=(python python-requests ffmpeg)
groups=('aszswaz')
build() {
    cd ../
    python -m build --wheel --no-isolation
}
package() {
    cd ../
    python -m installer --destdir="$pkgdir" dist/*.whl
}
