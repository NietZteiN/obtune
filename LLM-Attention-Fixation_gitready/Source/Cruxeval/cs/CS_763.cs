using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string values, string text, string markers) {
        return text.TrimEnd(values.ToCharArray()).TrimEnd(markers.ToCharArray());
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("2Pn"), ("yCxpg2C2Pny2"), ("")).Equals(("yCxpg2C2Pny")));
    }

}
