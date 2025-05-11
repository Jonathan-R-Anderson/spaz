<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
  <xsl:template match="/">
    <html>
      <body>
        <h2>RTMP Streams</h2>
        <table border="1">
          <tr bgcolor="#9acd32">
            <th>Application</th><th>Stream</th><th>Client Count</th>
          </tr>
          <xsl:for-each select="rtmp/server/application">
            <tr>
              <td><xsl:value-of select="name"/></td>
              <td><xsl:value-of select="live/stream"/></td>
              <td><xsl:value-of select="live/client"/></td>
            </tr>
          </xsl:for-each>
        </table>
      </body>
    </html>
  </xsl:template>
</xsl:stylesheet>
