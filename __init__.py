# -*- coding: utf-8 -*-
"""
/***************************************************************************
 SEC
                                 A QGIS plugin
 Funciones de la SEC en QGIS
                             -------------------
        begin                : 2016-06-30
        copyright            : (C) 2016 by Andrés V. O.
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load SEC class from file SEC.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .sec4qgis import Sec4Qgis
    return Sec4Qgis(iface)
