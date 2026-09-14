using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string item) {
        string modified = item.Replace(". ", " , ").Replace("&#33; ", "! ").Replace(". ", "? ").Replace(". ", ". ");
        return char.ToUpper(modified[0]) + modified.Substring(1);
    }
    public static void Main(string[] args) {
    Debug.Assert(F((".,,,,,. منبت")).Equals((".,,,,, , منبت")));
    }

}
