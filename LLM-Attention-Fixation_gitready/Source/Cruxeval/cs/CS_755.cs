using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string replace, string text, string hide) {
        while (text.Contains(hide)) {
            replace += "ax";
            text = text.Replace(hide, replace);
        }
        return text;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("###"), ("ph>t#A#BiEcDefW#ON#iiNCU"), (".")).Equals(("ph>t#A#BiEcDefW#ON#iiNCU")));
    }

}
