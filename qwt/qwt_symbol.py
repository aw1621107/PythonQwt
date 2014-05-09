# -*- coding: utf-8 -*-

from qwt.qwt_graphic import QwtGraphic
from qwt.qwt_painter import QwtPainter

from qwt.qt.QtGui import (QPainter, QTransform, QPixmap, QPen, QPolygonF,
                          QPainterPath, QBrush, QPaintEngine)
from qwt.qt.QtCore import QSize, QRect, QPointF, QRectF, QSizeF, Qt, QPoint
from qwt.qt.QtSvg import QSvgRenderer

from math import floor, sqrt, cos, pi, ceil


class QwtTriangle(object):
    
    # enum Type
    Left, Right, Up, Down = range(4)


def qwtPathGraphic(path, pen, brush):
    graphic = QwtGraphic()
    graphic.setRenderHint(QwtGraphic.RenderPensUnscaled)
    painter = QPainter(graphic)
    painter.setPen(pen)
    painter.setBrush(brush)
    painter.drawPath(path)
    painter.end()
    return graphic


def qwtScaleBoundingRect(graphic, size):
    scaledSize = QSize(size)
    if scaledSize.isEmpty():
        scaledSize = graphic.defaultSize()
    sz = graphic.controlPointRect().size()
    sx = 1.
    if sz.width() > 0.:
        sx = scaledSize.width()/sz.width()
    sy = 1.
    if sz.height() > 0.:
        sy = scaledSize.height()/sz.height()
    return graphic.scaledBoundingRect(sx, sy)


def qwtDrawPixmapSymbols(painter, points, numPoints, symbol):
    size = QSize(symbol.size())
    if size.isEmpty():
        size = symbol.pixmap().size()
    transform = QTransform(painter.transform())
    if transform.isScaling():
        r = QRect(0, 0, size.width(), size.height())
        size = transform.mapRect(r).size()
    pm = QPixmap(symbol.pixmap())
    if pm.size() != size:
        pm = pm.scaled(size)
    pinPoint = QPointF(.5*size.width(), .5*size.height())
    if symbol.isPinPointEnabled():
        pinPoint = symbol.pinPoint()
    painter.resetTransform()
    for pos in points:
        pos = QPointF(transform.map(pos))-pinPoint
        QwtPainter.drawPixmap(painter, QRect(pos.toPoint(), pm.size(), pm))
        

def qwtDrawSvgSymbols(painter, points, numPoints, renderer, symbol):
    if renderer is None or not renderer.isValid():
        return
    viewBox = QRectF(renderer.viewBoxF())
    if viewBox.isEmpty():
        return
    sz = QSizeF(symbol.size())
    if not sz.isValid():
        sz = viewBox.size()
    sx = sz.width()/viewBox.width()
    sy = sz.height()/viewBox.height()
    pinPoint = QPointF(viewBox.center())
    if symbol.isPinPointEnabled():
        pinPoint = symbol.pinPoint()
    dx = sx*(pinPoint.x()-viewBox.left())
    dy = sy*(pinPoint.y()-viewBox.top())
    for pos in points:
        x = pos.x()-dx
        y = pos.y()-dy
        renderer.render(painter, QRectF(x, y, sz.width(), sz.height()))


def qwtDrawGraphicSymbols(painter, points, numPoint, graphic, symbol):
    pointRect = QRectF(graphic.controlPointRect())
    if pointRect.isEmpty():
        return
    sx = 1.
    sy = 1.
    sz = QSize(symbol.size())
    if sz.isValid():
        sx = sz.width()/pointRect.width()
        sy = sz.height()/pointRect.height()
    pinPoint = QPointF(pointRect.center())
    if symbol.isPinPointEnabled():
        pinPoint = symbol.pinPoint()
    transform = QTransform(painter.transform())
    for pos in points:
        tr = QTransform(transform)
        tr.translate(pos.x(), pos.y())
        tr.scale(sx, sy)
        tr.translate(-pinPoint.x(), -pinPoint.y())
        painter.setTransform(tr)
        graphic.render(painter)
    painter.setTransform(transform)


def qwtDrawEllipseSymbols(painter, points, numPoints, symbol):
    painter.setBrush(symbol.brush())
    painter.setPen(symbol.pen())
    size = QSize(symbol.size())
    if QwtPainter.roundingAlignment(painter):
        sw = size.width()
        sh = size.height()
        sw2 = size.width()//2
        sh2 = size.height()//2
        for pos in points:
            x = round(pos.x())
            y = round(pos.y())
            r = QRectF(x-sw2, y-sh2, sw, sh)
            QwtPainter.drawEllipse(painter, r)
    else:
        sw = size.width()
        sh = size.height()
        sw2 = .5*size.width()
        sh2 = .5*size.height()
        for pos in points:
            x = pos.x()
            y = pos.y()
            r = QRectF(x-sw2, y-sh2, sw, sh)
            QwtPainter.drawEllipse(painter, r)


def qwtDrawRectSymbols(painter, points, numPoints, symbol):
    size = QSize(symbol.size())
    pen = QPen(symbol.pen())
    pen.setJoinStyle(Qt.MiterJoin)
    painter.setPen(pen)
    painter.setBrush(symbol.brush())
    painter.setRenderHint(QPainter.Antialiasing, False)
    if QwtPainter.roundingAlignment(painter):
        sw = size.width()
        sh = size.height()
        sw2 = size.width()//2
        sh2 = size.height()//2
        for pos in points:
            x = round(pos.x())
            y = round(pos.y())
            r = QRectF(x-sw2, y-sh2, sw, sh)
            QwtPainter.drawRect(painter, r)
    else:
        sw = size.width()
        sh = size.height()
        sw2 = .5*size.width()
        sh2 = .5*size.height()
        for pos in points:
            x = pos.x()
            y = pos.y()
            r = QRectF(x-sw2, y-sh2, sw, sh)
            QwtPainter.drawRect(painter, r)


def qwtDrawDiamondSymbols(painter, points, numPoints, symbol):
    size = QSize(symbol.size())
    pen = QPen(symbol.pen())
    pen.setJoinStyle(Qt.MiterJoin)
    painter.setPen(pen)
    painter.setBrush(symbol.brush())
    if QwtPainter.roundingAlignment(painter):
        for pos in points:
            x = round(pos.x())
            y = round(pos.y())
            x1 = x-size.width()//2
            y1 = y-size.height()//2
            x2 = x1+size.width()
            y2 = y1+size.height()
            polygon = QPolygonF()
            polygon += QPointF(x, y1)
            polygon += QPointF(x1, y)
            polygon += QPointF(x, y2)
            polygon += QPointF(x2, y)
            QwtPainter.drawPolygon(painter, polygon)
    else:
        for pos in points:
            x1 = pos.x()-.5*size.width()
            y1 = pos.y()-.5*size.height()
            x2 = x1+size.width()
            y2 = y1+size.height()
            polygon = QPolygonF()
            polygon += QPointF(pos.x(), y1)
            polygon += QPointF(x1, pos.y())
            polygon += QPointF(pos.x(), y2)
            polygon += QPointF(x2, pos.y())
            QwtPainter.drawPolygon(painter, polygon)


def qwtDrawTriangleSymbols(painter, type, points, numPoint, symbol):
    size = QSize(symbol.size())
    pen = QPen(symbol.pen())
    pen.setJoinStyle(Qt.MiterJoin)
    painter.setPen(pen)
    painter.setBrush(symbol.brush())
    doAlign = QwtPainter.roundingAlignment(painter)
    sw2 = .5*size.width()
    sh2 = .5*size.height()
    if doAlign:
        sw2 = floor(sw2)
        sh2 = floor(sh2)
    for pos in points:
        x = pos.x()
        y = pos.y()
        if doAlign:
            x = round(x)
            y = round(y)
        x1 = x-sw2
        x2 = x1+size.width()
        y1 = y-sh2
        y2 = y1+size.height()
        if type == QwtTriangle.Left:
            triangle = [QPointF(x2, y1), QPointF(x1, y), QPointF(x2, y2)]
        elif type == QwtTriangle.Right:
            triangle = [QPointF(x1, y1), QPointF(x2, y), QPointF(x1, y2)]
        elif type == QwtTriangle.Up:
            triangle = [QPointF(x1, y2), QPointF(x, y1), QPointF(x2, y2)]
        elif type == QwtTriangle.Down:
            triangle = [QPointF(x1, y1), QPointF(x, y2), QPointF(x2, y1)]
        QwtPainter.drawPolygon(painter, QPolygonF(triangle))


def qwtDrawLineSymbols(painter, orientations, points, numPoints, symbol):
    size = QSize(symbol.size())
    off = 0
    pen = QPen(symbol.pen())
    if pen.width() > 1:
        pen.setCapStyle(Qt.FlatCap)
        off = 1
    painter.setPen(pen)
    painter.setRenderHint(QPainter.Antialiasing, False)
    if QwtPainter.roundingAlignment(painter):
        sw = floor(size.width())
        sh = floor(size.height())
        sw2 = size.width()//2
        sh2 = size.height()//2
        for pos in points:
            if orientations & Qt.Horizontal:
                x = round(pos.x())-sw2
                y = round(pos.y())
                QwtPainter.drawLine(painter, x, y, x+sw+off, y)
            if orientations & Qt.Vertical:
                x = round(pos.x())
                y = round(pos.y())-sh2
                QwtPainter.drawLine(painter, x, y, x, y+sh+off)
    else:
        sw = size.width()
        sh = size.height()
        sw2 = .5*size.width()
        sh2 = .5*size.height()
        for pos in points:
            if orientations & Qt.Horizontal:
                x = round(pos.x())-sw2
                y = round(pos.y())
                QwtPainter.drawLine(painter, x, y, x+sw, y)
            if orientations & Qt.Vertical:
                x = round(pos.x())
                y = round(pos.y())-sh2
                QwtPainter.drawLine(painter, x, y, x, y+sh)


def qwtDrawXCrossSymbols(painter, points, numPoints, symbol):
    size = QSize(symbol.size())
    off = 0
    pen = QPen(symbol.pen())
    if pen.width() > 1:
        pen.setCapStyle(Qt.FlatCap)
        off = 1
    painter.setPen(pen)
    if QwtPainter.roundingAlignment(painter):
        sw = floor(size.width())
        sh = floor(size.height())
        sw2 = size.width()//2
        sh2 = size.height()//2
        for pos in points:
            x = round(pos.x())
            y = round(pos.y())
            x1 = x-sw2
            x2 = x1+sw+off
            y1 = y-sh2
            y2 = y1+sh+off
            QwtPainter.drawLine(painter, x1, y1, x2, y2)
            QwtPainter.drawLine(painter, x2, y1, x1, y2)
    else:
        sw = size.width()
        sh = size.height()
        sw2 = .5*size.width()
        sh2 = .5*size.height()
        for pos in points:
            x1 = pos.x()-sw2
            x2 = x1+sw
            y1 = pos.y()-sh2
            y2 = y1+sh
            QwtPainter.drawLine(painter, x1, y1, x2, y2)
            QwtPainter.drawLine(painter, x2, y1, x1, y2)


def qwtDrawStar1Symbols(painter, points, numPoints, symbol):
    size = QSize(symbol.size())
    painter.setPen(symbol.pen())
    sqrt1_2 = sqrt(.5)
    if QwtPainter.roundingAlignment(painter):
        r = QRect(0, 0, size.width(), size.height())
        for pos in points:
            r.moveCenter(pos.toPoint())
            d1 = r.width()/2.*(1.-sqrt1_2)
            QwtPainter.drawLine(painter,
                                  round(r.left()+d1), round(r.top()+d1),
                                  round(r.right()-d1), round(r.bottom()-d1))
            QwtPainter.drawLine(painter,
                                  round(r.left()+d1), round(r.bottom()-d1),
                                  round(r.right()-d1), round(r.top()+d1))
            c = QPoint(r.center())
            QwtPainter.drawLine(painter, c.x(), r.top(), c.x(), r.bottom())
            QwtPainter.drawLine(painter, r.left(), c.y(), r.right(), c.y())
    else:
        r = QRectF(0, 0, size.width(), size.height())
        for pos in points:
            r.moveCenter(pos.toPoint())
            c = QPointF(r.center())
            d1 = r.width()/2.*(1.-sqrt1_2)
            QwtPainter.drawLine(painter, r.left()+d1, r.top()+d1,
                                  r.right()-d1, r.bottom()-d1)
            QwtPainter.drawLine(painter, r.left()+d1, r.bottom()-d1,
                                  r.right()-d1, r.top()+d1)
            QwtPainter.drawLine(painter, c.x(), r.top(), c.x(), r.bottom())
            QwtPainter.drawLine(painter, r.left(), c.y(), r.right(), c.y())


def qwtDrawStar2Symbols(painter, points, numPoints, symbol):
    pen = QPen(symbol.pen())
    if pen.width() > 1:
        pen.setCapStyle(Qt.FlatCap)
    pen.setJoinStyle(Qt.MiterJoin)
    painter.setPen(pen)
    painter.setBrush(symbol.brush())
    cos30 = cos(30*pi/180.)
    dy = .25*symbol.size().height()
    dx = .5*symbol.size().width()*cos30/3.
    doAlign = QwtPainter.roundingAlignment(painter)
    for pos in points:
        if doAlign:
            x = round(pos.x())
            y = round(pos.y())
            x1 = round(x-3*dx)
            y1 = round(y-2*dy)
        else:
            x = pos.x()
            y = pos.y()
            x1 = x-3*dx
            y1 = y-2*dy
        x2 = x1+1*dx
        x3 = x1+2*dx
        x4 = x1+3*dx
        x5 = x1+4*dx
        x6 = x1+5*dx
        x7 = x1+6*dx
        y2 = y1+1*dy
        y3 = y1+2*dy
        y4 = y1+3*dy
        y5 = y1+4*dy
        star = [QPointF(x4, y1), QPointF(x5, y2), QPointF(x7, y2),
                QPointF(x6, y3), QPointF(x7, y4), QPointF(x5, y4),
                QPointF(x4, y5), QPointF(x3, y4), QPointF(x1, y4),
                QPointF(x2, y3), QPointF(x1, y2), QPointF(x3, y2)]
        QwtPainter.drawPolygon(painter, QPolygonF(star))


def qwtDrawHexagonSymbols(painter, points, numPoints, symbol):
    painter.setBrush(symbol.brush())
    painter.setPen(symbol.pen())
    cos30 = cos(30*pi/180.)
    dx = .5*(symbol.size().width()-cos30)
    dy = .25*symbol.size().height()
    doAlign = QwtPainter.roundingAlignment(painter)
    for pos in points:
        if doAlign:
            x = round(pos.x())
            y = round(pos.y())
            x1 = ceil(x-dx)
            y1 = ceil(y-2*dy)
        else:
            x = pos.x()
            y = pos.y()
            x1 = x-dx
            y1 = y-2*dy
        x2 = x1+1*dx
        x3 = x1+2*dx
        y2 = y1+1*dy
        y3 = y1+3*dy
        y4 = y1+4*dy
        hexa = [QPointF(x2, y1), QPointF(x3, y2), QPointF(x3, y3),
                QPointF(x2, y4), QPointF(x1, y3), QPointF(x1, y2)]
        QwtPainter.drawPolygon(painter, QPolygonF(hexa))


class QwtSymbol_PrivateData(object):
    def __init__(self, st, br, pn ,sz):
        self.style = st
        self.size = sz
        self.brush = br
        self.pen = pn
        self.isPinPointEnabled = False
        self.pinPoint = QPointF()

        class Path(object):
            def __init__(self):
                self.path = QPainterPath()
                self.graphic = QwtGraphic()
        self.path = Path()
        
        class Pixmap(object):
            def __init__(self):
                self.pixmap = QPixmap()
        self.pixmap = Pixmap()
        
        class Graphic(object):
            def __init__(self):
                self.graphic = QwtGraphic()
        self.graphic = Graphic()
        
        class SVG(object):
            def __init__(self):
                self.renderer = QSvgRenderer()
        self.svg = SVG()
        
        class PaintCache(object):
            def __init__(self):
                self.policy = 0
                self.pixmap = QPixmap()
        self.cache = PaintCache()


class QwtSymbol(object):
    
    # enum Style
    NoSymbol = -1
    (Ellipse, Rect, Diamond, Triangle, DTriangle, UTriangle, LTriangle,
     RTriangle, Cross, XCross, HLine, VLine, Star1, Star2, Hexagon, Path,
     Pixmap, Graphic, SvgDocument) = range(19)
    UserStyle = 1000
    
    # enum CachePolicy
    NoCache, Cache, AutoCache = range(3)
    
    def __init__(self, *args):
        if len(args) in (0, 1):
            if args:
                style, = args
            else:
                style = QwtSymbol.NoSymbol
            self.__data = QwtSymbol_PrivateData(style, QBrush(Qt.gray),
                                                QPen(Qt.black, 0), QSize())
        elif len(args) == 4:
            style, brush, pen, size = args
            self.__data = QwtSymbol_PrivateData(style, brush, pen, size)
        elif len(args) == 3:
            path, brush, pen = args
            self.__data = QwtSymbol_PrivateData(QwtSymbol.Path, brush, pen,
                                                QSize())
            self.setPath(path)
        else:
            raise TypeError("%s() takes 1, 3, or 4 argument(s) (%s given)"\
                            % (self.__class__.__name__, len(args)))

    def setCachePolicy(self, policy):
        if self.__data.cache.policy != policy:
            self.__data.cache.policy = policy
            self.invalidateCache()
    
    def cachePolicy(self):
        return self.__data.cache.policy
    
    def setPath(self, path):
        self.__data.style = QwtSymbol.Path
        self.__data.path.path = path
        self.__data.path.graphic.reset()
    
    def path(self):
        return self.__data.path.path
    
    def setPixmap(self, pixmap):
        self.__data.style = QwtSymbol.Pixmap
        self.__data.pixmap.pixmap = pixmap
    
    def pixmap(self):
        return self.__data.pixmap.pixmap
    
    def setGraphic(self, graphic):
        self.__data.style = QwtSymbol.Graphic
        self.__data.graphic.graphic = graphic
    
    def graphic(self):
        return self.__data.graphic.graphic
    
    def setSvgDocument(self, svgDocument):
        self.__data.style = QwtSymbol.SvgDocument
        if self.__data.svg.renderer is None:
            self.__data.svg.renderer = QSvgRenderer()
        self.__data.svg.renderer.load(svgDocument)
    
    def setSize(self, *args):
        if len(args) == 2:
            width, height = args
            if width >= 0 and height < 0:
                height = width
            self.setSize(QSize(width, height))
        elif len(args) == 1:
            size, = args
            if size.isValid() and size != self.__data.size:
                self.__data.size = size
                self.invalidateCache()
        else:
            raise TypeError("%s().setSize() takes 1 or 2 argument(s) (%s given)"\
                            % (self.__class__.__name__, len(args)))
    
    def size(self):
        return self.__data.size
    
    def setBrush(self, brush):
        if brush != self.__data.brush:
            self.__data.brush = brush
            self.invalidateCache()
            if self.__data.style == QwtSymbol.Path:
                self.__data.path.graphic.reset()
    
    def brush(self):
        return self.__data.brush
    
    def setPen(self, *args):
        if len(args) == 3:
            color, width, style = args
            self.setPen(QPen(color, width, style))
        elif len(args) == 1:
            pen, = args
            if pen != self.__data.pen:
                self.__data.pen = pen
                self.invalidateCache()
                if self.__data.style == QwtSymbol.Path:
                    self.__data.path.graphic.reset()
        else:
            raise TypeError("%s().setPen() takes 1 or 3 argument(s) (%s given)"\
                            % (self.__class__.__name__, len(args)))

    def pen(self):
        return self.__data.pen
    
    def setColor(self, color):
        if self.__data.style in (QwtSymbol.Ellipse, QwtSymbol.Rect,
                                 QwtSymbol.Diamond, QwtSymbol.Triangle,
                                 QwtSymbol.UTriangle, QwtSymbol.DTriangle,
                                 QwtSymbol.RTriangle, QwtSymbol.LTriangle,
                                 QwtSymbol.Star2, QwtSymbol.Hexagon):
            if self.__data.brush.color() != color:
                self.__data.brush.setColor(color)
                self.invalidateCache()
        elif self.__data.style in (QwtSymbol.Cross, QwtSymbol.XCross,
                                   QwtSymbol.HLine, QwtSymbol.VLine,
                                   QwtSymbol.Star1):
            if self.__data.pen.color() != color:
                self.__data.pen.setColor(color)
                self.invalidateCache()
        else:
            if self.__data.brush.color() != color or\
               self.__data.pen.color() != color:
                self.invalidateCache()
            self.__data.brush.setColor(color)
            self.__data.pen.setColor(color)
    
    def setPinPoint(self, pos, enable):
        if self.__data.pinPoint != pos:
            self.__data.pinPoint = pos
            if self.__data.isPinPointEnabled:
                self.invalidateCache()
        self.setPinPointEnabled(enable)
    
    def pinPoint(self):
        return self.__data.pinPoint
    
    def setPinPointEnabled(self, on):
        if self.__data.isPinPointEnabled != on:
            self.__data.isPinPointEnabled = on
            self.invalidateCache()
    
    def isPinPointEnabled(self):
        return self.__data.isPinPointEnabled
    
    def drawSymbols(self, painter, points, numPoints=None):
        if numPoints is not None and numPoints <= 0:
            return
        useCache = False
        if QwtPainter.roundingAlignment(painter) and\
           not painter.transform().isScaling():
            if self.__data.cache.policy == QwtSymbol.Cache:
                useCache = True
            elif self.__data.cache.policy == QwtSymbol.AutoCache:
                if painter.paintEngine().type() == QPaintEngine.Raster:
                    useCache = True
                else:
                    if self.__data.style in (QwtSymbol.XCross, QwtSymbol.HLine,
                                             QwtSymbol.VLine, QwtSymbol.Cross):
                        pass
                    elif self.__data.style == QwtSymbol.Pixmap:
                        if not self.__data.size.isEmpty() and\
                           self.__data.size != self.__data.pixmap.pixmap.size():
                            useCache = True
                    else:
                        useCache = True
        if useCache:
            br = QRect(self.boundingRect())
            rect = QRect(0, 0, br.width(), br.height())
            if self.__data.cache.pixmap.isNull():
                self.__data.cache.pixmap = QwtPainter.backingStore(None, br.size())
                self.__data.cache.pixmap.fill(Qt.transparent)
                p = QPainter(self.__data.cache.pixmap)
                p.setRenderHints(painter.renderHints())
                p.translate(-br.topLeft())
                pos = QPointF()
                self.renderSymbols(p, pos, 1)
            dx = br.left()
            dy = br.top()
            for point in points:
                left = round(point.x())+dx
                top = round(point.y())+dy
                painter.drawPixmap(left, top, self.__data.cache.pixmap)
        else:
            painter.save()
            self.renderSymbols(painter, points, numPoints)
            painter.restore()
    
    def drawSymbol(self, painter, rect):
        if self.__data.style == QwtSymbol.NoSymbol:
            return
        if self.__data.style == QwtSymbol.Graphic:
            self.__data.graphic.graphic.render(painter, rect,
                                               Qt.KeepAspectRatio)
        elif self.__data.style == QwtSymbol.Path:
            if self.__data.path.graphic.isNull():
                self.__data.path.graphic = qwtPathGraphic(
                    self.__data.path.path, self.__data.pen, self.__data.brush)
            self.__data.path.graphic.render(painter, rect, Qt.KeepAspectRatio)
            return
        elif self.__data.style == QwtSymbol.SvgDocument:
            if self.__data.svg.renderer is not None:
                scaledRect = QRectF()
                sz = QSizeF(self.__data.svg.renderer.viewBoxF().size())
                if not sz.isEmpty():
                    sz.scale(rect.size(), Qt.KeepAspectRatio)
                    scaledRect.setSize(sz)
                    scaledRect.moveCenter(rect.center())
                else:
                    scaledRect = rect
                self.__data.svg.renderer.render(painter, scaledRect)
        else:
            br = QRect(self.boundingRect())
            ratio = min([rect.width()/br.width(), rect.height()/br.height()])
            painter.save()
            painter.translate(rect.center())
            painter.scale(ratio, ratio)
            isPinPointEnabled = self.__data.isPinPointEnabled
            self.__data.isPinPointEnabled = False
            pos = QPointF()
            self.renderSymbols(painter, pos, 1)
            self.__data.isPinPointEnabled = isPinPointEnabled
            painter.restore()
    
    def renderSymbols(self, painter, points, numPoints):
        if self.__data.style == QwtSymbol.Ellipse:
            qwtDrawEllipseSymbols(painter, points, numPoints, self)
        elif self.__data.style == QwtSymbol.Rect:
            qwtDrawRectSymbols(painter, points, numPoints, self)
        elif self.__data.style == QwtSymbol.Diamond:
            qwtDrawDiamondSymbols(painter, points, numPoints, self)
        elif self.__data.style == QwtSymbol.Cross:
            qwtDrawLineSymbols(painter, Qt.Horizontal|Qt.Vertical,
                               points, numPoints, self)
        elif self.__data.style == QwtSymbol.XCross:
            qwtDrawXCrossSymbols(painter, points, numPoints, self)
        elif self.__data.style in (QwtSymbol.Triangle, QwtSymbol.UTriangle):
            qwtDrawTriangleSymbols(painter, QwtTriangle.Up,
                                   points, numPoints, self)
        elif self.__data.style == QwtSymbol.DTriangle:
            qwtDrawTriangleSymbols(painter, QwtTriangle.Down,
                                   points, numPoints, self)
        elif self.__data.style == QwtSymbol.RTriangle:
            qwtDrawTriangleSymbols(painter, QwtTriangle.Right,
                                   points, numPoints, self)
        elif self.__data.style == QwtSymbol.LTriangle:
            qwtDrawTriangleSymbols(painter, QwtTriangle.Left,
                                   points, numPoints, self)
        elif self.__data.style == QwtSymbol.HLine:
            qwtDrawLineSymbols(painter, Qt.Horizontal, points, numPoints, self)
        elif self.__data.style == QwtSymbol.VLine:
            qwtDrawLineSymbols(painter, Qt.Vertical, points, numPoints, self)
        elif self.__data.style == QwtSymbol.Star1:
            qwtDrawStar1Symbols(painter, points, numPoints, self)
        elif self.__data.style == QwtSymbol.Star2:
            qwtDrawStar2Symbols(painter, points, numPoints, self)
        elif self.__data.style == QwtSymbol.Hexagon:
            qwtDrawHexagonSymbols(painter, points, numPoints, self)
        elif self.__data.style == QwtSymbol.Path:
            if self.__data.path.graphic.isNull():
                self.__data.path.graphic = qwtPathGraphic(
                    self.__data.path.path, self.__data.pen, self.__data.brush)
            qwtDrawGraphicSymbols(painter, points, numPoints,
                                  self.__data.path.graphic, self)
        elif self.__data.style == QwtSymbol.Pixmap:
            qwtDrawPixmapSymbols(painter, points, numPoints, self)
        elif self.__data.style == QwtSymbol.Graphic:
            qwtDrawGraphicSymbols(painter, points, numPoints,
                                  self.__data.graphic.graphic, self)
        elif self.__data.style == QwtSymbol.SvgDocument:
            qwtDrawSvgSymbols(painter, points, numPoints,
                              self.__data.svg.renderer, self)

    def boundingRect(self):
        rect = QRectF()
        if self.__data.style in (QwtSymbol.Ellipse, QwtSymbol.Rect,
                                 QwtSymbol.Hexagon):
            pw = 0.
            if self.__data.pen.style() != Qt.NoPen:
                pw = max([self.__data.pen.widthF(), 1.])
            rect.setSize(self.__data.size+QSizeF(pw, pw))
            rect.moveCenter(QPointF(0., 0.))
        elif self.__data.style in (QwtSymbol.XCross, QwtSymbol.Diamond,
                                   QwtSymbol.Triangle, QwtSymbol.UTriangle,
                                   QwtSymbol.DTriangle, QwtSymbol.RTriangle,
                                   QwtSymbol.LTriangle, QwtSymbol.Star1,
                                   QwtSymbol.Star2):
            pw = 0.
            if self.__data.pen.style() != Qt.NoPen:
                pw = max([self.__data.pen.widthF(), 1.])
            rect.setSize(self.__data.size+QSizeF(2*pw, 2*pw))
            rect.moveCenter(QPointF(0., 0.))
        elif self.__data.style == QwtSymbol.Path:
            if self.__data.path.graphic.isNull():
                self.__data.path.graphic = qwtPathGraphic(
                    self.__data.path.path, self.__data.pen, self.__data.brush)
            rect = qwtScaleBoundingRect(self.__data.path.graphic,
                                        self.__data.size)
        elif self.__data.style == QwtSymbol.Pixmap:
            if self.__data.size.isEmpty():
                rect.setSize(self.__data.pixmap.pixmap.size())
            else:
                rect.setSize(self.__data.size)
            rect.moveCenter(QPointF(0., 0.))
        elif self.__data.style == QwtSymbol.Graphic:
            rect = qwtScaleBoundingRect(self.__data.graphic.graphic,
                                        self.__data.size)
        elif self.__data.style == QwtSymbol.SvgDocument:
            if self.__data.svg.renderer is not None:
                rect = self.__data.svg.renderer.viewBoxF()
            if self.__data.size.isValid() and not rect.isEmpty():
                sz = QSizeF(rect.size())
                sx = self.__data.size.width()/sz.width()
                sy = self.__data.size.height()/sz.height()
                transform = QTransform()
                transform.scale(sx, sy)
                rect = transform.mapRect(rect)
        else:
            rect.setSize(self.__data.size)
            rect.moveCenter(QPointF(0., 0.))
        if self.__data.style in (QwtSymbol.Graphic, QwtSymbol.SvgDocument,
                                 QwtSymbol.Path):
            pinPoint = QPointF(0., 0.)
            if self.__data.isPinPointEnabled:
                pinPoint = rect.center()-self.__data.pinPoint
            rect.moveCenter(pinPoint)
        r = QRect()
        r.setLeft(floor(rect.left()))
        r.setTop(floor(rect.top()))
        r.setRight(floor(rect.right()))
        r.setBottom(floor(rect.bottom()))
        if self.__data.style != QwtSymbol.Pixmap:
            r.adjust(-1, -1, 1, 1)
        return r
    
    def invalidateCache(self):
        if not self.__data.cache.pixmap.isNull():
            self.__data.cache.pixmap = QPixmap()
    
    def setStyle(self, style):
        if self.__data.style != style:
            self.__data.style = style
            self.invalidateCache()
    
    def style(self):
        return self.__data.style
