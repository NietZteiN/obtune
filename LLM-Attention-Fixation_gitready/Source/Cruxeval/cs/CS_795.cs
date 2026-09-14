using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text) {
        text = System.Threading.Thread.CurrentThread.CurrentCulture.TextInfo.ToTitleCase(text);
        text = text.Replace("Io", "io");
        return text;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("Fu,ux zfujijabji pfu.")).Equals(("Fu,Ux Zfujijabji Pfu.")));
    }

}
